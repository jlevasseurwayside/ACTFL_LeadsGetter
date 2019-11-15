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
dummy_fn = 'dummydata.csv'


def get_conf_data():

    # SC is the event code in the Xpress Lead data
    sc = 'ACTF1119'

    # EXID is the exhibitor ID
    exid = '1977893'

    # Email for the account (AKA Michelle)
    em = 'marketing@waysidepublishing.com'

    term_id = 'D356DF7FA99849B'
    
    url = 'https://www.xpressleadpro.com/portal/public/signin/marketing@waysidepublishing.com/1977893/qualifiers'

    s = requests.Session()

    s.get(url)

    download_url = "https://www.xpressleadpro.com/portal/public/downloadbyexid/1977893/csv"

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
    if header == "Languages":
        language_values = {
            'Spanish': '359661_69529pi_359661_69529_631397',
            'French': '359661_69529pi_359661_69529_631399',
            'German': '359661_69529pi_359661_69529_631401',
            'Italian': '359661_69529pi_359661_69529_631403',
            'Latin': '359661_69529pi_359661_69529_631405',
            'Portuguese': '359661_69529pi_359661_69529_631407',
            'Mandarin': '359661_69529pi_359661_69529_631409',
            'Japanese': '359661_69529pi_359661_69529_631411',
            'Hindi': '359661_69529pi_359661_69529_631413',
            'Arabic': '359661_69529pi_359661_69529_631415',
            'Russian': '359661_69529pi_359661_69529_631417',
        }

        return map_from_to(value, language_values)

    if header == 'Email 30 day access to these programs':
        digital_values = {
            'EntreCulturas 1 Spanish': '359661_69471pi_359661_69471_631259',
            'EntreCulturas 1A Spanish': '359661_69473pi_359661_69473_631261',
            'EntreCulturas 1B Spanish': '359661_69475pi_359661_69475_631263',
            'EntreCulturas 2 Spanish': '359661_69477pi_359661_69477_631265',
            'EntreCulturas 3 Spanish': '359661_69479pi_359661_69479_631267',
            'EntreCulturas 4 Unit 1 Spanish': '359661_69481pi_359661_69481_631269',
            'Tejidos': '359661_69483pi_359661_69483_631271',
            'Triangulo APreciado': '359661_69485pi_359661_69485_631273',
            'Azulejo': '359661_69487pi_359661_69487_631275',
            'APprenons': '359661_69499pi_359661_69499_631287',
            'Neue Blickwinkel German': '359661_69501pi_359661_69501_631289',
            'Chiarissimo Uno Italian': '359661_69503pi_359661_69503_631291',
            'Chiarissimo Due Italian': '359661_69505pi_359661_69505_631293',
            'Scandite Muros Latin': '359661_69507pi_359661_69507_631295',
            'EntreCultures 1A French': '359661_69489pi_359661_69489_631277',
            'EntreCultures 1B French': '359661_69491pi_359661_69491_631279',
            'EntreCultures 1 French': '359661_69493pi_359661_69493_631281',
            'EntreCultures 2 French': '359661_69495pi_359661_69495_631283',
            'EntreCultures 3 Unit 1 French': '359661_69497pi_359661_69497_631285' 

        }

        return map_from_to(value, digital_values)

    if header == "Wayside is giving you these print resources now":
        print_values = {
            'EntreCulturas 4 Print Sample Unit': '359661_69509pi_359661_69509_631297',
            'EntreCultures 3 Print Sample Unit': '359661_69511pi_359661_69511_631299',
        }

        return map_from_to(value, print_values)

    if header == "The next adoption related deadline will be":
        deadline_values = {
            'Before September 2020': '359661_69535pi_359661_69535_632741',
            'After September 2020': '359661_69535pi_359661_69535_632743',
        }

        return map_from_to(value, deadline_values)

    if header == 'Wayside should stay in touch about':
        in_touch_values = {
            'German 1, 2, 3': '359661_69515pi_359661_69515_631303',
            'EntreCulturas 4': '359661_69679pi_359661_69679_632745',
            'Entrecultures 3': '359661_69513pi_359661_69513_631301'
        }

        return map_from_to(value, in_touch_values)

    if header == 'Lead Rating':
        rating_values = {
            '1': '359661_69543pi_359661_69543_631391',
            '2': '359661_69543pi_359661_69543_631393',
            '3': '359661_69543pi_359661_69543_631393',
            '4': '359661_69543pi_359661_69543_631395',
            '5': '359661_69543pi_359661_69543_631395'
        }
        return map_from_to(value, rating_values)


def push_data_to(fn, url_pardot):
    with open(fn, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        #update left hand values to match new ACTFL form
        tag_names = {
            'First Name': '359661_69455pi_359661_69455',
            'Last Name': '359661_69457pi_359661_69457',
            'Company': '359661_69463pi_359661_69463',
            'Street': '359661_69547pi_359661_69547',
            'Street (line 2)': '359661_69549pi_359661_69549',
            'City': '359661_69465pi_359661_69465',
            'State/Province': '359661_69467pi_359661_69467',
            'Zip Code': '359661_69469pi_359661_69469',
            'Country': '359661_69551pi_359661_69551',
            'Phone': '359661_69553pi_359661_69553',
            'Email': '359661_69459pi_359661_69459',

            'Assignment': '359661_69555pi_359661_69555',
            'Level': '359661_69557pi_359661_69557',

            'Languages': '',

            'Name of Waysider completing the form': '359661_69677pi_359661_69677',

            'Email 30 day access to these programs': '',

            'The next adoption related deadline will be': '',

            'What Learning Management System LMS do you use': '359661_69533pi_359661_69533',

            'Wayside should stay in touch about': '',

            'Wayside is giving you these print resources now': '',

            'OPTIONAL Non sales follow up': '359661_69681pi_359661_69681',

            'Notes': '359661_69541pi_359661_69541',

            'Lead Rating': '',
        }

        all_data = []

        for row in reader:
            pardot_data = {}
            for header in headers:
                tag_name = tag_names.get(header)
                if tag_name is not None:
                    value = row[header]
                    if header in [
                                  "Languages",
                                  "Email 30 day access to these programs",
                                  "The next adoption related deadline will be",
                                  "Wayside is giving you these print resources now",
                                  "Wayside should stay in touch about",
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
                        'EntreCulturas 1A Spanish': '9122772',
                        'EntreCulturas 1B Spanish': '9123315',
                        'EntreCulturas 1 Spanish': '13463',
                        'EntreCulturas 2 Spanish': '13507',
                        'EntreCulturas 3 Spanish': '13518',
                        'EntreCulturas 4 Unit 1 Spanish': '13338928',
                        'Tejidos': '1955',
                        'Triangulo Aprobado': '3551',
                        'Triangulo APreciado': '6250713',
                        'Azulejo': '3',
                        'APprenons': '11138',
                        'Neue Blickwinkel German': '12741',
                        'Chiarissimo Uno Italian': '6698',
                        'Chiarissimo Due Italian': '12271',
                        'Scandite Muros Latin': '13435',
                        'EntreCultures 1A French': '12730537',
                        'EntreCultures 1B French': '12730581',
                        'EntreCultures 1 French': '9330042',
                        'EntreCultures 2 French': '8404114',
                        'EntreCultures 3 Unit 1 French': '13486602'
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
            push_data_to(parsed_data_fn, 'http://www2.waysidepublishing.com/l/359661/2019-11-05/l8tm6s')

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
