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
cwd = os.path.dirname(os.path.realpath(__file__))
new_fn = os.path.join(cwd, "new_data.csv")
old_fn = os.path.join(cwd, "archive.csv")
delta_fn = os.path.join(cwd, "delta.csv")
lock_fn = os.path.join(cwd, "lock.txt")
cronlog_fn = os.path.join(cwd, "cronlog.txt")
log_fn = os.path.join(cwd, "log.txt")
# Debug variables
debug_remove_archive = False
DEBUG_INVITES_EMAIL = "jameslevasseurwayside@gmail.com"


def get_conf_data():
    s = requests.Session()

    s.get(constants.SIGNIN_URL)

    download_url = (
        constants.DOWNLOAD_URL
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

# gets value in dict given and tries to look up alias values for textbook related dicts
def get_mapped_value(v, dict):
    mapped_val = dict.get(v)
    if mapped_val != None and mapped_val != "":
        return mapped_val
    elif dict in [constants.DIGITAL_VALUES, constants.PRINT_VALUES, constants.SHIP_VALUES, constants.TEXTBOOK_ID_MAP]:
        for textbook_identifier, alias_array in constants.TEXTBOOK_ALIAS_LOOKUP.items():
            if v in alias_array:
                return dict.get(textbook_identifier)
    return None

CHECKBOX_FIELDTYPE = "checkbox"
DROPDOWN_FIELDTYPE = "dropdown"
# this method maps Xpress Lead answer's form value to the form name
# we handle the splitting of checkboxes differently to dropdowns
def map_from_to(v, n, fieldtype):
    all_val = v.split("|")
    ret_val = {}

    for v in all_val:
        curr_tag_name = get_mapped_value(v, n)
        if curr_tag_name != None:
            tag_pieces = curr_tag_name.split("_")
            new_key = (
                curr_tag_name
                if fieldtype == CHECKBOX_FIELDTYPE
                else "_".join(tag_pieces[0:4])
            )
            ret_val[new_key] = tag_pieces[-1]

    return ret_val


def handle_multioption_headers(header, value):
    if header == constants.ADOPTION_DEADLINE_XPRESS_LEADS_HEADER:
        return map_from_to(value, constants.DEADLINE_VALUES, DROPDOWN_FIELDTYPE)

    #if header == constants.LEAD_RATING_XPRESS_LEADS_HEADER:
        #return map_from_to(value, constants.LEADS_VALUES, DROPDOWN_FIELDTYPE)

    if header == constants.WHAT_LMS_XPRESS_LEADS_HEADER:
        return map_from_to(value, constants.LMS_VALUES, DROPDOWN_FIELDTYPE)

    if header == constants.STAY_IN_TOUCH_XPRESS_LEADS_HEADER:
        return map_from_to(value, constants.STAY_IN_TOUCH_VALUES, CHECKBOX_FIELDTYPE)

    if header == constants.EMAIL_30_DAY_XPRESS_LEADS_HEADER:
        return map_from_to(value, constants.DIGITAL_VALUES, CHECKBOX_FIELDTYPE)

    if header == constants.WAYSIDE_PRINT_XPRESS_LEADS_HEADER:
        return map_from_to(value, constants.PRINT_VALUES, CHECKBOX_FIELDTYPE)

    if header == constants.POST_ACTFL_XPRESS_LEADS_HEADER:
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
            constants.FIRST_NAME_XPRESS_LEADS_HEADER: constants.FIRST_NAME_FIELD_ID,
            constants.LAST_NAME_XPRESS_LEADS_HEADER: constants.LAST_NAME_FIELD_ID,
            constants.EMAIL_XPRESS_LEADS_HEADER: constants.EMAIL_FIELD_ID,
            constants.COMPANY_XPRESS_LEADS_HEADER: constants.COMPANY_FIELD_ID,
            constants.ADD_TITLE_XPRESS_LEADS_HEADER: constants.ADD_TITLE_FIELD_ID,
            constants.WHAT_LMS_XPRESS_LEADS_HEADER: constants.WHAT_LMS_FIELD_ID,
            constants.NAME_OF_WAYSIDER_XPRESS_LEADS_HEADER: constants.WAYSIDER_COMPLETING_FIELD_ID,
            # shipping
            constants.ADDRESS_1_XPRESS_LEADS_HEADER: constants.ADDRESS_1_FIELD_ID,
            constants.ADDRESS_2_XPRESS_LEADS_HEADER: constants.ADDRESS_2_FIELD_ID,
            constants.CITY_XPRESS_LEADS_HEADER: constants.CITY_FIELD_ID,
            constants.ZIP_XPRESS_LEADS_HEADER: constants.ZIP_FIELD_ID,
            constants.COUNTRY_XPRESS_LEADS_HEADER: constants.COUNTRY_FIELD_ID,
            constants.STATE_XPRESS_LEADS_HEADER: constants.STATE_FIELD_ID,
            # blank values are handled by handle_multioption_headers or tacked on to Comment ID feild
            constants.WHAT_PROGRAM_XPRESS_LEADS_HEADER: "",
            constants.DOES_YOUR_SCHOOL_XPRESS_LEADS_HEADER: "",
            constants.NOTES_XPRESS_LEADS_HEADER: "",
            constants.ADOPTION_DEADLINE_XPRESS_LEADS_HEADER: "",
            # constants.LEAD_RATING_XPRESS_LEADS_HEADER: "",
            constants.EMAIL_30_DAY_XPRESS_LEADS_HEADER: "",
            constants.WAYSIDE_PRINT_XPRESS_LEADS_HEADER: "",
            constants.POST_ACTFL_XPRESS_LEADS_HEADER: "",
            constants.STAY_IN_TOUCH_XPRESS_LEADS_HEADER: "",
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
                        constants.ADOPTION_DEADLINE_XPRESS_LEADS_HEADER,
                        constants.WHAT_LMS_XPRESS_LEADS_HEADER,
                        #pconstants.LEAD_RATING_XPRESS_LEADS_HEADER,
                        constants.STAY_IN_TOUCH_XPRESS_LEADS_HEADER,
                        constants.EMAIL_30_DAY_XPRESS_LEADS_HEADER,
                        constants.WAYSIDE_PRINT_XPRESS_LEADS_HEADER,
                        constants.POST_ACTFL_XPRESS_LEADS_HEADER,
                    ]:
                        return_value = handle_multioption_headers(header, value)
                        if isinstance(return_value, str):
                            pardot_data[tag_name] = return_value
                        else:
                            pardot_data.update(return_value)
                    elif (
                        header
                        in [
                            constants.WHAT_PROGRAM_XPRESS_LEADS_HEADER,
                            constants.DOES_YOUR_SCHOOL_XPRESS_LEADS_HEADER,
                            constants.NOTES_XPRESS_LEADS_HEADER,
                        ]
                        and value != ""
                    ):
                        # makes the SF notes more readable
                        pretext = (
                            "Notes"
                            if header == constants.NOTES_XPRESS_LEADS_HEADER
                            else header
                        )
                        pretty_value = (
                            ", ".join(value.split("|")) if "|" in value else value
                        )
                        pardot_data[constants.COMMENT_FIELD_ID] = (
                            pardot_data[constants.COMMENT_FIELD_ID]
                            + pretext
                            + ": \n "
                            + pretty_value
                            + "\n"
                        )
                    elif header == constants.STATE_XPRESS_LEADS_HEADER:
                        try:
                            pardot_data[tag_name] = constants.STATE_MAP[value]
                        except KeyError as ke:
                            log(ke)
                    elif header == constants.ZIP_XPRESS_LEADS_HEADER:
                        # if SF admins get alpha-numeric changes working for the pardot form, remove this condition for zip
                        if str(value).isnumeric():
                            pardot_data[tag_name] = value
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
            #pprint(data)
            pprint("Pardot... processing %s/%s users" % (curr_data, len(all_data)))
            log("%s/%s users\n" % (curr_data, len(all_data)))
            r = requests.post(constants.PARDOT_FORM_URL, files=multipartify(data))
            curr_data += 1
        log("Successfully finished.\n")

def push_data_to_ls(fn):
    with open(fn, "r") as csvfile:
        all_data = []
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames

        for row in reader:
            data = {
                "key": constants.LS_POST_KEY,
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
                if header == constants.EMAIL_30_DAY_XPRESS_LEADS_HEADER:
                    all_textbooks = curr_val.split("|")

                    for t in all_textbooks:
                        curr_id = get_mapped_value(t, constants.TEXTBOOK_ID_MAP)
                        if curr_id != None and curr_id.strip() != "":
                            data["textbook"].append(curr_id)

                if header == constants.EMAIL_XPRESS_LEADS_HEADER:
                    # for testing email invites
                    if "cdsreg" in curr_val:
                        data["email"] = DEBUG_INVITES_EMAIL
                    else:
                        data["email"] = curr_val

                if header == constants.FIRST_NAME_XPRESS_LEADS_HEADER:
                    data["firstname"] = curr_val

                if header == constants.LAST_NAME_XPRESS_LEADS_HEADER:
                    data["lastname"] = curr_val

                if header == constants.COMPANY_XPRESS_LEADS_HEADER:
                    data["school"] = curr_val

                if header == constants.CITY_XPRESS_LEADS_HEADER:
                    data["city"] = curr_val

                if header == constants.STATE_XPRESS_LEADS_HEADER:
                    data["state"] = curr_val

                if header == constants.ZIP_XPRESS_LEADS_HEADER:
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
        pprint("Learning Site processing... %s/%s users\n" % (curr_d, len(all_data)))
        log("%s/%s users\n" % (curr_d, len(all_data)))
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        r = requests.post(constants.LS_POST_URL, data=json.dumps(d), headers=headers)
        print(r.text)
        curr_d += 1
    pprint("Successfully finished.")
    log("Successfully finished.\n")



def log(text):
    append_log = open(log_fn, "a+")
    append_log.write(str(text))
    append_log.close()


def cron_log(text):
    with open(cronlog_fn, "a+") as c_log:
        if text:
            c_log.write(str(text))
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

            push_data_to_ls(parsed_data_fn)

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