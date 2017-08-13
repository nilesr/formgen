def make(utils, filename, customCss, customJs, use_d3 = False):
	token = utils.gensym(filename)
	basejs = """
			window.show_value = false;
			window.iframeOnly = false;
			window.sort = false;
			window.reverse = false;
			// If we need more than this the graph is going to look ugly anyways
			// Colors are Oxley, Serenade, Chilean Fire, Vulcan, Zest, Froly, Havelock Blue, Firebrick, Purple, Regal Blue, Whiskey Sour, Cafe Royale, Fun Blue, Picton Blue and Reef
			window.all_colors = ["#85ac85", "#ffebd7", "#993300", "#37393d", "#e58755", "#ff8080", "#4891d9", "#cc2e2d", "#9900ff", "#1f4864", "#DB9863", "#6E4B2A", "#233C6F", "#438CB7", "#B8D891"]
	""" + customJs
	basehtml = """
<!doctype html>
<html>
	<head>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkData.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkCommon.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/tables/js/odkTables.js"></script>
		<script src="/"""+utils.appname+"""/config/assets/generate_common.js"></script>
		<script src="/"""+utils.appname+"""/config/assets/formgen_common.js"></script>
		<script src="/"""+utils.appname+"""/config/assets/userjs/"""+token+""".js"></script>
		<script src="/"""+utils.appname+"""/config/assets/graph.js"></script>
	"""
	if use_d3:
		basehtml += """
		<link href="/"""+utils.appname+"""/config/assets/d3.css" rel="stylesheet" />
		<script src="/"""+utils.appname+"""/config/assets/graph_d3.js"></script>
		<script src="/"""+utils.appname+"""/config/assets/d3.js"></script>
		"""
		basejs += "var use_d3 = true;"
	else:
		basejs += "var use_d3 = false;"
	basehtml += """
		<link href="/"""+utils.appname+"""/config/assets/generate_index.css" rel="stylesheet" />
		<link href="/"""+utils.appname+"""/config/assets/graph.css" rel="stylesheet" />
		<style>
		"""+customCss+"""
		</style>
	</head>
	<body onLoad='ol();'>
		<div class='button' id="title"></div>
		<div id="d3_wrapper"></div>
		<div id="key"></div>
		<div id="bg"></div>
	</body>
</html>
	"""
	open(filename, "w").write(basehtml);
	open("userjs/" +token + ".js", "w").write(basejs)
	utils.filenames.append("userjs/" + token + ".js")
