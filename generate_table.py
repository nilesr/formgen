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
        }
        #back {float: left}
        #add {float: right}
        #list {
            padding: 8px 5% 8px 5%;
        }
        .buttons {
            float: right;
            display: inline-block;
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
        <script type="text/javascript" src="/default/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/default/system/js/odkData.js"></script>
        <script type="text/javascript" src="/default/system/tables/js/odkTables.js"></script>
        <!--<link rel="stylesheet" href="../assets/pure-base-forms-buttons.css" />-->
        <script>
        
var S4 = function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
}
var newGuid = function newGuid() {
    return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
}
var page_go = function page_go(location) {
    //document.location.href = location;
    odkTables.launchHTML(null, location);
}
var page_back = function page_back() {
    //window.history.back();
    odkCommon.closeWindow(-1, null);
}
var add = function() {
    if (allowed_tables.indexOf(table_id) >= 0) {
        page_go("config/assets/formgen/"+table_id+"#" + newGuid());
    } else {
        // TODO
        //odkTables.addRowWithSurveyDefault(null, table_id);
        odkTables.addRowWithSurvey(null, table_id, table_id, null, null);
    }
}
var table_id = "";
var display_cols = """ + json.dumps(cols) + """
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """
var display_col = "";
var limit = 20;
var offset = 0;
var total_rows = 0;
var try_more_cols = false;

var ol = function ol() {
    table_id = document.location.hash.slice(1);
    display_subcol = [];
    display_col = null;
    """ + customJsOl + """
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
        // TODO - redirect to tables.html
        return;
    }
    document.getElementById("table_id").innerText = table_id;
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
    if (search != null && search.trim().length > 0) {
        var the_query = make_query(search, 10000, 0);
        odkData.arbitraryQuery(table_id, "SELECT COUNT(*) FROM " + table_id + " WHERE " + the_query[0], the_query[1], 10000, 0, function success(d) {
            total_rows = d.getData(0, "COUNT(*)");
            doSearch();
        }, function(e) {
            alert("Unexpected error " + e);
        })
    } else {
        odkData.arbitraryQuery(table_id, "SELECT COUNT(*) FROM " + table_id, [], 10000, 0, function(d) {
            total_rows = d.getData(0, "COUNT(*)");
            doSearch();
        }, function(e) {
            alert("Unexpected error " + e);
        });
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
    var where = null
    if (search != null && search.length > 0) {
        var cols = [display_col]
        if (try_more_cols) {
            for (var i = 0; i < display_subcol.length; i++) {
                cols = cols.concat(display_subcol[i][1]);
            }
        }
        //sql = sql.concat(" WHERE " + display_col + " LIKE ?")
        where = ""
        for (var i = 0; i < cols.length; i++) {
            if (i != 0) {
                where += " OR "
            }
            where += cols[i] + " LIKE ?"
            query_args = query_args.concat("%" + search + "%");
        }
    }
    //sql = sql.concat(" LIMIT " + limit + " OFFSET " + offset);
    //sql = sql.concat(" OFFSET " + offset);
    return [where, query_args, null, null, null, null, limit, offset, false];
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
    //query(tableId, whereClause, sqlBindParams, groupBy, having, orderByElementKey, orderByDirection, limit, offset, includeKVS, success, fail)
    var the_query = make_query(search, limit, offset);
    odkData.query(table_id, the_query[0], the_query[1], the_query[2], the_query[3], the_query[4], the_query[5], the_query[6], the_query[7], the_query[8], function success(d) {
        if (d.getCount() == 0) {
            if (!try_more_cols) {
                try_more_cols = true;
                update_total_rows(true)
            } else {
                list.innerText = "No results";
            }
            return;
        }
        list.innerHTML = "";
        try_more_cols = false;
        document.getElementById("navigation-text").innerText = "Showing rows " + (offset+(total_rows == 0 ? 0 :1)) + "-" + (offset+d.getCount()) + " of " + total_rows;
        for (var i = 0; i < d.getCount(); i++) {
            var li = document.createElement("div");
            var displays = document.createElement("span");
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
                subDisplay.appendChild(document.createTextNode(display_subcol[j][0]))
                subDisplay.appendChild(document.createTextNode(d.getData(i, display_subcol[j][1])))
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
                        //odkTables.editRowWithSurveyDefault(null, table_id, d.getData(i, "_id"));
                        odkTables.editRowWithSurvey(null, table_id, d.getData(i, "_id"), table_id, null, null);
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
            """ + customJsSearch + """
            buttons.appendChild(edit);
            buttons.appendChild(_delete);
            li.appendChild(buttons)
            var hr = document.createElement("hr")
            hr.classList.add("status");
            hr.setAttribute("data-status", d.getData(i, "_savepoint_type"))
            list.appendChild(li);
            list.appendChild(hr);

        }
    }, function(d) {
        alert("Failure! " + d);
    });
}
""" + customJsGeneric + """
        </script>
    </head>
    <body class="pure-form" onLoad="ol();">
        <div id="header">
            <button id='back' onClick='page_back();'>Back</button>
            <span id="table_id"></span>
            <button id='add' onClick='add();'>Add row</button>
        </div>
        <div id="navigation">
            <button disabled=true id='prev' onClick='prev();'>Previous page</button>
            <select id="limit" onChange='newLimit();'>
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
