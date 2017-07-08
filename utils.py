import json, os, subprocess
def yank_instance_col(table, form):
    formDef = json.loads(open("/home/niles/Documents/odk/app-designer/app/config/tables/" + table + "/forms/" + form + "/formDef.json", "r").read())
    try:
        return [x for x in formDef["xlsx"]["settings"] if x["setting_name"] == "instance_name"][0]["value"]
    except:
        pass
    try:
        return formDef["xlsx"]["specification"]["settings"]["instance_name"]["value"]
    except:
        print("ERROR could not yank instance col for " + table + "/" + form)
        return "_id"
def get_allowed_tables():
    result = []
    for table in get_tables():
        if subprocess.check_output(["adb", "shell", "test -d /sdcard/opendatakit/default/config/assets/formgen/" + table + " && echo yes || echo no"]).decode("utf-8").trim() == "yes":
            result.append(table)
    return result
def get_tables():
    return [os.path.basename(x) for x in glob.glob("/home/niles/Documents/odk/app-designer/app/config/tables/*")]
