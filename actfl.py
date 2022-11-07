import datetime
import requests
import os
import os.path
import csv
import json
import sys
from pprint import pprint
from .constants import *

# Global varibles
new_fn = "new_data.csv"
old_fn = "archive.csv"
delta_fn = "delta.csv"
lock_fn = "lock.txt"
# Debug variables
debug_remove_archive = True


def get_conf_data():
    url = "https://www.xpressleadpro.com/portal/public/signin/ligani@waysidepublishing.com/2182520/qualifiers"

    s = requests.Session()

    s.get(url)

    download_url = (
        "https://www.xpressleadpro.com/portal/public/downloadbyexid/2182520/csv"
    )

    with open(new_fn, "wb") as out_file:
        data = s.get(download_url)
        out_file.write(data.content)


def get_just_new_data_from():
    # If "archive.csv" doesn't exist, that means this is the first set of data ever downloaded
    if os.path.isfile(old_fn) != True:
        return new_fn

    else:
        with open(delta_fn, "a") as delta_file, open(old_fn, "r") as old_file, open(
            new_fn, "r"
        ) as new_file:
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
    all_val = v.split("|")
    ret_val = {}

    for v in all_val:
        curr_tag_name = n.get(v)
        if curr_tag_name != None:
            if curr_tag_name != "":
                ret_val[curr_tag_name] = curr_tag_name.split("_")[-1]

    return ret_val


def handle_headers(header, value):
    if header == "The next adoption-related deadline will be":
        return map_from_to(value, DEADLINE_VALUES)

    if header == "Lead Rating":
        return map_from_to(value, LEADS_VALUES)


"""
    #359661_164409pi_359661_164409
    if header == "What Learning Management System LMS do you use":
        deadline_values = {
            'Before 2019': '359661_41987pi_359661_41987_426393',
            'Spring 2019': '359661_41987pi_359661_41987_426395',
            'Spring 2020': '359661_41987pi_359661_41987_426397',
            'Fall 2019': '359661_41987pi_359661_41987_426399'
        }

        return map_from_to(value, deadline_values)
"""


def multipartify(data, parent_key=None, formatter: callable = None) -> dict:
    if formatter is None:
        formatter = lambda v: (None, v)  # Multipart representation of value

    if type(data) is not dict:
        return {parent_key: formatter(data)}

    converted = []

    for key, value in data.items():
        current_key = key if parent_key is None else f"{parent_key}[{key}]"
        if type(value) is dict:
            converted.extend(multipartify(value, current_key, formatter).items())
        elif type(value) is list:
            for ind, list_value in enumerate(value):
                iter_key = f"{current_key}[{ind}]"
                converted.extend(multipartify(list_value, iter_key, formatter).items())
        else:
            converted.append((current_key, formatter(value)))

    return dict(converted)


def push_data_to(fn, url_pardot):
    with open(fn, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        tag_names = {
            "First Name": FIRST_NAME_FIELD_ID,
            "Last Name": LAST_NAME_FIELD_ID,
            "Email": EMAIL_FIELD_ID,
            "State/Province": STATE_FIELD_ID,
            "Company": COMPANY_FIELD_ID,
            "Adoption Date": ADOPTION_DATE,
            "Add Title": ADD_TITLE_FIELD_ID,
            "What Learning Management System LMS do you use": WHAT_LMS_FIELD_ID,
            "Name of Waysider completing the form": WAYSIDER_COMPLETING_FIELD_ID,
            "What program do you currently use": "",
            "Does your school or district use": "",
            "NOTES (Q11)": "",
            "The next adoption-related deadline will be": "",
            "Lead Rating": "",
        }

        all_data = []

        for row in reader:
            pardot_data = {
                # Lead Source: Conferences
                LEAD_SOURCES_FIELD_ID: "1809660",
                COMMENT_ID_FIELD_ID: "",
            }
            for header in headers:
                tag_name = tag_names.get(header)
                if tag_name != None:
                    value = row[header]
                    if header in [
                        "The next adoption-related deadline will be",
                        # "What Learning Management System LMS do you use",
                        "Lead Rating",
                    ]:
                        return_value = handle_headers(header, value)
                        if isinstance(return_value, str):
                            pardot_data[tag_name] = return_value
                        else:
                            pardot_data.update(return_value)
                    elif (
                        header
                        in [
                            "What program do you currently use",
                            "Does your school or district use",
                            XPRESS_LEADS_NOTES_FIELD,
                        ]
                        and value != ""
                    ):
                        # makes the SF notes more readable
                        pretext = (
                            "Notes" if header == XPRESS_LEADS_NOTES_FIELD else header
                        )
                        pardot_data[COMMENT_ID_FIELD_ID] = (
                            pardot_data[COMMENT_ID_FIELD_ID]
                            + pretext
                            + ": \n "
                            + value
                            + "\n"
                        )
                    else:
                        pardot_data[tag_name] = value
            all_data.append(pardot_data)

        # Enter POST request here
        curr_data = 1
        log(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + " Filling out Pardot form... \n"
        )
        for data in all_data:
            if data[COMMENT_ID] == "":
                continue
            log("%s/%s users\n" % (curr_data, len(all_data)))
            r = requests.post(url_pardot, files=multipartify(data))
            pprint(str(r.content).count("This field is required."))
            log("Successfully finished.\n")
            curr_data += 1


def push_data_to_ls(fn, url_ls):
    with open(fn, "r") as csvfile:
        all_data = []
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames

        for row in reader:
            data = {
                "key": LS_POST_KEY,
                "campaign": "email",
                "textbook": [],
                "email": "",
                "firstname": "",
                "lastname": "",
                "school": "",
                "city": "",
                "state": "",
                "zipCode": "",
            }

            for header in headers:
                curr_val = row[header]
                if header == "Email 30 day access to these programs":
                    all_textbooks = curr_val.split("|")

                    for t in all_textbooks:
                        curr_id = TEXTBOOK_ID_MAP.get(t)
                        if curr_id != None and curr_id.strip() != "":
                            data["textbook"].append(curr_id)

                if header == "Email":
                    if "cdsreg" in curr_val:
                        data["email"] = "jlevdev@gmail.com"
                    else:
                        data["email"] = curr_val

                if header == "First Name":
                    data["firstname"] = curr_val

                if header == "Last Name":
                    data["lastname"] = curr_val

                if header == "Company":
                    data["school"] = curr_val

                if header == "City":
                    data["city"] = curr_val

                if header == "State/Province":
                    data["state"] = curr_val

                if header == "Zip Code":
                    data["zipCode"] = curr_val

            all_data.append(data)
    curr_d = 1
    log(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + " Adding samples for users...\n"
    )
    for d in all_data:
        if len(d["textbook"]) == 0:
            continue
        log("%s/%s users\n" % (curr_d, len(all_data)))
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
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
            c_log.write(
                "Cron ran at: "
                + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                + "\n"
            )


def cleanup(errno):
    if os.path.isfile(old_fn):
        os.remove(old_fn)

    if os.path.isfile(delta_fn):
        os.remove(delta_fn)

    if errno == 0:
        os.rename(new_fn, old_fn)

    os.remove(lock_fn)
    if debug_remove_archive:
        os.remove(old_fn)


def main():
    cron_log(None)

    try:
        if os.path.isfile(lock_fn) != True:
            print("Lock file doesn't exist, process isn't currently running")
            open(lock_fn, "w+")
            # Getting fresh data
            get_conf_data()

            # Parsing through new data to check for duplicates between
            # "new_data.csv" and "archive.csv" if "archive.csv" exists
            # Returns file name to process
            parsed_data_fn = get_just_new_data_from()

            # Push data to Pardot
            push_data_to(
                parsed_data_fn,
                PARDOT_FORM_URL,
            )

            # Push data to the LS
            # push_data_to_ls(parsed_data_fn, LS_POST_URL)

            # Deleting "archive.csv" and "delta.csv" if necessary, renames "new_data.csv" to "archive.csv"
            cleanup(0)
        else:
            cron_log("Lock file exists, process currently running")
            sys.exit(0)

    except Exception as error:
        cron_log(error)
        cleanup(1)
        sys.exit(1)


main()
