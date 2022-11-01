import requests


data = {
    'key': "EOQ89SMVP3K",
    'campaign': "email",
    'textbook': ['9123315'],
    'email': "mwong@waysidepublishing.com",
    'firstname': "Michael",
    'lastname': "Wong",
    'school': "Cool School",
    'city': "Cool City",
    'state': "Cool State",
    'zipCode': "04103"
}

r = requests.post("https://learningsite.waysidepublishing.com/api/user/", data=data)
print(r.text)
