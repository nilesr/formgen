import json, sys, os, glob
sys.path.append(".")
import utils
tables = [os.path.basename(x) for x in glob.glob("/home/niles/Documents/odk/app-designer/app/config/tables/*")]
tables = [[x, utils.yank_instance_col(x,x) == "_id"] for x in tables]
def entry(x):
    r = "<h2 onClick = 'page_go(\"config/assets/table.html#"+x[0]+"\");'"
    if x[1]:
        r += " style='color:darkred;'"
    r += ">" + x[0] + "</h2>"
    return r;
basehtml = """
<!doctype html>
<html>
    <head>
        <script type="text/javascript" src="/default/system/js/odkCommon.js"></script>
        <!--
            <script type="text/javascript" src="/default/system/js/odkData.js"></script>
        -->
        <script type="text/javascript" src="/default/system/tables/js/odkTables.js"></script>
        <script>
var page_go = function page_go(location) {
    //document.location.href = location;
    odkTables.launchHTML(null, location);
}
var page_back = function page_back() {
    //window.history.back();
    odkCommon.closeWindow(-1, null);
}
        </script>
    </head>
    <body>
    <h1>List of tables</h1>
""" + "".join([entry(x) for x in tables]) + """
    </body>
</html>
"""
open("tables.html", "w").write(basehtml)
