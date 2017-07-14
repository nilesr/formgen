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
""" + open("generate_detail.css", "r").read() + """
""" + customCss + """
        </style>
        <script>
// A map of table ids to their instance columns (or _id if we couldn't pull it)
var display_cols = """ + json.dumps(cols) + """
// List of tables to edit with formgen. If a table isn't found in this list, we edit it with survey instead
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """;
""" + open("generate_detail.js", "r").read().replace("_formgen_replace_customJsOl", customJsOl) + """
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
