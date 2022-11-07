import urllib.request
from .constants import *

url = SIGNIN_URL

with urllib.request.urlopen(url) as response:
    print(response.getcode())
