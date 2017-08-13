def make(utils, filename, customJs, customCss):
	token = utils.gensym(filename);
	basehtml = """
<!doctype html>
<html>
	<head>
		<script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
		<script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
		<script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
		<script type="text/javascript" src="formgen_common.js"></script>
		<script type="text/javascript" src="generate_common.js"></script>
		<link href="generate_index.css" rel="stylesheet" />
		<style>
		""" + customCss + """
		</style>
		<script type="text/javascript" src="/"""+utils.appname+"""/config/assets/userjs/"""+token+""".js"></script>
		<script src="generate_index.js"></script>
	</head>
	<body onLoad='ol();'>
		<div id="title" class="button"></div>
		<div id="list"></div>
	</body>
</html>
	"""
	basejs = """
			var metadata = {};
			var list_views = {};
			var menu = ["Empty menu!", null, []];
			// BEGIN CONFIG
			""" + customJs + """
			// END CONFIG
			"""
	open(filename, "w").write(basehtml)
	open("userjs/" + token + ".js", "w").write(basejs)
	utils.filenames.append("userjs/" + token + ".js")
