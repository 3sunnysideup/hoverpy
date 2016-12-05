.. urllib2eg

=========
urllib2eg
=========

Import hoverpy's main class: HoverPy 

::

>>> from hoverpy import HoverPy


Create our HoverPy object in capture mode 

::

>>> with HoverPy(capture=True) as hp:


Import urllib2 for http 

::

>>>     import urllib2


Build our proxy handler for urllib2. This is currently a rather crude method of initialising urllib2, and this code will be incorporated into the main library shortly. 

::

>>>     proxy = urllib2.ProxyHandler({'http': 'localhost:8500'})
>>>     opener = urllib2.build_opener(proxy)
>>>     urllib2.install_opener(opener)


Print the json from our get request. Hoverpy acted as a proxy: it made the request on our behalf, captured it, and returned it to us. 

::

>>>     print(urllib2.urlopen("http://ip.jsontest.com/myip").read())


Switch HoverPy to simulate mode. HoverPy no longer acts as a proxy; all it does from now on is replay the captured data. 

::

>>>     hp.simulate()


Print the json from our get request. This time the data comes from the store. 

::

>>>     print(urllib2.urlopen("http://ip.jsontest.com/myip").read())


