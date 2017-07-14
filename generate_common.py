import json, sys
def make(utils, filename):
    basejs = """
/*
""" + utils.warning + """
*/
""" + open("generate_common.js", "r").read().replace("_formgen_replace_appname", utils.appname)
    open(filename, "w").write(basejs)
