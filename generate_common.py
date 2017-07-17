import json, sys
def make(utils, filename, user_translations, choices, which):
	basejs = """
/*
""" + utils.warning + """
*/
var all_choices = """ + json.dumps(choices) + """;
var cols_that_need_choices = """ + json.dumps(which) + """;
var appname = """ + json.dumps(utils.appname) + """
var user_translations = """+json.dumps(user_translations)
	open(filename, "w").write(basejs)
