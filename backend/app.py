import sys
import subprocess, os, platform
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from components.squeaky_clean import folder_cleaner, clean_json
from components.selenium import login
from components.get_proj_details import find_master, project_details, recheck_dates
from components.compare import adjust_confirmed_details
from components.updater import gridmaster
from components.emailer import grid_emailer

app = Flask(__name__)
app_config = {"host": "0.0.0.0", "port": 4000}

desktop = os.path.join(os.path.join(os.path.expanduser("~")), "Desktop")
gm_path = f"{desktop}/GridMaster"
if not os.path.exists(gm_path):
    os.makedirs(gm_path)

folder_cleaner(gm_path)

login()

file_path = ""

"""
---------------------- DEVELOPER MODE CONFIG -----------------------
"""
# Developer mode uses app.py
if "app.py" in sys.argv[0]:

  # CORS settings
  cors = CORS(
    app,
    resources={r"/*": {"origins": "http://localhost*"}},
  )

  # CORS headers
  app.config["CORS_HEADERS"] = "Content-Type"


"""
--------------------------- REST CALLS -----------------------------
"""
@app.route("/")
def home():
    return jsonify("backend")


@app.route("/startover", methods=["GET"], strict_slashes=False)
def start_over():
    clean_json()
    return jsonify("Done")


@app.route("/master", methods=["POST"], strict_slashes=False)
def check_master():
    response = json.loads(request.get_data().decode('utf-8'))
    master_num = response["body"]
    file_exists = os.path.exists(f"{gm_path}/{master_num}.xlsx")

    good_master = find_master(master_num)
    if file_exists and good_master == "all good":
        return jsonify("File and Project found")  
    elif good_master == "not a master":
        return jsonify("Not a real Master Number")
    elif good_master == "not IV":
        return jsonify("Not an IV Master Number")
    else:
        return jsonify("No file found (did you rename it?)")


@app.route("/details", methods=["POST"], strict_slashes=False)
def get_project_details():
    response = json.loads(request.get_data().decode('utf-8'))
    data = response["body"]
    master_num = data[0]
    instructions = data[1]
    file_path = f"{gm_path}/{master_num}.xlsx"
    info_dict = {}

    if instructions == "full":
        # gets project details from pc & grid
        info_dict = project_details(master_num, file_path)
    elif instructions == "date":
       info_dict = recheck_dates(master_num)
    elif instructions == "grid":
       info_dict = project_details(master_num, file_path, recheck=True)

    new_file_path = "newFile.xlsx"

    try:
        # if platform.system() == 'Darwin':       # macOS
        #     subprocess.call(('open', new_file_path))
        # elif platform.system() == 'Windows':    # Windows
        #     os.startfile(new_file_path)
        # else:                                   # linux variants
        #     subprocess.call(('xdg-open', new_file_path))
        return json.dumps(info_dict, indent = 4)
    except:
        return jsonify("issue")


@app.route("/update", methods=["POST"], strict_slashes=False)
def update_master():
    """
    this needs
    """
    response = json.loads(request.get_data().decode('utf-8'))
    data = response["body"]

    master_num = data[0]
    confirmed_details = data[1]
    adjust_confirmed_details(confirmed_details)
    gridmaster(master_num)
    return jsonify("done")


@app.route("/email", methods=["GET"], strict_slashes=False)
def email_master():
    """
    this needs
    """
    grid_emailer()
    return jsonify("done")


"""
-------------------------- APP SERVICES ----------------------------
"""
# Quits Flask on Electron exit
@app.route("/quit")
def quit():
  shutdown = request.environ.get("werkzeug.server.shutdown")
  shutdown()

  return


if __name__ == "__main__":
  app.run(**app_config)
