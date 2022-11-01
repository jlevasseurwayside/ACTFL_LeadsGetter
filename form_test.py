import requests

url = 'http://www2.waysidepublishing.com/l/359661/2018-01-11/52g7py'

first_name = '359661_18396pi_359661_18396'
last_name = '359661_18398pi_359661_18398'
company = '359661_18400pi_359661_18400'
email = '359661_18402pi_359661_18402'
start_30_day_sample_of_flextext_and_explorer = '359661_18404pi_359661_18404'
grades_range = '359661_42913pi_359661_42913'
ec1 = '359661_42917pi_359661_42917_433725'

values = [
    {
        first_name: 'WOW',
        last_name: 'Wong',
        company: 'Super Cool Company',
        email: 'asdfgh@testing.com',
        start_30_day_sample_of_flextext_and_explorer: 'Yes PLEASE TESTING REPLACEMENT TESTING AGAIN YET AGAIN AND AGAIN',
        grades_range: '433713',
        ec1: "433725"
    },
    {
        first_name: 'Yo',
        last_name: 'Wong',
        company: 'Super Cool Company',
        email: 'asdfghjk@testing.com',
        start_30_day_sample_of_flextext_and_explorer: 'Yes PLEASE TESTING REPLACEMENT TESTING AGAIN YET AGAIN AND AGAIN',
        grades_range: '433713',
        ec1: "433725"
    },
    {
        first_name: 'Yoo',
        last_name: 'Wong',
        company: 'Super Cool Company',
        email: 'asdfghjkl@testing.com',
        start_30_day_sample_of_flextext_and_explorer: 'Yes PLEASE TESTING REPLACEMENT TESTING AGAIN YET AGAIN AND AGAIN',
        grades_range: '433713',
        ec1: "433725"
    }
]

for value in values:
    r = requests.post(url, data=value)
    print(r.status_code)
