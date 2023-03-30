from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, ElementNotInteractableException
import json
import time
from datetime import datetime, timedelta
from components.helpers import is_dst
from components.selenium import get_bot_pclog
from components.get_proj_details import get_respondents

bot, pc_logged = get_bot_pclog()

fv_summary = "http://fvscheduling.focusvision.local/FVScheduling/MasterSummary.htm?MasterId="
fvss = "http://fvscheduling.focusvision.local/FVScheduling/Project.htm?ProjectId="
fvpc = "https://online.focusvision.com/FVPC/default.aspx?Projectid="
notes_url = "https://online.focusvision.com/fvpc/notes.aspx?projectid="

with open("./json_templates/grid_templates.json") as templates_json:
    project_templates = json.load(templates_json)

with open("../frontend/src/json_templates/projectData.json") as project_data:
    country_templates = json.load(project_data)

def add_respondent(rsp_info, sess_type, country, lang, pnum, spoc, rcr_name=None):
    # project_templates - dict of all time zones, and pc equivalents
    rsp_name = rsp_info["rsp_name"]
    invite_name = rsp_info["invite_name"]
    display_name = rsp_info["display_name"]
    rsp_date = datetime.strptime(rsp_info["date"], "%m/%d/%Y")
    phone1 = rsp_info["phone1"]
    phone2 = rsp_info["phone2"]
    rsp_phone =  phone1 if not phone2 else f"{phone1} / {phone2}"
    # rsp_notes = rsp_info["notes"]
    # notes_field = f"Name: {rsp_name} | INV: {invite_name} \n{rsp_notes}"
    if not spoc:
        rsp_email = rsp_info["email"]
        notes_field = f"Name: {rsp_name} | INV: {invite_name}"
    else:
        today = datetime.today().strftime("%#m/%#d")
        rsp_email = ""
        notes_field = f"Name: {rsp_name} | INV: {invite_name}\nInvite sent to {spoc} - {today}"
    
    lang_num = project_templates["pc_lang"][lang]

    pc_data = get_respondents(pnum, rsp_date, "active")
    session_time = datetime.strptime(rsp_info["iv_time"], "%I:%M %p").time()
    sess_str_time = rsp_info["iv_time"]

    #need to add dateline check for APAC
    rsp_time = datetime.strptime(rsp_info["rsp_time"], "%H:%M:%S").time()
    rsp_str_time = rsp_time.strftime("%#I:%M %p")

    dst = is_dst(rsp_date, "US/Eastern")
    edt_est = "EDT" if dst else "EST"
    main_tzn = 19 if dst else 15

    what_page = bot.current_url
    if what_page != fvpc + pnum:
        bot.get(fvpc + pnum)

    if sess_type == "IDI":
        session_name = f"{sess_str_time} {edt_est} IDI"
        local_time = rsp_str_time
        rsp_tzn = project_templates["pc_st_tz"][rsp_info["time_zone"]]
    else:
        session_name = f"{sess_str_time} {edt_est} Group"
        local_time = sess_str_time
        rsp_tzn = main_tzn
        group = ""
        for rsp in pc_data:
            if sess_str_time == rsp["group-time"]:
                group = rsp["html-group"]
                print("issa match")

    if country != "United States" or country != "Canada":
        ous_tz = rsp_info["time_zone"]
        session_name = f"{session_name} ({rsp_str_time} {ous_tz})"
        print(session_name)

    if rcr_name:
        session_name = f"{session_name} ({rcr_name})"

    if sess_type == "IDI" or group == "":
        add = bot.find_element(By.ID, "btnAddSession")
        add.click()
        time.sleep(1)
        # Session Name
        bot.find_element(By.ID, "txtGroupName").send_keys(session_name)
        # Session Time
        element = bot.find_element(By.ID, "txtGroupTime")
        action = ActionChains(bot)
        action.double_click(on_element = element).send_keys(Keys.DELETE) \
            .double_click(on_element = element).send_keys(Keys.DELETE).perform()
        bot.find_element(By.ID, "txtGroupTime").send_keys(local_time)
        bot.find_element(By.ID, "txtGroupTime").send_keys(Keys.ENTER)

        # Session Time Zone (dropdown)
        bot.find_element(By.XPATH, f'//*[@id="groupTimeZone"]/option[{rsp_tzn + 1}]').click()

    else:
        group_num = group[group.index("_") + 1:]
        edit = bot.find_element(By.ID, "GroupEdit" + group_num)
        edit.click()
        # Session Name
        bot.find_element(By.ID, "txtGroupName").clear()
        bot.find_element(By.ID, "txtGroupName").send_keys(session_name)
        time.sleep(1)
    
    # First Name
    bot.find_element(By.ID, "txtUserName").send_keys(display_name)
    # Phone
    bot.find_element(By.ID, "txtPhone").send_keys(rsp_phone)
    # Email
    bot.find_element(By.ID, "txtEmail").send_keys(rsp_email)
    # Language (dropdown)
    bot.find_element(By.XPATH, f'//*[@id="ddlPersonLanguage"]/option[{lang_num +1}]').click()
    # RSP Time Zone (dropdown)
    bot.find_element(By.XPATH, f'//*[@id="ddlRespondentTimeZone"]/option[{rsp_tzn + 1}]').click()
    # Notes
    bot.find_element(By.ID, "txtNotes").send_keys(notes_field)

    try:
        save = bot.find_element(By.ID, "btnSavePeople")
        save.click()
        time.sleep(1)
    except UnexpectedAlertPresentException as err:
        exit = bot.find_element(By.ID, "divClosePeople")
        exit.click()
        time.sleep(1)
        print(err)
        return {"Unable to add" : rsp_info}


    # if sess_type == "Groups":
    #     pass
    # elif sess_type == "IDI":
    #     pass
    # elif sess_type == "IDI/Groups":
    #     pass


def delete_respondent(rsp_info, pnum):
    display_name = rsp_info["display_name"]
    rsp_date = datetime.strptime(rsp_info["date"], "%m/%d/%Y")
    rsp_date_6pm = datetime.strptime(rsp_info["date"] + " 6:00 pm", "%m/%d/%Y %I:%M %p")
    deadline = rsp_date_6pm - timedelta(1)
    dis_name = rsp_info["display_name"]
    email = rsp_info["email"]
    sess_time = rsp_info["iv_time"]
    today = datetime.today()
    today_short = today.strftime("%#m/%#d")
    notes_field = f"\nCancelled on {today_short}"

    pc_data = get_respondents(pnum, rsp_date, "active")

    what_page = bot.current_url
    if what_page != fvpc + pnum:
        bot.get(fvpc + pnum)

    for rsp in pc_data:
        name = rsp["name"]
        pc_email = rsp["email"]
        pc_time = rsp["group-time"]
        group_name = ""
        rsp_num = None
        if (email == pc_email or pc_email == "") and (name in dis_name or dis_name in name) and sess_time == pc_time:
            print(name)
            found = True
            group_name = rsp["html-group"]
            rsp_html = rsp["html-name"]
            rsp_num = int(rsp_html[rsp_html.index("_") + 1:])

            bot.find_element(By.ID, rsp_html).click()
            time.sleep(1)
            #value 11:59 PM

            # First Name
            bot.find_element(By.ID, "txtUserName").send_keys(" (DEL)")
            # Notes
            bot.find_element(By.ID, "txtNotes").send_keys(notes_field)

            select = Select(bot.find_element(By.ID, 'ddlGroupNames'))
            select.select_by_visible_text("Deleted/Rescheduled")
            
            try:
                save = bot.find_element(By.ID, "btnSavePeople")
                save.click()
                time.sleep(1)
                add_lfb(display_name, sess_time,rsp_date, notes_field)
            except UnexpectedAlertPresentException as err:
                exit = bot.find_element(By.ID, "divClosePeople")
                exit.click()
                time.sleep(1)
                print(err)
                return {"Unable to delete" : rsp_info}

def add_lfb(name, sess_time, date, notes):
    dst = is_dst(date, "US/Eastern")
    edt_est = "EDT" if dst else "EST"
    main_tzn = 19 if dst else 15
    session_name = f"{sess_time} {edt_est} IDI"

    add = bot.find_element(By.ID, "btnAddSession")
    add.click()
    time.sleep(1)
    # Session Name
    bot.find_element(By.ID, "txtGroupName").send_keys(session_name)
    # Session Time
    element = bot.find_element(By.ID, "txtGroupTime")
    action = ActionChains(bot)
    action.double_click(on_element = element).send_keys(Keys.DELETE) \
        .double_click(on_element = element).send_keys(Keys.DELETE).perform()
    bot.find_element(By.ID, "txtGroupTime").send_keys(sess_time)
    bot.find_element(By.ID, "txtGroupTime").send_keys(Keys.ENTER)
    # Session Time Zone (dropdown)
    bot.find_element(By.XPATH, f'//*[@id="groupTimeZone"]/option[{main_tzn + 1}]').click()
    
    # First Name
    bot.find_element(By.ID, "txtUserName").send_keys(f"{name} - LFB")
    # Notes
    bot.find_element(By.ID, "txtNotes").send_keys(notes)


def reschedule_respondent(rsp_info):
    delete_respondent(rsp_info)
    add_respondent(rsp_info)


def gridmaster(master_num):
    with open("./json_templates/rsp_combo_details.json", "r") as file:
        data = json.load(file)
        rsps = data["grid_rsps"]

    with open("./json_templates/project_details.json", "r") as file:
        details = json.load(file)    

    session_type = details["session-type"] 
    country = details["country"]
    language = details["language"]   
    dates = details["dates"]
    projects = details["project-numbers"]
    spoc = details["spoc"]
    rcr_name = details["rcr_name"]
    errors = []

    date_project = {dates[i] : projects[i] for i in range(len(projects))}

    for rsp in rsps:
        project = date_project[rsp["date"]]
        if rsp["row_color"] == "yellow":
            result = add_respondent(
                rsp_info=rsp, 
                sess_type=session_type, 
                country=country, 
                lang=language, 
                pnum=project,
                spoc=spoc,
                rcr_name = rcr_name
                )
            if result:
                errors.append(result)
        elif rsp["row_color"] == "red":
            result = delete_respondent(rsp, project)
            if result:
                errors.append(result)
        elif rsp["row_color"] == "green":
            result = reschedule_respondent(rsp)
            if result:
                errors.append(result)

# login()
# gridmaster("m146337")