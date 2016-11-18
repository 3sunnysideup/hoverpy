# import hoverpy's main class: HoverPy
from hoverpy import HoverPy

# import requests for http, and time to time our code
import requests
import time

# setup argparse. If we call our app with --capture, it captures the request. Else it plays them back.
# The --limit flag determines how many articles we get from readthedocs.io
from argparse import ArgumentParser
parser = ArgumentParser(description="Perform proxy testing/URL list creation")
parser.add_argument("--capture", help="capture the data", action="store_true")
parser.add_argument("--limit", default=50, help="number of links to capture / simulate")
args = parser.parse_args()

# this function requests articles from readthedocs.io.
def getLinks(hp, limit):
  print("\nGetting links in %s mode!\n" % hp.mode())
  start = time.time()
  sites = requests.get("http://readthedocs.org/api/v1/project/?limit=%d&offset=0&format=json" % limit)
  objects = sites.json()['objects']
  links = ["http://readthedocs.org" + x['resource_uri'] for x in objects]

  for link in links:
      response = requests.get(link)
      print("url: %s, status code: %s" % (link, response.status_code))
  
  print("Time taken: %f" % (time.time() - start))

# construct our HoverPy object in capture mode
hp = HoverPy(capture=args.capture)

# get the links from read the docs.
getLinks(hp, args.limit)
