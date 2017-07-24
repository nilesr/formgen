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
		<link href="generate_table.css" rel="stylesheet" />
		<style>
		""" + customCss + """
		</style>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8">
		<script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
		<script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
		<script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
		<script type="text/javascript" src="formgen_common.js"></script>
		<script type="text/javascript" src="generate_common.js"></script>
		<script>
// If you set a display_col, that column will be shown in the large text for each row item.
// If you don't set one, we'll try and use the table id to pull it from this variable, which stores the
// instance column for each table or _id if it couldn't be found.
var display_cols = """ + json.dumps(cols) + """
// List of tables we can add/edit with formgen, if the table isn't found in this list, we'll use survey
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """
// A map of table ids to tokens that can be used to localize their display name
var localized_tables = """ + json.dumps(utils.get_localized_tables()) + """;
var display_col_wrapper = null;
var customJsOl = function customJsOl() {
	"""+customJsOl+"""
}
var customJsSearch = function customJsSearch() {
	"""+customJsSearch+"""
}
""" + customJsGeneric + """
		</script>
		<script type="text/javascript" src="generate_table.js"></script>
	</head>
	<body onLoad="ol();">
		<div id="header">
			<button id='back' onClick='page_back();'></button>
			<span id="table_id"></span>
			<button id='add' onClick='add();'></button>
		</div>
		<div id="navigation">
			<button id="group-by" onClick='groupBy();' style='font-size: small;' disabled></button>
			<select id="group-by-list" style='display: none;'></select>
			<button id="group-by-go" style='display: none;' onClick="groupByGo();"></button>
			<button disabled id='prev' onClick='prev();'></button>
			<select id="limit" onChange='newLimit();'>
				<!--<option value="2">2 (debug)</option>-->
				<option value="20">20</option>
				<option value="50">50</option>
				<option value="100">100</option>
				<option value="1000">1000</option>
			</select>
			<span id="navigation-text">Loading...</span>
			<button disabled id='next' onClick='next();'></button>
		</div>
		<div id="search">
			<input type='text' id='search-box' onblur='offset=0; update_total_rows(false)' />
			<!--
				<button onClick='offset=0; update_total_rows(false);' id='search-button'></button>
			-->
			<button id='search-button'></button>
		</div>
		<div id="list">Loading...</div>
		""" + customHtml + """
	</body>
</html>"""
	open(filename, "w").write(basehtml)
