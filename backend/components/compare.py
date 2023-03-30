import json
from datetime import datetime

def get_json_data():
    # with open("./json_templates/project_details.json") as project_json:
    #     project_details = json.load(project_json)

    with open("./json_templates/rsp_grid_details.json") as rsp_grid_json:
        rsp_grid_data = json.load(rsp_grid_json)

    with open("./json_templates/rsp_pc_details.json") as rsp_pc_json:    
        rsp_pc_data = json.load(rsp_pc_json)

    return [rsp_grid_data, rsp_pc_data]


def save_combo_data(rsp_list, missing_rsp_list, overlaps, stats):
    data = {
        "grid_rsps" : rsp_list,
        "missing_rsps" : missing_rsp_list,
        "overlaps" : overlaps,
        "stats" : stats
    }
    with open("./json_templates/rsp_combo_details.json", "w") as outfile:
        json.dump(data, outfile, default=str)
    
    return data


def compare_grid_pc(project_details):
    rsp_grid_data, rsp_pc_data = get_json_data()
    # # found_on_pc = []

    pnums = project_details["project-numbers"]
    pc_dates = [datetime.strptime(x, "%m/%d/%Y") for x in project_details["dates"]]
    pc_statuses = project_details["statuses"]
    sess_type = project_details["session-type"]

    date_project = {pc_dates[i] : pnums[i] for i in range(len(pnums))}
    # project = date_project[rsp["date"]]

    rsps_to_add = 0
    rsps_to_delete = 0
    rsps_to_change = 0

    rsp_list = []
    missing_rsp_list = []
    overlaps = []

    for i in rsp_grid_data["rsp_data"]:
        grid_dname = i["display_name"]
        grid_time =  datetime.strptime(i["iv_time"], "%H:%M:%S").time()
        grid_email = i["email"]
        grid_phone1 = i["phone1"]
        grid_date = datetime.strptime(i["date"], "%Y-%m-%d").date()
        grid_dt = datetime.combine(grid_date, grid_time)  
        i["iv_time"] = datetime.strftime(grid_dt, "%#I:%M %p")
        i["date"] = datetime.strftime(grid_dt, "%#m/%#d/%Y")
        color = i["row_color"]
        
        if len(rsp_pc_data) == 0:
            #if pc is empty, all respondents are new
            i["project_nums"] = []
        else:
            proj_nums = []
            # print(grid_dt)
            for j in rsp_pc_data:
                pc_dname = j["name"]
                pc_time =  datetime.strptime(j["my-time"], "%I:%M %p").time()
                pc_email = j["email"]
                pc_phone = j["phone"]
                pc_date = datetime.strptime(j["date"], "%m/%d/%Y").date()
                pc_dt = datetime.combine(pc_date, pc_time) 
                pc_num = j["project"]
                pc_status = j["status"]

                # print(pc_dt)
                if grid_email:
                    if (grid_email == pc_email and grid_dt == pc_dt and 
                    (pc_dname in grid_dname or grid_dname in pc_dname)):
                        proj_nums.append({pc_num : [pc_status, "Full Match"]})
                        j["found"] = True
                        
                        color = "stale yellow" if color == "yellow" else color
                    elif grid_email == pc_email and grid_dt == pc_dt:
                        proj_nums.append({pc_num : [pc_status, "Diff name"]})
                        j["found"] = True
                        color = "stale yellow" if color == "yellow" else color
                    elif grid_email == pc_email and (pc_dname in grid_dname or grid_dname in pc_dname):
                        if grid_date == pc_date:
                            proj_nums.append({pc_num : [pc_status, "Diff time"]})
                            j["found"] = True
                            color = "stale yellow" if color == "yellow" else color
                        elif grid_time == pc_time:
                            proj_nums.append({pc_num : [pc_status, "Diff date"]})
                            j["found"] = True
                            color = "stale yellow" if color == "yellow" else color
                    elif (pc_dname in grid_dname or grid_dname in pc_dname) and grid_dt == pc_dt:
                        proj_nums.append({pc_num : [pc_status, "Diff email"]})
                        j["found"] = True
                        color = "stale yellow" if color == "yellow" else color
                elif (pc_dname in grid_dname or grid_dname in pc_dname) and grid_dt == pc_dt:
                    pass
                elif grid_dt == pc_dt and sess_type == "IDI":
                    gdt = grid_dt.strftime("%#m/%#d/%#y %#I:%M %p")
                    pdt =pc_dt.strftime("%#m/%#d/%#y %#I:%M %p")
                    overlaps.append(f"Potential overlap: Grid - {gdt} {grid_dname} | PC - {pdt} {pc_dname}")

                if j == rsp_pc_data[-1] and proj_nums == []:
                    proj_nums.append("not found")
                   
            i["project_nums"] = proj_nums
        if color == "stale yellow":
            i["row_color"] = color
            i["row_color_hex"] = "FFFFFFFF"
        rsp_list.append(i)

        if color == "yellow":
            rsps_to_add +=1
        elif color == "green":
            rsps_to_change +=1
        elif color == "red":
            rsps_to_delete +=1
        
    if "@" in rsp_grid_data["spoc"]:
        spoc = {True : rsp_grid_data["spoc"]}
    else:
        spoc = {False : ""}

    missing_rsp_list = [x for x in rsp_pc_data if "found" not in x.keys()]
    missing_rsp_list = [x for x in missing_rsp_list if x["group-time"] != "Deleted/"]

    stats = {
        "spoc" : spoc,
        "rsps_to_add" : rsps_to_add,
        "rsps_to_delete" : rsps_to_delete,
        "rsps_to_change" : rsps_to_change,
        "missing_rsps" : len(missing_rsp_list),
        "overlaps" : len(overlaps)
    }

    return save_combo_data(rsp_list, missing_rsp_list, overlaps, stats)


def adjust_confirmed_details(new_details):
    with open("./json_templates/project_details.json") as project_json:
        project_details = json.load(project_json)
    
    project_details["country"] = new_details["country"]
    project_details["language"] = new_details["language"]
    project_details["session-type"] = new_details["session_type"]
    project_details["rcr_name"] = new_details["rcr_name"]
    project_details["spoc"] = new_details["spoc"]
    project_details["bcc"] = new_details["bcc"]
    project_details["stats"] = new_details["stats"]
    
    with open("./json_templates/project_details.json", "w") as outfile:
        json.dump(project_details, outfile, default=str)