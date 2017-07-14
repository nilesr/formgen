# This whole thing needs to be generalized into one function, maybe something that takes
# menu a list of triplets like ["some displayed text", "page", "config/assets/other_page.html"]
# and others like ["some displayed text", "group_by", "refrigerators", "model_row_id"]
# or something, but in its current state it's pretty stupid
global_css = lambda utils: """
        <style>
body {
    font-family: "Helvetica Neue", Helvetica, sans-serif;
    text-align: center;
    font-size: 2em;
    background: url('/""" + utils.appname + """/config/assets/img/hallway.jpg') no-repeat center/cover fixed;
    color: #eee;
    min-height: 100vh;
}
.button {
    display: block;
    width: 80%;
    margin-left: 10%;
    background-color: lightblue;
    padding-top: 10px;
    padding-bottom: 10px;
    border: none;
    color: white;
    background-color: #33b5e5;
    /*font-size: 16pt;*/
    font-size: 21px;
    font-weight: 400;
    -webkit-box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .2), inset 0 1px 0 rgba(255, 255, 255, .2), 0 1px 1px rgba(0, 0, 0, .25);
    box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .2), inset 0 1px 0 rgba(255, 255, 255, .2), 0 1px 1px rgba(0, 0, 0, .25);
    border-radius: 2px;
    padding-top: 15px;
    padding-bottom: 15px;
    margin-bottom: 10px;
}
#title {
    display: block;
    font-family: serif;
    background-color: #cc2e2d;
}
        </style>
"""
def from_list(utils, filename, config):
    basehtml = """
<!doctype html>
<html>
    <head>
    """ + global_css(utils) + """
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
        <script type="text/javascript" src="formgen_common.js"></script>
        <script>
""" + config + """
var ol = function ol() {
    document.getElementById("title").innerText = title;
    odkData.arbitraryQuery(table_id, "SELECT _id FROM " + table_id + ";", [], 0, 0, callback, function error(e) {
        alert("Error: " + e);
    });
}
var callback = function callback(d) {
    var button = document.createElement("button");
    allowed_group_bys.reverse();
    allowed_group_bys = allowed_group_bys.concat(0)
    allowed_group_bys[allowed_group_bys.length - 1] = ["", false];
    allowed_group_bys.reverse();
    for (var i = 0; i < allowed_group_bys.length; i++) {
        var button = document.createElement("button");
        var pair = allowed_group_bys[i]
        if (typeof(pair) == "string") pair = [pair, true];
        if (pair[1]) {
            button.innerText = "By " + get_from_allowed_group_bys(allowed_group_bys, pair[1], pair, d.getMetadata());
        } else {
            button.innerText = "View All";
        }
        button.classList.add("button");
        document.getElementById("list").appendChild(button);
        (function(button, this_pair) {
            button.addEventListener("click", function() {
                odkTables.launchHTML(null, list_view_filename + "#" + table_id + "/" + this_pair[0]);
            });
        })(button, pair);
        console.log(button)
        document.getElementById("list").appendChild(button);
    }
}
        </script>
    </head>
    <body onLoad='ol();'>
        <div id="title" class="button"></div>
        <div id="list"></div>
    </body>
</html>
    """
    open(filename, "w").write(basehtml)

def make_index(utils, filename, config):
    basehtml = """
<!doctype html>
<html>
    <head>
    """ + global_css(utils) + """
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkCommon.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/js/odkData.js"></script>
        <script type="text/javascript" src="/""" + utils.appname + """/system/tables/js/odkTables.js"></script>
        <script type="text/javascript" src="formgen_common.js"></script>
        <script>
""" + config + """
var ol = function ol(d) {
    document.getElementById("title").innerText = title;
    for (var i = 0; i < menu.length; i++) {
        var button = document.createElement("button");
        var pair = menu[i]
        button.innerText = pair[1]
        button.classList.add("button");
        document.getElementById("list").appendChild(button);
        (function(button, this_pair) {
            button.addEventListener("click", function() {
                odkTables.launchHTML(null, this_pair[0]);
            });
        })(button, pair);
        console.log(button)
        document.getElementById("list").appendChild(button);
    }
}
        </script>
    </head>
    <body onLoad='ol();'>
        <div id="title" class="button"></div>
        <div id="list"></div>
    </body>
</html>
    """
    open(filename, "w").write(basehtml)

