import json, sys, os, glob
def make(utils, filename, customHtml, customCss, customJsOl, customJsGeneric):
    cols = {}
    tables = utils.get_tables();
    for table in tables:
        cols[table] = utils.yank_instance_col(table, table)
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
// A map of table ids to their instance columns (or _id if we couldn't pull it)
var display_cols = """ + json.dumps(cols) + """
var table_id = null;
var row_id = null;
// a map you can override in customJsOnload that dictates which columns get printed and how they get printed
// e.g. pretty printed or not, or you can give a callback for a column that returns what should get printed
// If you leave it as this, it will just print every column as not pretty printed no matter what
// If you set it, only the things you put in it will get set. For what to put in it, see README.md
var colmap = [];
// The main column. We'll try and get this from display_cols unless you override it in customJsOl
var main_col = "";
// Used so we only have to query the database once, just save the result object
var cached_d = null;
// List of tables to edit with formgen. If a table isn't found in this list, we edit it with survey instead
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
        odkData.deleteRow(table_id, null, row_id, function(d) {
            odkCommon.closeWindow();
        }, function(e) {
            alert("Failed to _delete row - " + JSON.stringify(e));
        });
    }
}
var update_callback = function update_callback(d) {
    cached_d = d;
    var metadata = d.getMetadata();

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
        var xlscol = col;
        var checkMedia = false;
        var split = xlscol.split("_")
        if (["contentType", "uriFragment"].indexOf(split[split.length - 1]) >= 0) {
            var tail_fragment = split[split.length - 1];
            xlscol = split.reverse().slice(1).reverse().join("_")
            pending_media[tail_fragment] = val;
            checkMedia = true;
        }
        for (var j = 0; j < colmap.length; j++) {
            if (colmap[j][0] == xlscol) {
                found = colmap[j];
                break;
            }
        }
        var li = null;
        if (col == main_col) {
            li = document.getElementById("main-col")
        } else {
            li = document.createElement("li");
        }
        var is_html = "text";
        if (checkMedia) {
            if ("contentType" in pending_media && "uriFragment" in pending_media) {
                is_html = "element";
                var type = pending_media["contentType"].split("/")[0];
                var src = odkCommon.getRowFileAsUrl(table_id, row_id, pending_media["uriFragment"]);
                if (type == "audio" || type == "video") {
                    var elem = document.createElement(type);
                    var source = document.createElement("source");
                    source.src = src;
                    elem.appendChild(source)
                    val = elem;
                } else if (type == "image") {
                    var elem = document.createElement("img");
                    elem.src = src;
                    val = elem;
                } else {
                    alert("unknown content type for column " + xlscol);
                }
                pending_media = {}
            } else {
                continue;
            }
        } 
        if (found) {
            if (typeof(found[1]) == "string") {
                li.appendChild(make_li(xlscol, found[1], val, "text"));
            } else if (found[1] === true) {
                li.appendChild(make_li(xlscol, displayCol(col, metadata), pretty(val), "text"));
            } else {
                li.appendChild(make_li(xlscol, "", found[1](li, val, d), "html"));
            }
        } else {
            if (col[0] == "_" || colmap.length > 0) {
                // TODO check if its _sync_state or _savepoint_type and change body appropriately
                // Wasn't in the colmap and we have a colmap? Don't display it
                // If we don't have a colmap, default to displaying everything (except underscore prefixed/special columns)
                continue;
            }
            li.appendChild(make_li(xlscol, displayCol(col, metadata), val, is_html));
        }
        if (col != main_col) {
            ul.appendChild(li);
        }
    }
}
var make_li = function make_li(column_id, column_text, value_text, is_html) {
    var wrapper = document.createElement("span");
    wrapper.setAttribute("data-column", column_id);
    wrapper.classList.add("li-inner")
    var colelem = document.createElement("span");
    colelem.innerText = column_text
    colelem.style.fontWeight = "bold";
    wrapper.appendChild(colelem);
    if (is_html == "html") {
        var inner = document.createElement("span")
        inner.innerHTML = value_text;
        wrapper.appendChild(inner);
    } else if (is_html == "text") {
        wrapper.appendChild(document.createTextNode(": " + value_text));
    } else if (is_html == "element") {
        wrapper.appendChild(value_text);
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
