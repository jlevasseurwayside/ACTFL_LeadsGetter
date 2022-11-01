import urllib.request
import datetime
import requests
import os
import os.path
import csv
import json
import sys

# Global varibles
new_fn = 'new_data.csv'
old_fn = 'archive.csv'
delta_fn = 'delta.csv'
lock_fn = 'lock.txt'


def get_conf_data():
    url = 'https://www.xpressleadpro.com/portal/public/signin/ligani@waysidepublishing.com/2182520/qualifiers'

    s = requests.Session()

    s.get(url)

    download_url = "https://www.xpressleadpro.com/portal/public/downloadbyexid/2182520/csv"

    with open(new_fn, 'wb') as out_file:
        data = s.get(download_url)
        out_file.write(data.content)


def get_just_new_data_from():
    # If "archive.csv" doesn't exist, that means this is the first set of data ever downloaded
    if os.path.isfile(old_fn) is not True: 
        return new_fn

    else:
        with open(delta_fn, 'a') as delta_file, open(old_fn, 'r') as old_file, open(new_fn, 'r') as new_file:
            old_file_data = csv.DictReader(old_file)
            new_file_data = csv.DictReader(new_file)

            headers = new_file_data.fieldnames

            writer = csv.DictWriter(delta_file, fieldnames=headers)
            writer.writeheader()

            for line in new_file_data:
                if line not in old_file_data:
                    writer.writerow(line)

        return delta_fn


# this method maps Xpress Lead answer's form value to the form name
def map_from_to(v, n):
    all_val = v.split('|')
    ret_val = {}

    for v in all_val:
        curr_tag_name = n.get(v)
        if curr_tag_name is not None:
            if curr_tag_name is not '':
                ret_val[curr_tag_name] = curr_tag_name.split("_")[-1]

    return ret_val


def handle_headers(header, value):
    if header == "Level":
        level_values = {
            "High School": "426379",
            "Middle/Jr. High": "426381",
            "Elementary": "426383",
            "Elementary,Middle/Jr. High,High School": "426385",
            'Middle/Jr. High,High School': '426387',
            'Community College': '426389',
            'Adult Ed': '426391'
        }
        return level_values.get(value, '')

    if header == "Languages":
        language_values = {
            'Spanish': '359661_41981pi_359661_41981_426009',
            'French': '359661_41981pi_359661_41981_426011',
            'German': '359661_41981pi_359661_41981_426013',
            'Italian': '359661_41981pi_359661_41981_426015',
            'Latin': '359661_41981pi_359661_41981_426017',
            'Portuguese': '359661_41981pi_359661_41981_426019',
            'Mandarin': '359661_41981pi_359661_41981_426021',
            'Japanese': '359661_41981pi_359661_41981_426023',
            'Hindi': '359661_41981pi_359661_41981_426025',
            'Arabic': '359661_41981pi_359661_41981_426027',
            'Russian': '359661_41981pi_359661_41981_426029',
        }

        return map_from_to(value, language_values)

    if header == 'Email 30 day access to these programs':
        digital_values = {
            'EntreCulturas 1 - Spanish': '359661_41915pi_359661_41915_425935',
            'EntreCulturas 1a - Spanish': '359661_42103pi_359661_42103_426413',
            'EntreCulturas 1b - Spanish': '359661_42105pi_359661_42105_426415',
            'EntreCulturas 2 - Spanish': '359661_41917pi_359661_41917_425937',
            'EntreCulturas 3 - Spanish': '359661_41919pi_359661_41919_425939',
            'Tejidos': '359661_41921pi_359661_41921_425941',
            'Triangulo Aprobado': '359661_41923pi_359661_41923_425943',
            'Triangulo APreciado': '359661_42107pi_359661_42107_426417',
            'Azulejo': '359661_41925pi_359661_41925_425945',
            'APprenons': '359661_41927pi_359661_41927_425947',
            'Neue Blickwinkel': '359661_41929pi_359661_41929_425949',
            'Chiarissimo Uno': '359661_41931pi_359661_41931_425951',
            'Chiarissimo Due': '359661_41933pi_359661_41933_425953',
            'Scandite Muros': '359661_41935pi_359661_41935_425955',
            'EntreCultures 1 - Unit 1 - French': '359661_42115pi_359661_42115_426425'

        }

        return map_from_to(value, digital_values)

    if header == "Wayside is giving you these print resources now":
        print_values = {
            'EntreCultures Sampler': '359661_42115pi_359661_42115_426425',
            'EntreCulturas 1a': '359661_42117pi_359661_42117_426427',
            'EntreCulturas 1b': '359661_42119pi_359661_42119_426429',
            'EntreCulturas 1': '359661_41937pi_359661_41937_425957',
            'EntreCulturas 2': '359661_41939pi_359661_41939_425959',
            'EntreCulturas 3': '359661_41941pi_359661_41941_425961',
            'Tejidos': '359661_41943pi_359661_41943_425963',
            'Triangulo Aprobado': '359661_41945pi_359661_41945_425965',
            'Triangulo APreciado': '359661_42121pi_359661_42121_426431',
            'Azulejo': '359661_41947pi_359661_41947_425967',
            'APprenons': '359661_41949pi_359661_41949_425969',
            'Neue Blickwinkel': '359661_41951pi_359661_41951_425971',
            'Chiarissimo Uno': '359661_41953pi_359661_41953_425973',
            'Chiarissimo Due': '359661_41955pi_359661_41955_425975',
            'Scandite Muros': '359661_41957pi_359661_41957_425977',
        }
        return map_from_to(value, print_values)

    if header == "Digital tools in your classroom":
        digital_tools_values = {
            '1 to 1': '359661_41983pi_359661_41983_426031',
            '1 to 2 or more': '359661_41983pi_359661_41983_426033',
            'Technology Cart': '359661_41983pi_359661_41983_426035',
            'Language Lab': '359661_41983pi_359661_41983_426401'
        }

        return map_from_to(value, digital_tools_values)

    if header == "The next adoption-related deadline will be":
        deadline_values = {
            'Before 2019': '359661_41987pi_359661_41987_426393',
            'Spring 2019': '359661_41987pi_359661_41987_426395',
            'Spring 2020': '359661_41987pi_359661_41987_426397',
            'Fall 2019': '359661_41987pi_359661_41987_426399'
        }

        return map_from_to(value, deadline_values)

    if header == 'Wayside should stay in touch about':
        in_touch_values = {
            'Wayside newsletter subscription': '359661_41959pi_359661_41959_426437',
            'EntreCultures 123 - Levels 1 and 2 coming 2019': '359661_41963pi_359661_41963_425983',
            'Updates on EntreCulturas 4 - Spanish': '359661_42127pi_359661_42127_426439',
            'Updates on German 1, 2, 3': '359661_41965pi_359661_41965_425985',
            'Learning Site Updates': '359661_42129pi_359661_42129_426441',
        }

        return map_from_to(value, in_touch_values)

    if header == 'Post-ACTFL shipment requested':
        create_values = {
            'EntreCulturas 1a': '359661_42135pi_359661_42135_426447',
            'EntreCulturas 1b': '359661_42137pi_359661_42137_426449',
            'EntreCulturas 1': '359661_42139pi_359661_42139_426451',
            'EntreCulturas 2': '359661_42141pi_359661_42141_426453',
            'EntreCulturas 3': '359661_42143pi_359661_42143_426455',
            'Tejidos': '359661_42145pi_359661_42145_426457',
            'Triangulo Aprobado': '359661_42147pi_359661_42147_426459',
            'Triangulo APreciado': '359661_42149pi_359661_42149_426461',
            'Azulejo': '359661_44005pi_359661_44005_444589',
            'APprenons': '359661_42153pi_359661_42153_426465',
            'Neue Blickwinkel': '359661_42155pi_359661_42155_426467',
            'Chiarissimo Uno': '359661_42157pi_359661_42157_426469',
            'Chiarissimo Due': '359661_42159pi_359661_42159_426471',
            'Scandite Muros': '359661_42161pi_359661_42161_426473',
            'EntreCultures 1 print sampler of unit 1': '359661_44474pi_359661_44474_448870'
        }

        return map_from_to(value, create_values)

    if header == 'If you had your wish, Wayside would create':
        sales_values = {
            'Chiarissimo Tre': '359661_41967pi_359661_41967_425987',
            'Elementary French': '359661_41969pi_359661_41969_425989',
            'Elementary German': '359661_41971pi_359661_41971_425991',
            'Elementary Spanish': '359661_41975pi_359661_41975_425995',
            'Elementary Mandarin': '359661_42133pi_359661_42133_426445',
            'Mandarin 1, 2, 3': '359661_41977pi_359661_41977_425997',
        }

        return map_from_to(value, sales_values)

    if header == 'Lead Rating':
        rating_values = {
            '1': '359661_41993pi_359661_41993_426403',
            '2': '359661_41993pi_359661_41993_426405',
            '3': '359661_41993pi_359661_41993_426407',
            '4': '359661_41993pi_359661_41993_426409',
            '5': '359661_41993pi_359661_41993_426411'
        }
        return map_from_to(value, rating_values)


def push_data_to(fn, url_pardot):
    with open(fn, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        tag_names = {
            'First Name': '359661_41897pi_359661_41897',
            'Last Name': '359661_41899pi_359661_41899',
            'Company': '359661_41903pi_359661_41903',
            'Street': '359661_41905pi_359661_41905',
            'Street (line 2)': '359661_41907pi_359661_41907',
            'City': '359661_41909pi_359661_41909',
            'State/Province': '359661_41911pi_359661_41911',
            'Zip Code': '359661_41913pi_359661_41913',
            'Country': '359661_42097pi_359661_42097',
            'Phone': '359661_42099pi_359661_42099',
            'Email': '359661_41901pi_359661_41901',

            'Assignment': '359661_41979pi_359661_41979',
            'Level': '359661_42101pi_359661_42101',

            'Languages': '',

            'Name of Waysider completing this form': '359661_42703pi_359661_42703',

            'Email 30 day access to these programs': '',

            'Wayside is giving you these print resources now': '',

            'The next adoption-related deadline will be': '',

            'Digital tools in your classroom': '',

            'Wayside should stay in touch about': '',

            'If you had your wish, Wayside would create': '',

            'Post-ACTFL shipment requested': '',

            'OPTIONAL Non Sales Follow Up': '359661_42705pi_359661_42705',

            'Notes': '359661_41991pi_359661_41991',

            'Lead Rating': '',
        }

        all_data = []

        for row in reader:
            pardot_data = {}
            for header in headers:
                tag_name = tag_names.get(header)
                if tag_name is not None:
                    value = row[header]
                    if header in ["Level",
                                  "Languages",
                                  "Email 30 day access to these programs",
                                  "Wayside is giving you these print resources now",
                                  "The next adoption-related deadline will be",
                                  "Digital tools in your classroom",
                                  "Wayside should stay in touch about",
                                  "If you had your wish, Wayside would create",
                                  "Lead Rating"]:
                        return_value = handle_headers(header, value)
                        if isinstance(return_value, str):
                            pardot_data[tag_name] = return_value
                        else:
                            pardot_data.update(return_value)
                    else:
                        pardot_data[tag_name] = value
            all_data.append(pardot_data)

        # Enter POST request here
        curr_data = 1
        log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Filling out Pardot form... \n')
        for data in all_data:
            log('%s/%s users\n' % (curr_data, len(all_data)))
            r = requests.post(url_pardot, data=data)
            log("Successfully finished.\n")
            curr_data += 1


def push_data_to_ls(fn, url_ls):
    with open(fn, 'r') as csvfile:
        all_data = []
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames

        for row in reader:
            data = {
                'key': 'EOQ89SMVP3K',
                'campaign': 'email',
                'textbook': [],
                'email': '',
                'firstname': '',
                'lastname': '',
                'school': '',
                'city': '',
                'state': '',
                'zipCode': ''
            }

            for header in headers:
                curr_val = row[header]

                if header == 'Email 30 day access to these programs':
                    all_textbooks = curr_val.split("|")
                    textbook_ids = {
                        'EntreCulturas 1a - Spanish': '9122772',
                        'EntreCulturas 1b - Spanish': '9123315',
                        'EntreCulturas 1 - Spanish': '13463',
                        'EntreCulturas 2 - Spanish': '13507',
                        'EntreCulturas 3 - Spanish': '13518',
                        'Tejidos': '1955',
                        'Triangulo Aprobado': '3551',
                        'Triangulo APreciado': '6250713',
                        'Azulejo': '3',
                        'APprenons': '11138',
                        'Neue Blickwinkel': '12741',
                        'Chiarissimo Uno': '6698',
                        'Chiarissimo Due': '12271',
                        'Scandite Muros': '13435',
                        'EntreCultures 1 - Unit 1 - French': '4627944'
                    }

                    for t in all_textbooks:
                        curr_id = textbook_ids.get(t)
                        if curr_id is not None and curr_id is not '':
                            data['textbook'].append(curr_id)

                if header == 'Email':
                    data['email'] = curr_val

                if header == 'First Name':
                    data['firstname'] = curr_val

                if header == 'Last Name':
                    data['lastname'] = curr_val

                if header == 'Company':
                    data['school'] = curr_val

                if header == 'City':
                    data['city'] = curr_val

                if header == 'State/Province':
                    data['state'] = curr_val

                if header == 'Zip Code':
                    data['zipCode'] = curr_val

            all_data.append(data)

    curr_d = 1
    log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Adding samples for users...\n')
    for d in all_data:
        log("%s/%s users\n" % (curr_d, len(all_data)))
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(url_ls, data=json.dumps(d), headers=headers)
        log("Successfully finished.\n")
        print(r.text)
        curr_d += 1


def log(text):
    append_log = open("log.txt", "a+")
    append_log.write(text)
    append_log.close()


def cron_log(text):
    with open("cronlog.txt", "a+") as c_log:
        if text:
            c_log.write(text)
        else:
            c_log.write("Cron ran at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")


def cleanup(errno):
    if os.path.isfile(old_fn):
        os.remove(old_fn)

    if os.path.isfile(delta_fn):
        os.remove(delta_fn)

    if errno is 0:
        os.rename(new_fn, old_fn)

    os.remove(lock_fn)


def main():
    cron_log(None)

    try:
        if os.path.isfile(lock_fn) is not True:
            print('Lock file doesn\'t exist, process isn\'t currently running')
            open(lock_fn, 'w+')
            # Getting fresh data
            get_conf_data()

            # Parsing through new data to check for duplicates between
            # "new_data.csv" and "archive.csv" if "archive.csv" exists
            # Returns file name to process
            parsed_data_fn = get_just_new_data_from()

            # Push data to Pardot
            push_data_to(parsed_data_fn, 'http://www2.waysidepublishing.com/l/359661/2018-10-22/dn4z2b')

            # Push data to the LS
            push_data_to_ls(parsed_data_fn, 'https://learningsite.waysidepublishing.com/api/user/')

            # Deleting "archive.csv" and "delta.csv" if necessary, renames "new_data.csv" to "archive.csv"
            cleanup(0)
        else:
            cron_log('Lock file exists, process currently running')
            sys.exit(0)

    except Exception as error:
        cron_log(error)
        cleanup(1)
        sys.exit(1)


main()
