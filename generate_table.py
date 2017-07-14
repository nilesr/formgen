import json, sys, os, glob
cols = {}
def make(utils, filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    tables = utils.get_tables();
    for table in tables:
        cols[table] = utils.yank_instance_col(table, table)
    basehtml = """
<!doctype html>
""" + utils.warning + """
<html>
    <head>
        <style>
        """ + open("generate_table.css", "r").read() + """
        """ + customCss + """
        </style>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
        <script type="text/javascript" src="formgen_common.js"></script>
        <script>
// If you set a display_col, that column will be shown in the large text for each row item.
// If you don't set one, we'll try and use the table id to pull it from this variable, which stores the
// instance column for each table or _id if it couldn't be found.
var display_cols = """ + json.dumps(cols) + """
// List of tables we can add/edit with formgen, if the table isn't found in this list, we'll use survey
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """
// A map of table ids to tokens that can be used to localize their display name
var localized_tables = """ + json.dumps(utils.get_localized_tables()) + """;
""" + open("generate_table.js", "r").read().replace("_formgen_replace_cusotomJsOl", customJsOl).replace("_formgen_replace_customJsSearch", customJsSearch) + """
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
