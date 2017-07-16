import json, sys
def make(utils, filename, user_translations):
    basejs = """
/*
""" + utils.warning + """
*/
""" + open("generate_common.js", "r").read().replace("_formgen_replace_appname", utils.appname).replace("_formgen_replace_user_translations", json.dumps(user_translations))
    open(filename, "w").write(basejs)
