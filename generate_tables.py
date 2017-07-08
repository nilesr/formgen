import json, sys, os, glob
sys.path.append(".")
import utils
tables = [os.path.basename(x) for x in glob.glob("/home/niles/Documents/odk/app-designer/app/config/tables/*")]
tables = [[x, utils.yank_instance_col(x,x) == "_id"] for x in tables]
def entry(x):
    r = "<h2 onClick = 'window.location.href = \"table.html#"+x[0]+"\";'"
    if not x[1]:
        r += " style='color:darkred;'"
    r += ">" + x[0] + "</h2>"
    return r;
basehtml = """
<!doctype html>
<html>
    <head>
    </head>
    <body>
    <h1>List of tables</h1>
""" + "".join([entry(x) for x in tables]) + """
    </body>
</html>
"""
open("tables.html", "w").write(basehtml)
