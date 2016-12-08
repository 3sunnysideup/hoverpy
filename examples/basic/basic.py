# This is by far the simplest example on how to get started with HoverPy.
# Please run this example using: <br><br>``$ python examples/basic/basic.py``<br><br>
# You should see your IP address show up twice. Let's walk through the
# code to see what's happening.
from hoverpy import HoverPy
import requests

# Above, we start by importing our most important class `HoverPy`. We also
# bring in ``requests`` for our http traffic.<br><br>
# .. hoverpy: hoverpy.html#module-hoverpy<br><br>

# Now let's create our HoverPy object in capture mode. We do so with a
# `with` statement as this is the pythonic way, although this is not a necessity.
with HoverPy(capture=True) as hoverpy:

    # print the json from our get request. Hoverpy acted as a proxy: it made
    # the request on our behalf, captured it, and returned it to us.
    print(requests.get("http://ip.jsontest.com/myip").json())

    # switch HoverPy to simulate mode. HoverPy no longer acts as a proxy; all
    # it does from now on is replay the captured data.
    hoverpy.simulate()

    # print the json from our get request. This time the data comes from the
    # store.
    print(requests.get("http://ip.jsontest.com/myip").json())


# requests.db<br>
# -----------<br>
# <br>
# You may have noticed this created a ``requests.db`` inside your current
# directory. This is a boltdb database, holding our requests, and their
# responses.
