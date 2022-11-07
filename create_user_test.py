import requests
from .constants import *

data = {
    "key": LS_POST_KEY,
    "campaign": "email",
    "textbook": ["9123315"],
    "email": "mwong@waysidepublishing.com",
    "firstname": "Michael",
    "lastname": "Wong",
    "school": "Cool School",
    "city": "Cool City",
    "state": "Cool State",
    "zipCode": "04103",
}

r = requests.post(LS_POST_URL, data=data)
print(r.text)
