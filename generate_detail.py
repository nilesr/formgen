import json, sys, os, glob
sys.path.append(".")
import utils
cols = {}
tables = utils.get_tables();
for table in tables:
    cols[table] = utils.yank_instance_col(table, table)
def make(filename, customHtml, customCss, customJsOl, customJsGeneric):
    basehtml = """
<html>
""" + utils.warning + """
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <script type="text/javascript" src="/default/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/default/system/js/odkData.js"></script>
        <script type="text/javascript" src="/default/system/tables/js/odkTables.js"></script>
        <style>
""" + customCss + """
        body {
            font-family: Roboto;
        }
        #edit {
            float: right;
        }
        #header {
            text-align: center;
            font-size: 150%;
            min-height: 1.5em;
        }
        #back {
            float: left;
        }
        input, button {font-size: 16px;}
        </style>
        <script>
var display_cols = """ + json.dumps(cols) + """
var table_id = null;
var row_id = null;
var colmap = [];
var main_col = "";
var cached_d = null;
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """;
var ol = function ol() {
    var hash = document.location.hash.substr(1);
    if (hash.length > 0 && hash.indexOf("/") > 0) {
        table_id = hash.split("/")[0]
        row_id = hash.split("/")[1]
    }
    """ + customJsOl + """
    update();
    odkCommon.registerListener(function doaction_listener() {
        var a = odkCommon.viewFirstQueuedAction();
        if (a != null) {
            // may have edited this row
            clear_cached_d_and_update();
            odkCommon.removeFirstQueuedAction();
        }
    });

}
var update_callback = function update_callback(d) {
    cached_d = d;

    table_id = d.getTableId();
    if (main_col.length == 0) {
        main_col = display_cols[table_id];
    }

    row_id = d.getData(0, "_id");

    document.getElementById("edit").disabled = false;

    var ul = document.getElementById("rest");
    ul.innerHTML = "";
    if (d.getCount() == 0) {
        ul.innerText = "Row not found!";
    }
    for (var i = 0; i < d.getColumns().length; i++) {
        var col = d.getColumns()[i];
        var val = d.getData(0, col);
        var found = false;
        for (var j = 0; j < colmap.length; j++) {
            if (colmap[j][0] == col) {
                found = colmap[j];
                break;
            }
        }
        if (!found && col[0] == "_") {
            // TODO check if its _sync_state or _savepoint_type and change body appropriately
            continue;
        }
        var li = document.createElement("li");
        if (col == main_col) {
            li = document.getElementById("main-col")
        }
        if (found) {
            if (typeof(found[1]) == "string") {
                li.appendChild(document.createTextNode(found[1]));
                li.appendChild(document.createTextNode(val));
            } else {
                li.appendChild(document.createTextNode(found[1](li, val)));
            }
        } else {
            li.appendChild(document.createTextNode(col + ": " + val));
        }
        if (col != main_col) {
            ul.appendChild(li);
        }
    }
}
var failure_callback = function failure_callback(e) {
    alert("Error querying data: " + e);
    odkCommon.closeWindow();
}
var update = function update() {
    if (cached_d != null) {
        update_callback(cached_d);
        return;
    }
    if (table_id != null && row_id != null) {
        odkData.arbitraryQuery(table_id, "SELECT * FROM " + table_id + " WHERE _id = ?", [row_id], 1, 0, update_callback, failure_callback);
    } else {
        odkData.getViewData(update_callback, failure_callback, 1, 0);
    }
}
var clear_cached_d_and_update = function clear_cached_d_and_update() {
    cached_d = null;
    update();
}
var edit = function() {
    if (allowed_tables.indexOf(table_id) >= 0){ 
        odkTables.launchHTML({}, "config/assets/formgen/" + table_id + "#" + row_id);
    } else {
        odkTables.editRowWithSurvey({}, table_id, row_id, table_id, null, null);
    }
}
""" + customJsGeneric + """
        </script>
    </head>
    <body onLoad='ol();'>
        <div id="header">
            <button id="back" onClick='odkCommon.closeWindow();'>Back</button>
            <span id="main-col"></span>
            <button id="edit" onClick='edit();' disabled>Edit Row</button>
        </div>
        <ul id="rest">Loading...</ul>
""" + customHtml + """
    </body>
</html>"""
    open(filename, "w").write(basehtml)
if __name__ == "__main__":
    make("detail.html", "", "", "", "");

