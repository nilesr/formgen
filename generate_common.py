import json, sys
def make(utils, filename, user_translations, choices, which):
    basejs = """
/*
""" + utils.warning + """
*/
var all_choices = """ + json.dumps(choices) + """;
var cols_that_need_choices = """ + json.dumps(which) + """;
""" + open("generate_common.js", "r").read().replace("_formgen_replace_appname", utils.appname).replace("_formgen_replace_user_translations", json.dumps(user_translations))
    open(filename, "w").write(basejs)
