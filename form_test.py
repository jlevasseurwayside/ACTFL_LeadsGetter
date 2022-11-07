import requests
from .constants import *

values = [
    {
        FIRST_NAME_FIELD_ID: "WOW",
        LAST_NAME_FIELD_ID: "Wong",
        COMPANY_FIELD_ID: "Super Cool Company",
        EMAIL_FIELD_ID: "asdfgh@testing.com",
    },
    {
        FIRST_NAME_FIELD_ID: "Yo",
        LAST_NAME_FIELD_ID: "Wong",
        COMPANY_FIELD_ID: "Super Cool Company",
        EMAIL_FIELD_ID: "asdfghjk@testing.com",
    },
    {
        FIRST_NAME_FIELD_ID: "Yoo",
        LAST_NAME_FIELD_ID: "Wong",
        COMPANY_FIELD_ID: "Super Cool Company",
        EMAIL_FIELD_ID: "asdfghjkl@testing.com",
    },
]

for value in values:
    r = requests.post(PARDOT_FORM_URL, data=value)
    print(r.status_code)
