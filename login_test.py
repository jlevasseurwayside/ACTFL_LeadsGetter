import urllib.request
from constants import constants

url = constants.SIGNIN_URL

with urllib.request.urlopen(url) as response:
    print(response.getcode())
