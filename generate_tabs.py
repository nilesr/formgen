def make(utils, filename, customJs, customCss):
	basehtml = """
<!doctype html>
<html>
	<head>
		<script src="generate_common.js"></script>
		<script src="formgen_common.js"></script>
		<script type="text/javascript" src="/"""+utils.appname+"""/system/js/odkCommon.js"></script>
		<link href="tabs.css" rel="stylesheet" />
		<style>
			"""+customCss+"""
		</style>
		<script>
			"""+customJs+"""
		</script>
		<script src="tabs.js"></script>
	</head>
	<body onLoad='ol();'>
		<div id="tabs"></div>
		<iframe id='iframe'></iframe>
	</body>
</html>
	"""
	open(filename, "w").write(basehtml);
