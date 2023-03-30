import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from components.excel import clean_and_check_grid, make_new_excel
from components.compare import compare_grid_pc
from components.helpers import find_country, find_language, define_type
from components.selenium import get_bot_pclog, pc_login

bot, pc_logged = get_bot_pclog()

fv_summary = "http://fvscheduling.focusvision.local/FVScheduling/MasterSummary.htm?MasterId="
fvss = "http://fvscheduling.focusvision.local/FVScheduling/Project.htm?ProjectId="
fvpc = "https://online.focusvision.com/FVPC/default.aspx?Projectid="
notes_url = "https://online.focusvision.com/fvpc/notes.aspx?projectid="

with open("./json_templates/grid_templates.json") as templates_json:
    project_templates = json.load(templates_json)

with open("../frontend/src/json_templates/projectData.json") as project_data:
    country_templates = json.load(project_data)


def find_master(master_num):
    bot.get(fv_summary + master_num[1:])
    
    mast_id = bot.find_element(By.ID, "field-master")
    if "#" in mast_id.text:
        return "not a master"

    iv_or_fv = bot.find_element(By.ID, "field-type0")
    if iv_or_fv.text != "InterVu":
        return "not IV"
    
    return "all good"


def save_project_details(info_dict):
    with open("./json_templates/project_details.json", "w") as outfile:
        json.dump(info_dict, outfile)


def save_rsp_pc_details(rsp_dict):
    with open("./json_templates/rsp_pc_details.json", "w") as outfile:
        json.dump(rsp_dict, outfile, default=str)

# dummy_project = open("project_details.json")
# dummy = json.load(dummy_project)


def recheck_dates(master_num):
    bot.get(fv_summary + master_num[1:])

    with open("./json_templates/project_details.json", "r") as file:
        info_dict = json.load(file)

    info_dict["project-numbers"] = [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol0")]
    info_dict["dates"] = [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol1")]
    info_dict["times"] = [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol3")]
    info_dict["statuses"] = [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol6")]

    save_project_details(info_dict)
    return info_dict

# login()
# recheck_dates("m146337")



# project_numbers = ["600612", "600352", "600353"]
# dates =  ["1/1/2023", "12/16/2023", "12/17/2023"]
# statuses = ["Active", "Active", "Active"]


def get_respondents(pnum, pdate, day_status):
    global pc_logged
    # if only want single page, just pass in a list of 1
    rescueduled = ["r/s", "rescheduled", "r.s."]

    rsp_list = []

    if not pc_logged:
        pc_logged = pc_login(pnum)
    else:
        what_page = bot.current_url
        time.sleep(1)
        if fvpc + pnum not in what_page:
            bot.get(fvpc + pnum)
            time.sleep(1)

    g = 0
    tr = 0

    if len(bot.find_elements(By.CLASS_NAME, "GroupsInfo")) == 0:
        time.sleep(1)

    for group in bot.find_elements(By.CLASS_NAME, "GroupsInfo"):
        grp_name = bot.find_element(By.ID, f"GroupName{g}").text
        grp_time = grp_name[:8].strip()
        my_time = bot.find_element(By.ID, f"GroupLocalTime{g}").text[8:]
        status = ""
        extras = ""

        if "(" in grp_name:
            extras = grp_name.split("(")[-1].strip()[:-1]

        r = 0
        for rsp in (bot.find_element(By.ID, f"GroupMainRow_{g}")
            .find_elements(By.CLASS_NAME, "RespondentName")):
            rsp_name = rsp.text.replace("edit", "").strip()
            status = ""

            if "Deleted" not in grp_name and day_status == "Active":
                status = "Scheduled"
            elif day_status != "Active":
                status = "Deleted"
            else:
                for t in rescueduled:
                    if t in rsp_name.lower():
                        status = "Rescheduled"
                        break
                    else:
                        status = "Deleted" 

            rsp_info = {
                "project" : pnum,
                "date" : pdate,
                "group-time" : grp_time,
                "my-time" : my_time,
                "name" : rsp_name,
                "phone" : bot.find_elements(By.CLASS_NAME, "RespContact")[tr].text,
                "email" : bot.find_elements(By.CLASS_NAME, "RespEmail")[tr].text,
                "html-group" : f"GroupMainRow_{g}",
                "html-name" : f"RespondentName{g}_{r}",
                "extras" : extras,
                "status" : status
            }
            rsp_list.append(rsp_info)
            r += 1
            tr += 1
        g += 1
        
    return rsp_list

def get_all_respondents(project_numbers, dates, statuses):
    rsp_list = []   
    for i in range(len(project_numbers)):
        pnum = project_numbers[i]
        pdate = dates[i]
        status = statuses[i]
        rsp_list.extend(get_respondents(pnum, pdate, status))
    save_rsp_pc_details(rsp_list)
    return rsp_list

# login()
# get_all_respondents(project_numbers, dates, statuses)


def project_details(master_num, file_path, recheck=False):
    what_page = bot.current_url
    if fv_summary not in what_page:
        bot.get(fv_summary + master_num[1:])
    
    mast_id = "m" + bot.find_element(By.ID, "field-master").text
    if mast_id == master_num:
        if not recheck:
            first_proj = bot.find_element(By.ID, "field-projectnumber0").text
            info_dict = {
                "master": mast_id,
                "fac" : bot.find_element(By.ID, "field-facility0").text,
                "country" : "",
                "language" : "",
                "two-channel" : "",
                "session-type" : "",
                "webcam" : "",
                "project-notes" : "",
                "project-numbers" : [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol0")],
                "dates" : [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol1")],
                "times" : [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol3")],
                "statuses" : [x.text for x in bot.find_elements(By.CLASS_NAME, "mastergridcol6")],
                "grid_dates" : [],
                "grid_times" : []
            }
            bot.get(fvss + first_proj)

            info_dict["two-channel"] = bot.find_element(By.ID, "field-transmitted-audio").get_attribute("value")

            sess_type = bot.find_element(By.ID, "field-sessiontype").get_attribute("value")
            info_dict["session-type"] = define_type(sess_type)

            info_dict["webcam"] = bot.find_element(By.ID, "field-intervutype").get_attribute("value")

            grid_dates, grid_times, grid_notes = clean_and_check_grid(file_path, master_num, info_dict)

            info_dict["grid_dates"] = grid_dates
            info_dict["grid_times"] = grid_times
            info_dict["grid_notes"] = grid_notes
            get_all_respondents(info_dict["project-numbers"], info_dict["dates"], info_dict["statuses"])

            bot.get(notes_url + first_proj)
            time.sleep(2)
            info_dict["project-notes"] = bot.find_element(By.ID, "intervuNoteEditor").text

            info_dict["country"] = find_country(info_dict["fac"], info_dict["project-notes"], country_templates)
            info_dict["language"] = find_language(info_dict["project-notes"], info_dict["two-channel"], country_templates)
        else:
            with open("./json_templates/project_details.json", "r") as file:
                info_dict = json.load(file)
            null, null, grid_notes = clean_and_check_grid(file_path, master_num, info_dict)
            info_dict["grid_notes"] = grid_notes


        combo_data = compare_grid_pc(info_dict)
        info_dict["stats"] = combo_data["stats"]
        info_dict["missing_rsps"] = combo_data["missing_rsps"]
        make_new_excel(combo_data["grid_rsps"])

        save_project_details(info_dict)

        return info_dict
    else:
        return "master number mismatch"