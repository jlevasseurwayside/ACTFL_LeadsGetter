import datetime
import requests
import os
import os.path
import csv
import json
import sys
from pprint import pprint
from constants import constants

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


CHECKBOX_FIELDTYPE = "checkbox"
DROPDOWN_FIELDTYPE = "dropdown"
# this method maps Xpress Lead answer's form value to the form name
# we handle the splitting of checkboxes differently to dropdowns
def map_from_to(v, n, fieldtype):
    all_val = v.split("|")
    ret_val = {}

    for v in all_val:
        curr_tag_name = n.get(v)
        if curr_tag_name != None and curr_tag_name != "":
            tag_pieces = curr_tag_name.split("_")
            new_key = (
                curr_tag_name
                if fieldtype == CHECKBOX_FIELDTYPE
                else "_".join(tag_pieces[0:4])
            )
            ret_val[new_key] = tag_pieces[-1]

    return ret_val


def handle_multioption_headers(header, value):
    if header == "The next adoption-related deadline will be":
        return map_from_to(value, constants.DEADLINE_VALUES, DROPDOWN_FIELDTYPE)

    if header == "Lead Rating":
        return map_from_to(value, constants.LEADS_VALUES, DROPDOWN_FIELDTYPE)

    if header == "What Learning Management System LMS do you use":
        return map_from_to(value, constants.LMS_VALUES, DROPDOWN_FIELDTYPE)

    if header == "Wayside should stay in touch about":
        return map_from_to(value, constants.STAY_IN_TOUCH_VALUES, CHECKBOX_FIELDTYPE)

    if header == "Email 30 day access to these programs":
        return map_from_to(value, constants.DIGITAL_VALUES, CHECKBOX_FIELDTYPE)

    if header == "Wayside is giving you these print resources now":
        return map_from_to(value, constants.PRINT_VALUES, CHECKBOX_FIELDTYPE)

    if header == "Post ACTFL shipment requested":
        return map_from_to(value, constants.SHIP_VALUES, CHECKBOX_FIELDTYPE)


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


def push_data_to_pardot(fn):
    with open(fn, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        tag_names = {
            "First Name": constants.FIRST_NAME_FIELD_ID,
            "Last Name": constants.LAST_NAME_FIELD_ID,
            "Email": constants.EMAIL_FIELD_ID,
            "Company": constants.COMPANY_FIELD_ID,
            "Adoption Date": constants.ADOPTION_DATE,
            "Add Title": constants.ADD_TITLE_FIELD_ID,
            "What Learning Management System LMS do you use": constants.WHAT_LMS_FIELD_ID,
            "Name of Waysider completing the form": constants.WAYSIDER_COMPLETING_FIELD_ID,
            # shipping
            "Address 1": constants.ADDRESS_1_FIELD_ID,
            "Address 2": constants.ADDRESS_2_FIELD_ID,
            "City": constants.CITY_FIELD_ID,
            "Zip Code": constants.ZIP_FIELD_ID,
            "Country": constants.COUNTRY_FIELD_ID,
            constants.XPRESS_LEADS_STATE_FIELD: "",
            # blank values are handled by handle_multioption_headers or tacked on to Comment ID feild
            "What program do you currently use": "",
            "Does your school or district use": "",
            "NOTES (Q11)": "",
            "The next adoption-related deadline will be": "",
            "Lead Rating": "",
            "Email 30 day access to these programs": "",
            "Wayside is giving you these print resources now": "",
            "Post ACTFL shipment requested": "",
        }

        all_data = []

        for row in reader:
            pardot_data = {
                # Lead Source: Conferences
                constants.LEAD_SOURCES_FIELD_ID: "1809660",
                constants.COMMENT_FIELD_ID: "",
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
                        return_value = handle_multioption_headers(header, value)
                        if isinstance(return_value, str):
                            pardot_data[tag_name] = return_value
                        else:
                            pardot_data.update(return_value)
                    elif (
                        header
                        in [
                            "What program do you currently use",
                            "Does your school or district use",
                            constants.XPRESS_LEADS_NOTES_FIELD,
                        ]
                        and value != ""
                    ):
                        # makes the SF notes more readable
                        pretext = (
                            "Notes"
                            if header == constants.XPRESS_LEADS_NOTES_FIELD
                            else header
                        )
                        pardot_data[constants.COMMENT_FIELD_ID] = (
                            pardot_data[constants.COMMENT_FIELD_ID]
                            + pretext
                            + ": \n "
                            + value
                            + "\n"
                        )
                    elif header == constants.XPRESS_LEADS_STATE_FIELD:
                        try:
                            pardot_data[tag_name] = constants.STATE_MAP[value]
                        except KeyError:
                            pass
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
            if data[constants.COMMENT_FIELD_ID] == "":
                continue
            log("%s/%s users\n" % (curr_data, len(all_data)))
            r = requests.post(constants.PARDOT_FORM_URL, files=multipartify(data))
            pprint(str(r.content).count("This field is required."))
            log("Successfully finished.\n")
            curr_data += 1


def push_data_to_ls(fn):
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
                        curr_id = constants.TEXTBOOK_ID_MAP.get(t)
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
        r = requests.post(constants.LS_POST_URL, data=json.dumps(d), headers=headers)
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

            push_data_to_pardot(parsed_data_fn)

            # push_data_to_ls(parsed_data_fn)

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
