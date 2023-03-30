from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
from datetime import datetime
from components.selenium import get_bot_pclog
from components.get_proj_details import get_respondents
from components.helpers import is_dst

bot, pc_logged = get_bot_pclog()

fvpc = "https://online.focusvision.com/FVPC/default.aspx?Projectid="

with open("./json_templates/email_items.json", "r", encoding="utf8") as file:
    email_items = json.load(file)

def send_email(rsp_info, country, lang, pnum, spoc=None, bcc=None):
    rsp_date = datetime.strptime(rsp_info["date"], "%m/%d/%Y")
    inv_name = rsp_info["invite_name"]
    dis_name = rsp_info["display_name"]
    email = rsp_info["email"]
    sess_time = rsp_info["iv_time"]
    tz = rsp_info["time_zone"]
    pc_data = get_respondents(pnum, rsp_date, "active")
    change_script = "document.querySelector(arguments[0]).innerText = arguments[1]"
    greeting_path = "#CKEditor1_contentDiv > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > font:nth-child(2) > b:nth-child(1)"
    dt_path = "#CKEditor1_contentDiv > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(3) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > font:nth-child(2) > b:nth-child(1)"
    found = False
    # greeting = email_items["Greetings"][lang]
    # greeting = f"{greeting} {inv_name},"

    dst = is_dst(rsp_date, "US/Eastern")

    if country == "United States" or country == "Canada":
        session_time = datetime.strptime(rsp_info["iv_time"], "%I:%M %p").time()
        sess_str_time = rsp_info["iv_time"]
        inv_tz = email_items["US_InvTZ"][tz]
    else:
        session_time = datetime.strptime(rsp_info["iv_time"], "%I:%M %p").time()
        sess_str_time = session_time.strftime('%H:%M')
        if dst and country in email_items["OUS_DT_InvTZ"].keys():
            inv_tz = email_items["OUS_DT_InvTZ"][country]
        else:
            inv_tz = email_items["OUS_ST_InvTZ"][country]

    
    at = email_items["At"][lang]
    day = rsp_date.strftime('%d')
    year = rsp_date.strftime('%Y')

    if lang != "English":
        dotw = f"{lang}{rsp_date.strftime('%A')}"
        inv_dotw = email_items["DaysOTWeek"][dotw]
        month = f"{lang}{rsp_date.strftime('%B')}"
        inv_month = email_items["MonthsOTYear"][month]
        sess_str_time = f"{inv_dotw}, {inv_month} {day}, {year} {at} {sess_str_time} {inv_tz}"
    else:
        dotw = rsp_date.strftime('%A')
        month = rsp_date.strftime('%B')
        sess_str_time = f"{dotw}, {day} {month}, {year} {at} {sess_str_time} {inv_tz}"
    
    # print(greeting)
    for rsp in pc_data:
        name = rsp["name"]
        pc_email = rsp["email"]
        pc_time = rsp["group-time"]
        group_name = ""
        rsp_num = None
        if (email == pc_email or spoc) and (name in dis_name or dis_name in name) and sess_time == pc_time:
            found = True
            group_name = rsp["html-group"]
            rsp_num = int(rsp["html-name"][rsp["html-name"].index("_") + 1:])

            bot.find_element(By.ID, group_name).find_elements(
                By.CLASS_NAME, "sendinvitationanchor")[rsp_num].click()
            time.sleep(1)

            if spoc:
                bot.find_element(By.ID, "ccEmail").send_keys(email)
            
            if bcc:
                bcc = f"GlobalInterVuCoordination@forsta.com;{bcc}"
            else:
                bcc = "GlobalInterVuCoordination@forsta.com"
            bot.find_element(By.ID, "bccEmail").send_keys(bcc) 

            bot.execute_script(change_script, greeting_path, inv_name)
            bot.execute_script(change_script, dt_path, sess_str_time)
            bot.find_element(By.ID, "divemailto").click()
            time.sleep(5)

            bot.find_element(By.ID, "btnSendEmail").click()
    return found


def grid_emailer():
    with open("./json_templates/rsp_combo_details.json", "r") as file:
        data = json.load(file)
        rsps = data["grid_rsps"]

    with open("./json_templates/project_details.json", "r") as file:
        details = json.load(file)    

    country = details["country"]
    language = details["language"]   
    spoc = details["spoc"]
    bcc = details["bcc"]
    dates = details["dates"]
    projects = details["project-numbers"]
    statuses = details["statuses"]
    date_project = {dates[i] : projects[i] for i in range(len(projects))}
    problems = []

    for rsp in rsps:
        project = date_project[rsp["date"]]
        if rsp["row_color"] == "stale yellow":
            sent = send_email(rsp, country, language, project, spoc, bcc)
            if not sent:
                problems.append(rsp["name"])
