import json, sys
def make(utils, filename):
    basejs = """
/*
""" + utils.warning + """
*/
""" + open("generate_common.js", "r").read() # This is here so we can do replacement on things like app name later
    open(filename, "w").write(basejs)
