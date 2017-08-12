import json, sys, os, glob
def make(utils, filename, customHtml, customCss, customJsOl, customJsGeneric):
	cols = {}
	tables = utils.get_tables();
	for table in tables:
		cols[table] = utils.yank_instance_col(table)
	token = utils.gensym(filename)
	basehtml = """
<html>
""" + utils.warning + """
	<head>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8">
		<script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
		<script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
		<script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
		<script type="text/javascript" src="formgen_common.js"></script>
		<script type="text/javascript" src="generate_common.js"></script>
		<link href="generate_detail.css" rel="stylesheet" />
		<style>
""" + customCss + """
		</style>
		<script type="text/javascript" src="userjs/"""+token+""".js"></script>
		<script type="text/javascript" src="generate_detail.js"></script>
	</head>
	<body onLoad='ol();'>
		<div id="header">
			<button id="back" onClick='odkCommon.closeWindow();'></button>
			<button id="delete" onClick='_delete();' disabled></button>
			<button id="edit" onClick='edit();' disabled></button>
			<span id="main-col"></span>
		</div>
		<ul id="rest">Loading...</ul>
""" + customHtml + """
	</body>
</html>"""
	basejs = """
// A map of table ids to their instance columns (or _id if we couldn't pull it)
var display_cols = """ + json.dumps(cols) + """
// List of tables to edit with formgen. If a table isn't found in this list, we edit it with survey instead
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """;
var customJsOl = function customJsOl() {
	"""+customJsOl+"""
}
""" + customJsGeneric
	open(filename, "w").write(basehtml)
	open("userjs/" + token + ".js", "w").write(basejs)
	utils.filenames.append("userjs/" + token + ".js")
