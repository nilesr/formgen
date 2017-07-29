import json, sys
def make(utils, filename, user_translations, choices, which):
	defs = utils.custom_prompt_types;
	js_defs = ""
	all_custom_prompt_types = []
	for x in defs:
		js_defs += json.dumps(x[1]) + ": {" + x[3] + "},"
		all_custom_prompt_types.append(x[1]);
	basejs = """
/*
""" + utils.warning + """
*/
var all_choices = """+json.dumps(choices)+""";
var cols_that_need_choices = """+json.dumps(which)+""";
var appname = """ + json.dumps(utils.appname) + """;
var custom_prompt_types = {""" + js_defs + """};
var all_custom_prompt_types = """ + json.dumps(all_custom_prompt_types) + """;
var user_translations = """+json.dumps(user_translations) + ";"
	open(filename, "w").write(basejs)
