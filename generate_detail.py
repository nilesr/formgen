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
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
        <script type="text/javascript" src="formgen_common.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
        <style>
""" + customCss + """
        body {
            font-family: Roboto;
        }
        #edit, #delete {
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
var global_join = "";
var global_which_cols_to_select = "*"
var ol = function ol() {
    var hash = document.location.hash.substr(1);
    if (hash.length > 0 && hash.indexOf("/") > 0) {
        table_id = hash.split("/")[0]
        row_id = hash.split("/")[1]
    }
    """ + customJsOl + """
    if (main_col.length == 0) {
        main_col = display_cols[table_id];
    }
    get_row_id(update);
    odkCommon.registerListener(function doaction_listener() {
        var a = odkCommon.viewFirstQueuedAction();
        if (a != null) {
            // may have edited this row
            clear_cached_d_and_update();
            odkCommon.removeFirstQueuedAction();
        }
    });
}
var get_row_id = function get_row_id(callback) {
    odkData.getViewData(function (d) {
        row_id = d.getData(0, "_id");
        table_id = d.getTableId();
        callback();
    }, failure_callback, 1, 0);
}
var _delete = function _delete() {
    if (confirm("Please confirm deletion of row " + row_id)) {
        // Escape the LIMIT 1
        odkData.arbitraryQuery(table_id, "DELETE FROM " + table_id + " WHERE _id = ?;--", [row_id], 1000, 0, function(d) {
            odkCommon.closeWindow();
        }, function(e) {
            alert("Failed to _delete row - " + JSON.stringify(e));
        });
    }
}
var update_callback = function update_callback(d) {
    cached_d = d;

    document.getElementById("edit").disabled = false;
    document.getElementById("delete").disabled = false;

    var ul = document.getElementById("rest");
    ul.innerHTML = "";
    if (d.getCount() == 0) {
        ul.innerText = "Row not found!";
    }
    var pending_media = {}
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
        var li = document.createElement("li");
        if (col == main_col) {
            li = document.getElementById("main-col")
        }
        if (found) {
            if (typeof(found[1]) == "string") {
                li.appendChild(make_li(col, found[1], val));
            } else if (found[1] === true) {
                li.appendChild(make_li(col, displayCol(table_id, col), pretty(val)));
            } else {
                li.appendChild(make_li(col, "", found[1](li, val, d)));
            }
        } else {
            var checkMedia = false;
            if (col.split("_", 2)[1] == "contentType") {
                pending_media["contentType"] == val;
                checkMedia = true;
            } else if (col.split("_", 2)[1] == "uriFragment") { 
                pending_media["uriFragment"] == val;
                checkMedia = true;
            } 
            if (checkMedia && "contentType" in pending_media && "uriFragment" in pending_media) {
                var type = pending_media["contentType"].split("/")[0];
                var src = odkCommon.getRowFileAsUrl(table_id, row_id, pending_media["uriFragment"]);
                if (type == "audio" || type == "video") {
                    var elem = document.createElement(type);
                    var source = document.createElement("source");
                    source.src = src;
                    elem.appendChild(source)
                    li.appendChild(elem)
                } else if (type == "image") {
                    var elem = document.createElement("img");
                    elem.src = src;
                    li.appendChild(elem)
                } else {
                    checkMedia = false;
                }
                pending_media = {}
            } 
            if (col[0] == "_" || colmap.length > 0) {
                // TODO check if its _sync_state or _savepoint_type and change body appropriately
                // Wasn't in the colmap and we have a colmap? Don't display it
                // If we don't have a colmap, default to displaying everything (except underscore prefixed/special columns)
                continue;
            }
            if (!checkMedia) {
                li.appendChild(make_li(col, displayCol(table_id, col), val));
            }
        }
        if (col != main_col) {
            ul.appendChild(li);
        }
    }
}
var make_li = function make_li(column_id, column_text, value_text) {
    var wrapper = document.createElement("span");
    wrapper.setAttribute("data-column", column_id);
    wrapper.classList.add("li-inner")
    var colelem = document.createElement("span");
    colelem.innerText = column_text
    colelem.style.fontWeight = "bold";
    wrapper.appendChild(colelem);
    if (column_text == "") {
        var inner = document.createElement("span")
        inner.innerHTML = value_text;
        wrapper.appendChild(inner);
    } else {
        wrapper.appendChild(document.createTextNode(": " + value_text));
    }
    return wrapper;
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
    odkData.arbitraryQuery(table_id, "SELECT " + global_which_cols_to_select + " FROM " + table_id + (global_join.trim().length > 0 ? " JOIN " : "") + global_join + " WHERE " + table_id + "._id = ?", [row_id], 1, 0, update_callback, failure_callback);
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
            <button id="delete" onClick='_delete();' disabled>Delete Row</button>
            <button id="edit" onClick='edit();' disabled>Edit Row</button>
            <span id="main-col"></span>
        </div>
        <ul id="rest">Loading...</ul>
""" + customHtml + """
    </body>
</html>"""
    open(filename, "w").write(basehtml)
if __name__ == "__main__":
    make("detail.html", "", "", "", "");

