from datetime import datetime
import pytz

def find_country(fac, notes, project_templates):
    notes = notes.lower()
    if fac == "InterVu (US)":
        return "United States"
    elif fac == "InterVu (Germany)":
        return "Germany"
    elif fac == "InterVu (Japan)":
        return "Japan"
    else:
        for key, value in project_templates["Abbreviations"].items():
            co = f" {key.lower()} "
            ab = f" {value.lower()} "
            if co in notes or ab in notes:
                return(key)
        return ""


def find_language(notes, two_ca, project_templates):
    notes = notes.lower()
    for i in project_templates["Languages"]:
        if i.lower() in notes:
            return i
    if two_ca == "200":
        return "English"
    else:
        return ""


def define_type(sess_type):
    if sess_type == "Groups":
        return "Groups"
    elif sess_type == "1 on 1":
        return "IDI"
    elif sess_type == "IDI/Groups":
        return "IDI/Groups Mix"


def is_dst(dt=None, timezone='UTC'):
    timezone = pytz.timezone(timezone)
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    if dt.tzinfo is None:
        tz_aware_dt = timezone.localize(dt, is_dst=None)
    else:
        tz_aware_dt = dt.astimezone(timezone)
    return tz_aware_dt.tzinfo._dst.seconds != 0

def make_pretty_notes(note_list):
    pretty_notes = ""

    for x in note_list:
        if x == "CHECK AM OR PM iv":
            pretty_notes += "Confirm if InterVu time is AM or PM. "
        elif x == "CHECK AM OR PM rsp":
            pretty_notes += "Confirm if respondent time is AM or PM. "
        elif x == "CHECK TIME W/ RCR":
            pretty_notes += "No Time provided, check with recruiter. "
        elif x == "UNABLE TO DETERMINE":
            pretty_notes += "Unable to determine time-zone. "
        elif x == "TIMEZONE MISMATCH":
            pretty_notes += "The provided time-zone doesn't align with the times provided. "
        elif x == "BAD EMAIL":
            pretty_notes += "Email appears to be incorrect. "
        elif x == "UNABLE TO DETERMINE COLOR":
            pretty_notes += "Unable to determine row color, please adjust. "
        elif "Potential Overlap" in x:
            pretty_notes += x
            
    return pretty_notes