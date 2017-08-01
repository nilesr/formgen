import json, sys, os, glob
def make(utils, filename):
	cols = {}
	tables = utils.get_tables();
	for table in tables:
		cols[table] = utils.yank_instance_col(table)
	basehtml = """
<!doctype html>
""" + utils.warning + """
<html>
	<head>
		<script type="text/javascript" src="/default/system/js/odkCommon.js"></script>
		<!--
			<script type="text/javascript" src="/default/system/js/odkData.js"></script>
		-->
		<script type="text/javascript" src="/default/system/tables/js/odkTables.js"></script>
		<script type="text/javascript" src="formgen_common.js"></script>
		<script type="text/javascript" src="generate_common.js"></script>
		<script>
var table_ids = """ + json.dumps(tables) + """
var display_cols = """ + json.dumps(cols) + """
var allowed_tables = """ + json.dumps(utils.get_allowed_tables()) + """
var localized_tables = """ + json.dumps(utils.get_localized_tables()) + """;
var ol = function ol() {
	document.getElementsByTagName("h1")[0].innerText = _t("List of tables");
	for (var i = 0; i < table_ids.length; i++) {
		var table = table_ids[i];
		var h2 = document.createElement("h2");
		h2.innerText = display(localized_tables[table], table, window.possible_wrapped.concat("title"));
		(function(h2, table) {
			h2.addEventListener("click", function() {
				page_go("config/assets/table.html#" + table);
			});
		})(h2, table);
		if (allowed_tables.indexOf(table) < 0) {
			h2.style.color = "darkred";
		}
		document.body.appendChild(h2);
	}
}
		</script>
	</head>
	<body onLoad='ol();'>
		<h1></h1>
	</body>
</html>
"""
	open(filename, "w").write(basehtml)
