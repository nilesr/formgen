import json, sys, os, glob
sys.path.append(".")
import utils
cols = {}
tables = utils.get_tables();
for table in tables:
    cols[table] = utils.yank_instance_col(table, table)
def make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    basehtml = """
<!doctype html>
""" + utils.warning + """
<html>
    <head>
        <style>
        body {
            margin: 0 0 0 0;
            font-family: Roboto;
        }
        input, button {font-size: 16px;}
        #header {
            padding: 8px 8px 8px 8px;
            text-align: center;
            width: calc(100% - 16px);
            font-size: 150%;
            color: navyblue;
            height: 20%;
            min-height: 1em;
        }
        #back {float: left}
        #add {float: right}
        #list {
            padding: 8px 5% 8px 5%;
        }
        .buttons {
            float: right;
            display: inline-block;
            /* test */
            /*
            position: relative;
            top: 50%;
            -webkit-transform: translateY(-50%);
            transform: translateY(-50%);
            */
            height: 100%;
            vertical-align: middle;
        }
        .li {
            /*min-height: 36px;*/
            width: 100%;
            /*margin-bottom: 10px;*/ /* put some space between the list elements */
        }
        .displays {
            display: inline-block;
            float: left;
        }
        .main-display {
            font-size: 150%;
        }
        .sub-display {
            /*font-size: 75%;*/ /* a bit small */
        }
        #navigation {
            padding: 8px 8px 8px 8px;
            text-align: center;
            margin-bottom: 10px;
        }
        #next {
            float: right;
        }
        #prev {
            float: left;
        }
        #search {
            text-align: center;
        }
        .status {
            /*
            width: 95%;
            */
            height: 10px;
            border-style: none;
            margin-top: 22;
            margin-bottom: 18;
        }
        .status[data-status="COMPLETE"] {
            background-color: #38c0f4; /* Blue */
        }
        .status[data-status="INCOMPLETE"] {
            background-color: #F7C64A; /* Kournikova */
        }
        .status[data-status="null"] {
            background-color: red;
        }
        """ + customCss + """
        </style>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
        <script type="text/javascript" src="formgen_common.js"></script>
        <script>
var add = function() {
    if (allowed_tables.indexOf(table_id) >= 0) {
        page_go("config/assets/formgen/"+table_id+"#" + newGuid());
    } else {
        // TODO
        //odkTables.addRowWithSurveyDefault({}, table_id);
        odkTables.addRowWithSurvey({}, table_id, table_id, null, null);
    }
}
var table_id = "";
var display_cols = """ + json.dumps(cols) + """
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """
var localized_tables = """ + json.dumps(utils.get_localized_tables()) + """;
var allowed_group_bys = null;
var global_join = "";
var display_col = "";
var cols = [];
var limit = 20;
var offset = 0;
var total_rows = 0;
var try_more_cols = false;
var global_where_clause = null;
var global_where_arg = null;
var global_group_by = null;
var global_which_cols_to_select = "*"

var ol = function ol() {
    var sections = document.location.hash.substr(1).split("/");
    table_id = sections[0]
    if (sections.length == 2) {
        global_group_by = sections[1];
    } else {
        global_where_clause = sections[1]
        if (global_where_clause && !(global_where_clause.indexOf(".") >= 0)) global_where_clause = table_id + "." + global_where_clause
        global_where_arg = sections[2]
    }
    display_subcol = [];
    display_col = null;
    """ + customJsOl + """
    if (allowed_group_bys != null && allowed_group_bys.length == 0) document.getElementById("group-by").style.display = "none"
    if (display_col == null) {
        display_col = display_cols[table_id];
    }
    if (display_col == undefined) {
        display_col = "_id"; // BAD IDEA
    }
    search = odkCommon.getSessionVariable(table_id + ":search");
    limit = Number(odkCommon.getSessionVariable(table_id + ":limit", limit));
    if (isNaN(limit)) limit = 20;
    var children = document.getElementById("limit").children;
    var res = 0;
    for (var i = 0; i < children.length; i++) {
        if (children[i].value == limit.toString()) {
            res = i;
            break;
        }
    }
    document.getElementById("limit").selectedIndex = res;
    offset = Number(odkCommon.getSessionVariable(table_id + ":offset"));
    if (isNaN(offset)) offset = 0;
    if (search != undefined && search != null && search.length > 0) {
        document.getElementById("search-box").value = search;
    }
    if (table_id.length == 0) {
        list.innerText = "No table specified!";
        document.location.href = "/""" + utils.appname + """/config/assets/tables.html"
        return;
    }
    document.getElementById("table_id").innerText = display(localized_tables[table_id]);
    odkCommon.registerListener(function doaction_listener() {
        var a = odkCommon.viewFirstQueuedAction();
        if (a != null) {
            // may have added a new row
            update_total_rows(true);
            odkCommon.removeFirstQueuedAction();
        }
    });
    update_total_rows();
}
var newLimit = function newLimit() {
    var newlimit = Number(document.getElementById("limit").selectedOptions[0].value);
    if (!isNaN(newlimit)) {
        limit = newlimit;
    }
    doSearch();
}
var cached_search = null;
var update_total_rows = function update_total_rows(force) {
    var search = document.getElementById("search-box").value;
    if (search == cached_search && !force) {
        console.log("Search was unchanged!")
        doSearch();
        return;
    }
    cached_search = search;
    var the_query = make_query(search, 10000, 0);
    var success = function success(d) {
        total_rows = d.getData(0, "COUNT(*)");
        doSearch();
    };
    var failure = function failure(e) {
        alert("Unexpected error " + e);
    };
    if (global_group_by != null && global_group_by != undefined && global_group_by.trim().length > 0) {
        odkData.arbitraryQuery(table_id, "SELECT COUNT(*) FROM (SELECT * FROM " + table_id + " GROUP BY " + the_query[2] + ")", the_query[1], the_query[6], the_query[7], success, failure);
    } else {
        odkData.arbitraryQuery(table_id, "SELECT COUNT(*) FROM " + table_id + (the_query[0] ? " WHERE " + the_query[0] : "") + (the_query[2] ? " GROUP BY " + the_query[2] : ""), the_query[1], the_query[6], the_query[7], success, failure);
    }
}
var next = function next() {
    offset += limit;
    doSearch();
}
var prev = function next() {
    offset -= limit;
    doSearch();
}
var make_query = function make_query(search, limit, offset) {
    var query_args = []
    //var sql = "SELECT * FROM " + table_id;
    var where = null;
    if (search != null && search.length > 0) {
        var cols = [display_col]
        if (try_more_cols) {
            for (var i = 0; i < display_subcol.length; i++) {
                if (display_subcol[i][1] == null) continue;
                cols = cols.concat(display_subcol[i][1]);
            }
        }
        where = "("
        for (var i = 0; i < cols.length; i++) {
            if (i != 0) {
                where += " OR "
            }
            where += cols[i] + " LIKE ? "
            query_args = query_args.concat("%" + search + "%");
        }
        where += ")"
    }
    if (global_where_clause != undefined && global_where_clause != null) {
        if (where != null && where.trim() != "") {
            where += " AND ";
        }
        if (where == null) where = "";
        where += global_where_clause;
        if (!(global_where_clause.indexOf("IS NULL") > 0)) {
            query_args = query_args.concat(global_where_arg);
        }
    }
    var group_by = null;
    if (global_group_by != undefined && global_group_by != null) {
        group_by = table_id + "." + global_group_by
    }
    join = ""
    if (global_join != null && global_join != undefined && global_join.trim().length > 0) {
        join = global_join;
    }
    //[whereClause, sqlBindParams, groupBy, having, orderByElementKey, orderByDirection, limit, offset, includeKVS, (NOT IN odkData.query!!!) join]
    return [where, query_args, group_by, null, null, null, limit, offset, false, join, global_which_cols_to_select];
}
var getCols = function getCols() {
    if (cols.length == 0) {
        // Don't use global_which_cols_to_select or we will get extra columns in there that we can't actually group by
        odkData.arbitraryQuery(table_id, "SELECT * FROM " + table_id + " WHERE 0", [], 0, 0, function success(d) {
            for (var i = 0; i < d.getColumns().length; i++) {
                var col = d.getColumns()[i];
                if (col[0] != "_") {
                    cols = cols.concat(col);
                }
            }
            document.getElementById("group-by").disabled = false;
            if ((global_group_by != null && global_group_by != undefined && global_group_by.trim().length > 0) || (global_where_clause != null && global_where_clause != undefined && global_where_clause.trim().length > 0)) {
                //global_group_by = global_group_by.trim();
                groupBy();
            }
        }, function failure(e) {
            alert("Could not get columns: " + e);
        }, 0, 0);
    }
}
var doSearch = function doSearch() {
    offset = Math.max(offset, 0);
    document.getElementById("prev").disabled = offset <= 0
    document.getElementById("next").disabled = offset + limit >= total_rows
    var list = document.getElementById("list");
    var search = document.getElementById("search-box").value;
    odkCommon.setSessionVariable(table_id + ":search", search);
    odkCommon.setSessionVariable(table_id + ":limit", limit);
    odkCommon.setSessionVariable(table_id + ":offset", offset);
    var the_query = make_query(search, limit, offset);
    //odkData.query(table_id, the_query[0], the_query[1], the_query[2], the_query[3], the_query[4], the_query[5], the_query[6], the_query[7], the_query[8], function success(d) { // doesn't handle the_query[9] (join)
    getCols()
    var raw = "SELECT " + the_query[10] + " FROM " + table_id + (the_query[9].length > 0 ? " JOIN " + the_query[9] : "") + (the_query[0] ? " WHERE " + the_query[0] : "") + (the_query[2] ? " GROUP BY " + the_query[2] : "")
    console.log(raw);
    odkData.arbitraryQuery(table_id, raw , the_query[1], the_query[6], the_query[7], function success(d) {
        if (d.getCount() == 0) {
            if (!try_more_cols) {
                try_more_cols = true;
                update_total_rows(true)
            } else {
                list.innerText = "No results";
                document.getElementById("navigation-text").innerText = ""
            }
        } else {
            list.innerHTML = "";
            try_more_cols = false;
        }
        var display_total = Number(total_rows);
        var rows = ""
        if (global_group_by == null && global_where_clause == null) rows = "rows "
        var newtext = "Showing " + rows + (offset + (total_rows == 0 ? 0 : 1)) + "-" + (offset + d.getCount()) + " of " + display_total;
        if (global_group_by != null && global_group_by != undefined && global_group_by.trim().length > 0) newtext += " distinct values of " + get_from_allowed_group_bys(global_group_by, false);
        if (global_where_clause != null && global_where_clause != undefined && global_where_clause.trim().length > 0) newtext += " rows where " + get_from_allowed_group_bys(global_where_clause.split(" ")[0], false) + " is " + global_where_arg
        document.getElementById("navigation-text").innerText = newtext;
        for (var i = 0; i < d.getCount(); i++) {
            var li = document.createElement("div");
            var displays = document.createElement("span");
            displays.style.lineHeight = "normal";
            displays.classList.add("displays");
            var mainDisplay = document.createElement("div")
            mainDisplay.classList.add("main-display");
            mainDisplay.innerText = d.getData(i, display_col);
            displays.appendChild(mainDisplay)
            var subDisplay = null;
            for (var j = 0; j < display_subcol.length; j++) {
                if (subDisplay == null) {
                    subDisplay = document.createElement("div")
                    subDisplay.classList.add("sub-display");
                }
                if (typeof(display_subcol[j][0]) == "string") {
                    subDisplay.appendChild(document.createTextNode(display_subcol[j][0]))
                    if (display_subcol[j][1] != null) {
                        subDisplay.appendChild(document.createTextNode(d.getData(i, display_subcol[j][1])))
                    }
                } else if (display_subcol[j][0] == "Group by value: ") {
                    subDisplay.appendChild(document.createTextNode(display_subcol[j][0] + pretty(d.getData(i, display_subcol[j][1]))))
                } else {
                    subDisplay.appendChild(document.createTextNode(display_subcol[j][0](subDisplay, d.getData(i, display_subcol[j][1]), d, j)))
                }
                //subDisplay.innerText = d.getData(i, display_subcol[j][1]);
                if (display_subcol[j][2]) {
                    displays.appendChild(subDisplay)
                    subDisplay = null;
                }
            }
            if (subDisplay != null) {
                displays.appendChild(subDisplay)
            }
            li.appendChild(displays);
            li.classList.add("li");
            li.style.display = "inline-block";
            var buttons = document.createElement("div");
            buttons.classList.add("buttons");
            var edit = document.createElement("button");
            edit.innerText = "Edit";
            var _delete = document.createElement("button");
            _delete.innerText = "Delete";
            (function(edit, _delete, i, d) {
                edit.addEventListener("click", function() {
                    if (allowed_tables.indexOf(table_id) >= 0) {
                        page_go("config/assets/formgen/"+table_id+"#" + d.getData(i, "_id"));
                    } else {
                        // TODO
                        //odkTables.editRowWithSurveyDefault({}, table_id, d.getData(i, "_id"));
                        odkTables.editRowWithSurvey({}, table_id, d.getData(i, "_id"), table_id, null, null);
                    }
                });
                displays.addEventListener("click", function() {
                    if (global_group_by == null || global_group_by == undefined || global_group_by.trim().length == 0) {
                        //page_go("config/assets/detail.html#"+table_id+"/"+d.getData(i, "_id"));
                        odkTables.openDetailView({}, table_id, d.getData(i, "_id"));
                    } else {
                        odkTables.launchHTML({}, clean_href() + "#" + table_id + "/" + global_group_by + (d.getData(i, global_group_by) == null ? " IS NULL " : " = ?" ) + "/" + d.getData(i, global_group_by));
                    }
                });
                _delete.addEventListener("click", function() {
                    if (!confirm("Please confirm deletion of row: " + d.getData(i, "_id"))) {
                        return;
                    }
                    // Escape the LIMIT 1
                    odkData.arbitraryQuery(table_id, "DELETE FROM " + table_id + " WHERE _id = ?;--", [d.getData(i, "_id")], 1000, 0, function(d) {
                        update_total_rows(true);
                    }, function(e) {
                        alert("Failed to _delete row - " + JSON.stringify(e));
                    });
                });
            })(edit, _delete, i, d);
            buttons.appendChild(edit);
            buttons.appendChild(_delete);
            li.appendChild(buttons)
            var hr = document.createElement("hr")
            hr.classList.add("status");
            hr.setAttribute("data-status", d.getData(i, "_savepoint_type"))
            list.appendChild(li);
            li.style.lineHeight = li.clientHeight.toString() + "px";
            displays.style.width = (li.clientWidth - buttons.clientWidth - 10).toString() + "px";
            list.appendChild(hr);

        }
        """ + customJsSearch + """
    }, function(d) {
        alert("Failure! " + d);
    });
}
var get_from_allowed_group_bys = function get_from_allowed_group_bys(colname, optional_pair) {
    if (!allowed_group_bys) {
        optional_pair = [colname, true];
    }
    if (!optional_pair) {
        for (var i = 0; i < allowed_group_bys.length; i++) {
            if (allowed_group_bys[i][0] == colname) {
                optional_pair = allowed_group_bys[i];
                break;
            }
        }
    }
    if (!optional_pair) return "ERROR";
    if (optional_pair[1] === true) {
        return displayCol(table_id, optional_pair[0]);
    } else if (optional_pair[1] === false) {
        return optional_pair[0];
    } else {
        return optional_pair[1];
    }
}
var groupBy = function groupBy() {
    var list = document.getElementById("group-by-list");
    if (allowed_group_bys == null) {
        for (var i = 0; i < cols.length; i++) {
            var child = document.createElement("option");
            child.value = cols[i];
            child.innerText = displayCol(table_id, cols[i]);
            list.appendChild(child);
            if (global_group_by == cols[i]) {
                list.selectedOptions = [child];
            }
        }
    } else {
        for (var i = 0; i < allowed_group_bys.length; i++) {
            var child = document.createElement("option");
            child.value = allowed_group_bys[i][0];
            child.innerText = get_from_allowed_group_bys(allowed_group_bys[i][1], allowed_group_bys[i])
            list.appendChild(child);
            if (global_group_by == cols[i]) {
                list.selectedOptions = [child];
            }
        }
    }
    if (global_where_clause != null && global_where_clause != undefined && global_where_clause.trim().length > 0) {
        document.getElementById("group-by").style.display = "none";
        return;
    }
    if (list.children.length == 1) {
        list.selectedOptions = [list.children[0]];
        groupByGo();
    }
    if (global_group_by != null && global_group_by != undefined && global_group_by.trim().length > 0) {
        document.getElementById("group-by").style.display = "none";
        groupByGo()
    } else {
        list.style.display = "inline-block";
        document.getElementById("group-by").style.display = "none";
        document.getElementById("group-by-list").addEventListener("change", function() {
            groupByGo();
        });
        document.getElementById("group-by-list").addEventListener("blur", function() {
            groupByGo();
        });
        //document.getElementById("group-by-go").style.display = "inline-block";
    };
}
var groupByGo = function groupByGo() {
    var go = true;
    if (global_group_by != null && global_group_by != undefined && global_group_by.trim().length > 0) {
        go = false;
    } else {
        var list = document.getElementById("group-by-list");
        global_group_by = list.selectedOptions[0].value;
    }
    var _in = false;
    if (display_col == global_group_by) {
        _in = true;
    } else {
        for (var i = 0; i < display_subcol.length; i++) {
            if (display_subcol[i][1] == global_group_by && display_subcol[i][0] != "Group by value: ") {
                _in = true;
                break;
            }
        }
    }
    if (display_subcol.length == 0 || display_subcol[display_subcol.length - 1][0] != "Group by value: ") {
        if (!_in || display_subcol.length == 0) {
            display_subcol = display_subcol.concat(0)
            display_subcol[display_subcol.length - 1] = ["Group by value: ", global_group_by, true];
        }
        display_subcol[display_subcol.length - 1][2] = true;
    } else {
        if (_in) {
            display_subcol = display_subcol.reverse().slice(1).reverse()
        } else {
            display_subcol[display_subcol.length - 1][1] = global_group_by;
        }
    }
    //window.location.hash = "#" + table_id + "/" + global_group_by
    if (go) {
        odkTables.launchHTML({}, clean_href() + "#" + table_id + "/" + global_group_by);
        //update_total_rows(true);
    }
}
var clean_href = function clean_href() {
    var href = window.location.href.split("#")[0]
    href = href.split('""" + utils.appname + """', 2)[1]
    return href;
}
""" + customJsGeneric + """
        </script>
    </head>
    <body onLoad="ol();">
        <div id="header">
            <button id='back' onClick='page_back();'>Back</button>
            <span id="table_id"></span>
            <button id='add' onClick='add();'>Add row</button>
        </div>
        <div id="navigation">
            <button id="group-by" onClick='groupBy();' style='font-size: small;' disabled>Group by</button>
            <select id="group-by-list" style='display: none;'></select>
            <button id="group-by-go" style='display: none;' onClick="groupByGo();">Go</button>
            <button disabled=true id='prev' onClick='prev();'>Previous page</button>
            <select id="limit" onChange='newLimit();'>
                <!--<option value="2">2 (debug)</option>-->
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="1000">1000</option>
            </select>
            <span id="navigation-text">Loading...</span>
            <button disabled=true id='next' onClick='next();'>Next page</button>
        </div>
        <div id="search">
            <input type='text' id='search-box' onblur='offset=0; update_total_rows(false)' />
            <button onClick='offset=0; update_total_rows(false);'>Search</button>
        </div>
        <div id="list">Loading...</div>
        """ + customHtml + """
    </body>
</html>"""
    open(filename, "w").write(basehtml)
if __name__ == "__main__":
    make("table.html", "", "", "", "", "");
