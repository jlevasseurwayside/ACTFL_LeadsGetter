import requests
from constants import constants

values = [
    {
        constants.FIRST_NAME_FIELD_ID: "WOW",
        constants.LAST_NAME_FIELD_ID: "Wong",
        constants.OMPANY_FIELD_ID: "Super Cool Company",
        constants.EMAIL_FIELD_ID: "asdfgh@testing.com",
    },
    {
        constants.FIRST_NAME_FIELD_ID: "Yo",
        constants.LAST_NAME_FIELD_ID: "Wong",
        constants.COMPANY_FIELD_ID: "Super Cool Company",
        constants.EMAIL_FIELD_ID: "asdfghjk@testing.com",
    },
    {
        constants.FIRST_NAME_FIELD_ID: "Yoo",
        constants.LAST_NAME_FIELD_ID: "Wong",
        constants.COMPANY_FIELD_ID: "Super Cool Company",
        constants.EMAIL_FIELD_ID: "asdfghjkl@testing.com",
    },
]

for value in values:
    r = requests.post(constants.PARDOT_FORM_URL, data=value)
    print(r.status_code)
