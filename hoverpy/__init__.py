import time
import os
import logging
import json
import subprocess
from subprocess import Popen, PIPE
import platform
import sys

from . import config

try:
    import requests
except:
    pass

logging.basicConfig(filename='hoverfly.log', level=logging.DEBUG)

hoverfly = config.getHoverFlyBinaryPath()

if not hoverfly:
    hoverfly = config.downloadHoverFly()


def session():
    session = requests.Session()
    session.trust_env = False
    return session


class HoverPy:

    def __init__(self, host="localhost", capture=False,
                 proxyPort=8500, adminPort=8888, inMemory=False,
                 modify=False, middleware="",
                 dbpath="requests.db", simulation=""):
        self._proxyPort = proxyPort
        self._adminPort = adminPort
        self._host = host
        self._inMemory = inMemory
        self._modify = modify
        self._middleware = middleware
        self._flags = []
        self._capture = capture
        self._dbpath = dbpath
        self._simulation = simulation

        self.enableProxy()
        self.start()

    def __del__(self):
        if self._process:
            self.stop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._process:
            self.stop()

    def __enter__(self):
        return self

    def wipe(self):
        """
        Wipe the bolt database.

        Calling this after HoverPy has been instantiated is
        potentially dangerous. This function is mostly used
        internally for unit tests.
        """
        try:
            if os.isfile(self._dbpath):
                os.remove(self._dbpath)
        except OSError:
            pass

    def host(self):
        """
        Returns the URL to the admin interface / APIs.
        """
        return "http://%s:%i" % (self._host, self._adminPort)

    def v1(self):
        """
        Return the URL to the v1 API
        """
        return self.host()+"/api"

    def v2(self):
        """
        Return the URL to the v2 API
        """
        return self.host()+"/api/v2"

    def enableProxy(self):
        """
        Set the required environment variables to enable the use of hoverfly as a proxy.
        """
        logging.debug("enabling proxy")
        os.environ[
            "HTTP_PROXY"] = "http://%s:%i" % (self._host, self._proxyPort)
        os.environ[
            "HTTPS_PROXY"] = "https://%s:%i" % (self._host, self._proxyPort)
        os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            "cert.pem")

    def disableProxy(self):
        """
        Clear the environment variables required to enable the use of hoverfly as a proxy.
        """
        del os.environ['HTTP_PROXY']
        del os.environ['HTTPS_PROXY']
        del os.environ['REQUESTS_CA_BUNDLE']

    def start(self):
        """
        Start the hoverfly process.

        This function waits until it can make contact
        with the hoverfly API before returning.
        """
        logging.debug("starting %i" % id(self))
        FNULL = open(os.devnull, 'w')
        flags = self.flags()
        self._process = Popen(
            [hoverfly] +
            flags,
            stdout=FNULL,
            stderr=subprocess.STDOUT)
        start = time.time()
        while time.time() - start < 1:
            try:
                url = "http://%s:%i/api/health" % (self._host, self._adminPort)
                r = session().get(url)
                j = r.json()
                up = "message" in j and "healthy" in j["message"]
                if up:
                    logging.debug("has pid %i" % self._process.pid)
                    return self._process
                else:
                    time.sleep(1/100.0)
            except:
                # wait 10 ms before trying again
                time.sleep(1/100.0)
                pass

        logging.error("Could not start hoverfly!")
        raise ValueError("Could not start hoverfly!")

    def stop(self):
        """
        Stop the hoverfly process.
        """
        if logging:
            logging.debug("stopping")
        self._process.kill()
        self._process = None
        self.disableProxy()

    def capture(self):
        """
        Switches hoverfly to capture mode.
        """
        return self.mode("capture")

    def simulate(self):
        """
        Switches hoverfly to simulate mode.

        Please note simulate is the default mode.
        """
        return self.mode("simulate")

    def config(self):
        """
        Returns the hoverfly configuration json.
        """
        return session().get(self.v2()+"/hoverfly").json()

    def simulation(self, data=None):
        """
        Gets / Sets the simulation data.

        If no data is passed in, then this method acts as a getter.
        if data is passed in, then this method acts as a setter.

        Keyword arguments:
        data -- the simulation data you wish to set (default None)
        """
        if data:
            return session().put(self.v2()+"/simulation", data=data)
        else:
            return session().get(self.v2()+"/simulation").json()

    def destination(self, name=""):
        """
        Gets / Sets the destination data.
        TBD.
        """
        if name:
            return session().put(
                self.v2()+"/hoverfly/destination",
                data={"destination": name}).json()
        else:
            return session().get(self.v2()+"/hoverfly/destination").json()

    def middleware(self):
        """
        Gets the middleware data.
        TBD.
        """
        return session().get(self.v2()+"/hoverfly/middleware").json()

    def mode(self, mode=None):
        """
        Gets / Sets the mode.

        If no mode is provided, then this method acts as a getter.

        Keyword arguments:
        mode -- this should either be 'capture' or 'simulate' (default None)
        """
        if mode:
            logging.debug("SWITCHING TO %s" % mode)
            url = self.v2()+"/hoverfly/mode"
            logging.debug(url)
            return session().put(
                url, data=json.dumps({"mode": mode})).json()["mode"]
        else:
            return session().get(self.v2()+"/hoverfly/mode").json()["mode"]

    def usage(self):
        """
        Gets the usage data. TBD.
        """
        return session().get(self.v2()+"/hoverfly/usage").json()

    def metadata(self, delete=False):
        """
        Gets the metadata. TBD.
        """
        if delete:
            return session().delete(self.v1()+"/metadata").json()
        else:
            return session().get(self.v1()+"/metadata").json()

    def records(self, data=None):
        """
        Gets / Sets records. TBD.
        """
        if data:
            return session().post(self.v1()+"/records", data=data).json()
        else:
            return session().get(self.v1()+"/records").json()

    def delays(self, delays=[]):
        """
        Gets / Sets the delays. TBD.
        """
        if delays:
            return session().put(
                self.v1()+"/delays", data=json.dumps(delays)).json()
        else:
            return session().get(self.v1()+"/delays").json()

    def addDelay(self, urlPattern="", delay=0, httpMethod=None):
        """
        Adds delays. TBD.
        """
        delay = {"urlPattern": urlPattern, "delay": delay}
        if httpMethod:
            delay["httpMethod"] = httpMethod
        return self.delays(delays={"data": [delay]})

    def flags(self):
        """
        Internal method. Turns arguments into flags.
        """
        flags = []
        if self._dbpath:
            flags += ["-db-path", self._dbpath]
        if self._capture:
            flags.append("-capture")
        if self._inMemory:
            flags += ["-db", "memory"]
        if self._simulation:
            flags += ["-import", self._simulation]
        if self._modify:
            assert(self._middleware)
            flags += ["-modify", "-middleware", self._middleware]
        logging.debug("flags:" + str(flags))
        return flags


def capture(func):
    def func_wrapper():
        with HoverPy(capture=True):
            func()
    return func_wrapper


def simulate(func):
    def func_wrapper():
        with HoverPy(capture=False):
            func()
    return func_wrapper


def wipe():
    try:
        os.remove("./requests.db")
    except OSError:
        pass


def quick_test():
    hp = HoverPy()
    hp.capture()
    requests.get("http://ip.jsontest.com/ip")
    if "data" in hp.delays().keys():
        print("HOVERPY AND HOVERFLY QUICK TEST SUCCESS!!")

import unittest


class TestCase(unittest.TestCase):

    hp = None

    def setUp(self):
        enabled = os.environ.get(
            "HOVERPY_ENABLED",
            "true").lower() in [
            "true",
            "1",
            "on"]
        if enabled:
            capture = os.environ.get(
                "HOVERPY_CAPTURE",
                "").lower() in [
                "true",
                "1",
                "on"]
            self.hp = HoverPy(capture=capture)

    def tearDown(self):
        if self.hp:
            self.hp.disableProxy()

if __name__ == "__main__":
    quick_test()
