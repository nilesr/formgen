import json, sys
def make(utils, filename, user_translations):
	basejs = """
/*
""" + utils.warning + """
*/
var appname = """ + json.dumps(utils.appname) + """
var user_translations = """+json.dumps(user_translations)
	open(filename, "w").write(basejs)
