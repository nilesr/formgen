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
    border: none;
    color: white;
    background-color: #33b5e5;
    font-size: 21px;
    font-weight: 400;
    -webkit-box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .2), inset 0 1px 0 rgba(255, 255, 255, .2), 0 1px 1px rgba(0, 0, 0, .25);
    box-shadow: inset 0 -1px 0 rgba(0, 0, 0, .2), inset 0 1px 0 rgba(255, 255, 255, .2), 0 1px 1px rgba(0, 0, 0, .25);
    border-radius: 2px;
    padding-top: 30px;
    padding-bottom: 30px;
    margin-bottom: 20px;
}
#title {
    display: block;
    font-family: serif;
    background-color: #aac;
    color: black;
}
        </style>
"""
def make_demo(utils, filename, config):
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
    if (window.location.hash.slice(1).length > 0) {
        new_menu_path = window.location.hash.slice(1).split("/");
        for (var i = 0; i < new_menu_path.length; i++) {
            if (!isNaN(Number(new_menu_path[i]))) {
                menu_path = menu_path.concat(Number(new_menu_path[i]));
            }
        }
    }
    doMenu();
}
var getMetadataAndThen = function getMetadata(table, callback) {
    if (metadata[table] == undefined && table != null) {
        odkData.arbitraryQuery(table, "SELECT _id FROM " + table, [], 0, 0, function success(d) {
            metadata[table] = d.getMetadata();
            callback(metadata[table]);
        }, function error(e) {
            alert("Error: " + e);
        });
    } else {
        callback(metadata[table]);
    }
}
var menu_path = [];
var make_submenu = function make_submenu() {
    var submenu = menu;
    for (var i = 0; i < menu_path.length; i++) {
        submenu = submenu[2][menu_path[i]];
    }
    return submenu;
}
var buttonClick = function doButtonClick(path) {
    menu_path = menu_path.concat(Number(path));
    var submenu = make_submenu();
    if (submenu[1] == "_html") {
        odkTables.launchHTML(null, submenu[2]);
    } else {
        // Must be a group by
        if (typeof(submenu[2]) == "string") {
            odkTables.launchHTML(null, list_views[submenu[1]] + "#" + submenu[1] + "/" + submenu[2]);
        } else {
            var new_hash = "#";
            for (var i = 0; i < menu_path.length; i++) {
                new_hash += menu_path[i] + "/";
            }
            odkTables.launchHTML(null, clean_href() + new_hash);
        }
    }
}
var doMenu = function doMenu() {
    document.getElementById("list").innerHTML = "";
    var submenu = make_submenu();
    document.getElementById("title").innerText = _tu(submenu[0]);
    getMetadataAndThen(submenu[1], function(this_table_metadata) {

        for (var i = 0; i < submenu[2].length; i++) {
            var triplet = submenu[2][i];
            var button = document.createElement("button");
            if (triplet[0] === true) {
                button.innerText = _t("By ") + displayCol(triplet[2], this_table_metadata);
            } else {
                button.innerText = _tu(triplet[0]);
            }
            button.classList.add("button");
            document.getElementById("list").appendChild(button);
            (function(button, i) {
                button.addEventListener("click", function() {
                    buttonClick(i);
                });
            })(button, i);
            console.log(button)
            document.getElementById("list").appendChild(button);
        }
    });
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

