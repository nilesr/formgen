def make(utils, filename, customCss):
	basehtml = """
<!doctype html>
<html>
	<head>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkData.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkCommon.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/tables/js/odkTables.js"></script>
		<script src="generate_common.js"></script>
		<script src="formgen_common.js"></script>
		<script src="graph.js"></script>
		<link href="generate_index.css" rel="stylesheet" />
		<link href="graph.css" rel="stylesheet" />
		<style>
		"""+customCss+"""
		</style>
	</head>
	<body onLoad='ol();'>
		<div class='button' id="title"></div>
		<div id="key"></div>
	</body>
</html>
	"""
	open(filename, "w").write(basehtml);