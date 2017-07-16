def make_index(utils, filename, customJs, customCss):
    basehtml = """
<!doctype html>
<html>
    <head>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
        <script type="text/javascript" src="formgen_common.js"></script>
        <style>
        """ + open("generate_index.css", "r").read() + """
        """ + customCss + """
        </style>
        <script>
""" + open("generate_index.js", "r").read() + """
// BEGIN CONFIG
""" + customJs + """
// END CONFIG
        </script>
    </head>
    <body onLoad='ol();'>
        <div id="title" class="button"></div>
        <div id="list"></div>
    </body>
</html>
    """
    open(filename, "w").write(basehtml)

