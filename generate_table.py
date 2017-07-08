import json, sys, os, glob
sys.path.append(".")
import utils
cols = {}
tables = [os.path.basename(x) for x in glob.glob("/home/niles/Documents/odk/app-designer/app/config/tables/*")]
for table in tables:
    cols[table] = utils.yank_instance_col(table, table)
basehtml = """
<!doctype html>
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <!--
            <script type="text/javascript" src="/default/system/js/odkCommon.js"></script>
        -->
        <script type="text/javascript" src="/default/system/js/odkData.js"></script>
        <script>
var S4 = function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
}
var newGuid = function newGuid() {
    return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
}
var add = function() {
    document.location.href = "/default/config/assets/formgen/"+table_id+"#" + newGuid();
}
var table_id = "";
var display_cols = """ + json.dumps(cols) + """
var display_col = "";

var ol = function ol() {
    table_id = document.location.hash.slice(1);
    display_col = display_cols[table_id];
    if (table_id.length == 0) {
        list.innerText = "No table specified!";
        // TODO - redirect to tables.html
        return;
    }
    document.getElementById("table_id").innerText = table_id;
    var list = document.getElementById("list");

    // Escape the LIMIT 1
    odkData.arbitraryQuery(table_id, "SELECT * FROM "+table_id, [], 1000, 0, function(d) {
        for (var i = 0; i < d.getCount(); i++) {
            var span = document.createElement("span");
            span.innerText = d.getData(i, display_col);
            var edit = document.createElement("button");
            edit.innerText = "Edit";
            (function(edit, i, d) {
                edit.addEventListener("click", function() {
                    document.location.href = "/default/config/assets/formgen/"+table_id+"#" + d.getData(i, "_id");
                });
            })(edit, i, d);
            span.appendChild(edit);
            //span.appendChild(document.createElement("br"));
            span.style.width = "100%";
            list.appendChild(span);
        }
    }, function(d) {
        alert("Failure! " + d);
    });
}
        </script>
    </head>
    <body onLoad="ol();">
        <div id="header"><button onClick='window.history.back();'>Back</button><span id="table_id"></span><button onClick='add();'>Add</button></div>
        <div id="list"></div>
    </body>
</html>
"""
open("table.html", "w").write(basehtml)
