import json, sys, os, glob
sys.path.append(".")
import utils
cols = {}
tables = utils.get_tables();
for table in tables:
    cols[table] = utils.yank_instance_col(table, table)
basehtml = """
<!doctype html>
<html>
    <head>
        <style>input {font-size: 16px;}</style>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <script type="text/javascript" src="/default/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/default/system/js/odkData.js"></script>
        <script type="text/javascript" src="/default/system/tables/js/odkTables.js"></script>
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

var ol = function ol() {
    table_id = document.location.hash.slice(1);
    display_col = display_cols[table_id];
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
        //sql = sql.concat(" WHERE " + display_col + " LIKE ?")
        where = display_col + " LIKE ?";
        query_args = query_args.concat("%" + search + "%");
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
    //odkData.arbitraryQuery(table_id, sql, query_args, limit, offset, function(d) {
    //odkData.query(table_id, where, query_args, null, null, null, null, limit, offset, false, function success(d) {
    var the_query = make_query(search, limit, offset);
    odkData.query(table_id, the_query[0], the_query[1], the_query[2], the_query[3], the_query[4], the_query[5], the_query[6], the_query[7], the_query[8], function success(d) {
        if (d.getCount() == 0) {
            list.innerText = "No results";
        } else {
            list.innerHTML = "";
        }
        document.getElementById("navigation-text").innerText = "Showing rows " + (offset+(total_rows == 0 ? 0 :1)) + "-" + (offset+d.getCount()) + " of " + total_rows;
        for (var i = 0; i < d.getCount(); i++) {
            var span = document.createElement("div");
            span.innerText = d.getData(i, display_col);
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
            span.appendChild(edit);
            span.appendChild(_delete);
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
        <div id="header">
            <button onClick='page_back();'>Back</button>
            <span id="table_id"></span>
            <button onClick='add();'>Add row</button>
        </div>
        <div id="navigation">
            <button disabled=true id='prev' onClick='prev();'>Previous page</button>
            <span id="navigation-text">Loading...</span>
            <button disabled=true id='next' onClick='next();'>Next page</button>
            <select id="limit" onChange='newLimit();'>
                <option value="20">20</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="1000">1000</option>
            </select>
        </div>
        <div id="search">
            <input type='text' id='search-box' onblur='offset=0; update_total_rows(false)' />
            <button onClick='offset=0; update_total_rows(false);'>Search</button>
        </div>
        <div id="list">Loading...</div>
    </body>
</html>
"""
open("table.html", "w").write(basehtml)
