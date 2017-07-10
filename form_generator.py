import json, sys, os, glob, traceback, subprocess
sys.path.append(".")
import utils
# TODO items
# Must have before release!
#   - More filtering options in generate_table
#   - fix translation bugs (may have to pull in handlebars)
#   - Check permissions?
#   - Can finalize a totally empty form, row never gets inserted
#   - Make serious improvements to detail views, like displaying images instead of dbcol_uriFragment and dbcol_contentType - LOCALIZE COLUMN IDS!
#   - Display sync state in table, sync state and savepoint type in detail
#   - Make group by configurable in custom.py, maybe a preset list of group by options with display names for them, and automatically select it if there's only one thing. If not specified in customJsOl just generate it the way we currently do
#   - Launching table.html via tables.html or specifying table_id in the hash is now broken
#   - take picture is broken
#   - query filters
# Other things not implemented
#   - Figure out when to calculate assigns (and implement calculates object)
#   - Fix odkTables.editRowWithSurveyDefault() - SURVEY BUG
#   - Handle doAction in generate_table.py to call update_total_rows(true)
# 	- linegraph, piechart
# 	- goto (EASY!)
# 	- sections (could be hard)
# 	- send_sms
# 	- read_only_image
# 	- datetime, time
# 	- user_branch
# 	- signature
# 	- barcode
#   - customPromptTypes.js (could be easy-ish if I only support intent buttons, and I can check the prompt_types sheet to make sure it exists)
#   - Maybe automatically generate map view files? Much longer term goal
# Things that ARE supported
#   - If statements for displaying/not displaying prompts
#       - can be arbitrarily nested
#       - does some basic optimization so things in an 'if false' or 'if 0' won't even be put in the output file
#   - Csv queries
#       - With callbacks written in the xlsx (even the ones that use underscore)
#   - Cross table queries
#       - Can pull instance name from another form (done at compile time not runtime)
#   - Begin screen and end screen clauses
#   - Translation (almost) - done on the browser side
#   - Validation constraints
#       - Numeric data type validation
#       - Javascript based (i.e. "selected(data('acknowledged'), 'yes')" or "data('age') > 18", etc...)
#       - Required field constraints
#       - Won't let you next, back, finalize or save to the database until validation passes for the current screen
#   - Basic data types, text/string, integer, number/decimal
#   - Select one, select one dropdown (actually implemented as very different widgets)
#   - Select multiple, select multiple inline
#   - Select one grid, select one with other (needs a little more testing)
#   - acknowledge (alias for select_one with yes/no options)
#   - date
#   - assign, with javascript expressions in xlsx, evaluated at end of form
#   - save on prompt value change but also on next/back/finalize
#   - Auto generate row id and insert new row if no row id given in hash
#   - Automatically load prompt values from database abd save new values to database only when changed on the screen
#   - Uses finalized/incomplete properly
#   - translation
#   - barcode, image, video, audio
def die():
    global failed
    failed = True
    raise Exception()
def falsey(r):
    r = str(r).strip().lower();
    if r.endswith(";"):
        r = r[:-1].strip()
    return r == "0" or r == "false";
tables = utils.get_tables()
for table in tables:
    global failed
    failed = False
    try:
        formDef = json.loads(open("/home/niles/Documents/odk/app-designer/app/config/tables/" + table + "/forms/" + table + "/formDef.json", "r").read())
        screens = []
        rules = []
        screen = []
        assigns = []
        has_dates = False
        #defaults = {}
        for item in formDef["xlsx"]["survey"]:
            #print(item)
            if "clause" in item:
                clause = item["clause"].split("//")[0].strip();
                if clause in ["begin screen", "end screen"]:
                    if len(screen) > 0:
                        screens.append("".join(screen))
                    screen = []
                elif clause == "if":
                    rules.insert(0, item["condition"])
                elif clause == "end if":
                    rules = rules[1:]
                elif clause == "": pass
                else:
                    print("bad clause " + item["clause"]); die()
                continue
            if "type" in item:
                if len(rules) > 0:
                    continue_out = False
                    for rule in rules:
                        if falsey(rule):
                            continue_out = True
                            break
                        screen.append("<span style='display: none;' class='validate' data-validate-rule=\"" + str(rule) + "\">")
                    if continue_out:
                        continue
                if "display" in item: screen.append("<span class='translate'>" + json.dumps(item["display"]) + "</span> ")
                dbcol = ""
                if "name" in item:
                    dbcol = "data-dbcol=\""+item["name"]+"\"";
                required = ""
                calculation = ""
                hint = ""
                constraint = ""
                constraint_message = ""
                if "calculation" in item: calculation = "data-calculation=\"" + str(item["calculation"]) + "\"";
                if "display" in item and type(item["display"]) == type([]) and "hint" in item["display"]: hint = "placeholder=\""+item["display"]["hint"]["text"]+"\""
                if "required" in item:
                    required = "data-required=\"required\" "
                    if len(hint) == 0: required += "placeholder=\"Required field\"";
                if "constraint" in item:
                    constraint = "data-constraint=\"" + item["constraint"] + "\""
                if "display" in item and "constraint_message" in item["display"]:
                    constraint_message = "data-constraint_message=\"" + json.dumps(item["display"]["constraint_message"]).replace("\"", "'") + "\""
                attrs = " " + " ".join([dbcol, required, calculation, hint, constraint, constraint_message]) + " "
                wrapped_class = "prompt"
                _class = " class=\"prompt\" "
                if item["type"] == "note":
                    pass
                elif item["type"] == "text" or item["type"] == "string":
                    screen.append("<input type=\"text\" " + attrs + _class + " />")
                elif item["type"] in ["image", "audio", "video"]:
                    # NO DBCOL!
                    hrtype = item["type"][0].upper() + item["type"][1:]
                    for action in ["Choose", "Capture"]:
                        act = "org.opendatakit.survey.activities.Media" + action + hrtype + "Activity"
                        # like MediaChooseImageActivity or MediaCaptureVideoActivity
                        screen.append("<button onClick='doAction({dbcol: \""+item["name"]+"\", type: \"image\"}, \""+act+"\", makeIntent(survey, \""+act+"\", \""+item["name"]+"\"));' data-dbcol='"+item["name"]+"'>" + action + " " + ("Picture" if hrtype == "Image" else hrtype) + "</button>")
                    for suffix in ["uriFragment", "contentType"]:
                        column_id = item["name"] + "_" + suffix
                        dbcol = "data-dbcol=\""+column_id+"\"";
                        attrs = " ".join([dbcol, required, calculation, hint, constraint, constraint_message])
                        if suffix == "contentType": attrs += " style='display: none;' "
                        screen.append("<br />")
                        #screen.append("<label for='"+column_id+"'>"+suffix[0].upper() + suffix[1:] +": </label>")
                        screen.append("<input type=\"text\" disabled=true id='"+column_id+"' " + _class + attrs + " />")
                    if hrtype == "Image":
                        screen.append("<img style='display: none; width: 50%;' class='image' data-dbcol='"+item["name"]+"' />")
                    elif hrtype == "Audio":
                        screen.append("<audio style='display: none;' class='image audio' data-dbcol='"+item["name"]+"'></audio>")
                    elif hrtype == "Video":
                        screen.append("<video style='display: none;' class='image video' data-dbcol='"+item["name"]+"'></video>")
                elif item["type"] == "geopoint":
                    # NO DBCOL!
                    screen.append("<button class='geopoint' onClick='doAction({dbcol: \""+item["name"]+"\", type: \"geopoint\"}, \"org.opendatakit.survey.activities.GeoPointActivity\", makeIntent(survey, \"org.opendatakit.survey.activities.GeoPointActivity\"));' data-dbcol='"+item["name"]+"'>Record location</button>")
                    for suffix in ["latitude", "longitude", "altitude", "accuracy"]:
                        column_id = item["name"] + "_" + suffix
                        dbcol = "data-dbcol=\""+column_id+"\"";
                        attrs = " ".join([dbcol, required, calculation, hint, constraint, constraint_message])
                        screen.append("<br />")
                        screen.append("<label for='"+column_id+"'>"+suffix[0].upper() + suffix[1:] +": </label>")
                        screen.append("<input type=\"text\" disabled=true id='"+column_id+"' " + _class + attrs + " />")
                elif item["type"] == "geopoint":
                    screen.append("<button class='geopoint' onClick='doAction({dbcol: \""+item["name"]+"\", type: \"geopoint\"}, \"com.google.zxing.client.android.SCAN\", {});' data-dbcol='"+item["name"]+"'>Scan barcode</button>")
                    screen.append("<br />")
                    screen.append("<input type=\"text\" disabled=true id='"+column_id+"' " + _class + attrs + " />")
                elif item["type"] in ["linegraph", "bargraph", "piechart"]:
                    screen.append("TODO")
                elif item["type"] == "integer":
                    screen.append("<input type=\"number\" data-validate=\"integer\" " + attrs + _class + " />")
                    #defaults[item["name"]] = 0.0;
                elif item["type"] == "number" or item["type"] == "decimal":
                    screen.append("<input type=\"number\" step=\"any\" data-validate=\"double\" " + attrs + _class + " />")
                    #defaults[item["name"]] = 0;
                elif item["type"] in ["select_multiple", "select_multiple_inline"]:
                    screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-multiple "+wrapped_class+"\"" + attrs + "></div>")
                    #defaults[item["name"]] = []
                elif item["type"] in ["select_one", "select_one_grid"]:
                    screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-one "+wrapped_class+"\"" + attrs + "></div>")
                elif item["type"] == "select_one_with_other":
                    screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-one-with-other "+wrapped_class+"\"" + attrs + "></div>")
                elif item["type"] == "select_one_dropdown":
                    screen.append("<select data-values-list=\""+item["values_list"]+"\"")
                    if "choice_filter" in item:
                        screen.append(" data-choice-filter=\""+item["choice_filter"]+"\"")
                    screen.append(attrs + _class + "></select>")
                elif item["type"] == "acknowledge":
                    screen.append("<select data-values-list=\"_yesno\" " + attrs + _class + "></select>")
                elif item["type"] == "date":
                    has_dates = True;
                    screen.append("<span " + attrs + "class=\"date "+wrapped_class+"\">" )
                    screen.append("<select data-values-list=\"_year\"></select>")
                    screen.append(" / ")
                    screen.append("<select data-values-list=\"_month\"></select>")
                    screen.append(" / ")
                    screen.append("<select data-values-list=\"_day\"></select>")
                    screen.append("</span>")
                    #defaults[item["name"]] = "1970-01-01" + "T00:00:00.000000000";
                elif item["type"] == "assign":
                    # The only one that's not a prompt
                    assigns.append("<span class=\"assign\" "+attrs+"></span>")
                else:
                    print("bad type " + item["type"]); die()
                # prevent an empty screen for pages with only assigns on them
                if len(screen) > 0:
                    screen.append("<br /><br />")
                if len(rules) > 0:
                    for rule in rules:
                        screen.append("</span>")
        if len(screen) > 0: screens.append("".join(screen));
        screens[-1] += "".join(assigns)

        queries = "[]";
        choices = "[]"
        if "queries" in formDef["xlsx"]:
            for query in formDef["xlsx"]["queries"]:
                if query["query_type"] == "linked_table":
                    query["yanked_col"] = utils.yank_instance_col(query["linked_table_id"], query["linked_form_id"])
            queries = json.dumps(formDef["xlsx"]["queries"]);
        if "choices" in formDef["xlsx"]:
            choices = json.dumps(formDef["xlsx"]["choices"]);
        basehtml = """
<!doctype html>
""" + utils.warning + """
<html>
<head>
    <style>
    input {
        font-size: 16px;
    }
    body {
        margin: 0 0 0 0;
        font-family: Roboto;
        /*font-size: 120%;*/
    }
    #odk-toolbar {
        padding: 8px 8px 8px 8px;
        width: calc(100% - 16px);
        font-size: 150%;
        min-height: 40px;
    }
    #odk-container {
        padding: 8px 5% 8px 5%;
    }
    #back, #cancel {
        float: left;
    }
    
    #next, #finalize {
        float: right;
    }
    input[type="number"], input[type="text"] {
        /*border-radius: 3px; */
        /*border-type: inset;*/ /* ugly */
        /*display: block;*/
        /*height: 34px;*/
        padding: 6px 6px;
        color: #333;
        margin-left: 8px;
        line-height: 1.4;
        color: #555;
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    button {
        border-color: #ccc;
        padding: 10px 16px;
        line-height: 1.333;
        border-radius: 6px;
        border-style: solid;
        background-color: #eee;
        border-width: 1px;
    }
    label, input[type="radio"] {
        padding-top: 5px;
        padding-bottom: 5px;
        display: inline-block;
    }
    .select-one > div:not(:first-child), .select-multiple > div:not(:first-child), .select-one-with-other > div:not(:first-child) {
        border-top: 1px solid grey;
    }
    .select-one, .select-multiple, .select-one-with-other {
        border: 1px solid grey;
        border-radius: 10px;
        min-width: 50%;
        background-color: lightgrey;
    }
    </style>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <!--
        <meta content='width=device-width; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;' name='viewport' />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    -->
    <title>OpenDataKit Common Javascript Framework</title>
    <script type="text/javascript" src="../../formgen_common.js"></script>
    <script type="text/javascript" src="../../../../system/js/odkCommon.js"></script>
    <script type="text/javascript" src="../../../../system/js/odkData.js"></script>
    <script type="text/javascript" src="../../../../system/libs/underscore.1.8.3.js"></script> <!-- development zips -->
    <!--
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.5.1/underscore-min.js"></script>
    -->
    <noscript>This page requires javascript and a Chrome or WebKit browser</noscript>
    <script>
var screens = """ + json.dumps(screens) + """;
var choices = """ + choices + """;
var queries = """ + queries + """;
var table_id = '""" + table + """';
//var defaults = """ + json.dumps("""defaults""") + """
var has_dates = """ + ("true" if has_dates else "false") + """
var row_id = "";
var opened_for_edit = false;
var row_data = {};
var S4 = function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
}
var newGuid = function newGuid() {
    return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
}

var selected = function selected(id, value) {
    if (id == null) {
        return value == null || value.length == 0;
    }
    if (id.indexOf("[") == 0) {
        try {
            id = jsonParse(id);
            for (var i = 0; i < id.length; i++) {
                if (id[i] == value) return true;
            }
        } catch (e) {
            // keep going
        }
    }
    return id == value
}
var screen_data = function screen_data(id) {
    var elems = document.getElementsByClassName("prompt");
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].getAttribute("data-dbcol") == id) {
            if (elems[i].tagName == "INPUT") {
                if (elems[i].value.trim().length == 0) {
                    return null;
                }
                if (elems[i].getAttribute("data-validate") == "integer" || elems[i].getAttribute("data-validate") == "double") {
                    return Number(elems[i].value);
                }
                return elems[i].value.trim();
            } else if (elems[i].tagName == "SELECT") {
                if (elems[i].selectedOptions.length > 0) {
                    return elems[i].selectedOptions[0].value.trim();
                }
                return "";
            } else if (elems[i].classList.contains("select-multiple")) {
                var result = [];
                var subs = elems[i].getElementsByTagName("input");
                for (var j = 0; j < subs.length; j++) {
                    if (subs[j].checked) {
                        result = result.concat(subs[j].value.trim());
                    }
                }
                return JSON.stringify(result);
            } else if (elems[i].classList.contains("select-one") || elems[i].classList.contains("select-one-with-other")) {
                var subs = elems[i].getElementsByTagName("input");
                for (var j = 0; j < subs.length; j++) {
                    if (subs[j].checked) {
                        if (subs[j].value.trim() == "_other") {
                            return document.getElementById(elems[i].getAttribute("data-dbcol") + "_" + "_other" + "_tag").value;
                        } else {
                            return subs[j].value.trim();
                        }
                    }
                }
                return null;
            } else if (elems[i].classList.contains("date")) {
                var fields = elems[i].getElementsByTagName("select");
                var total = [0, 0, 0];
                for (var j = 0; j < fields.length; j++) {
                    var field = fields[j]; // the select element for day, month or year
                    if (field.selectedOptions[0] == undefined) {
                        total[j] = j == 0 ? "0000" : "00";
                    } else {
                        total[j] = field.selectedOptions[0].value.trim();
                    }
                }
                // fields on the screen are in the order YYYY/MM/DD
                // but return here as YYYY-MM-DDT00:00:00.000000000 for storage in the database
                var pad = odkCommon.padWithLeadingZeros
                return pad(total[0], 4) + "-" + pad(total[1], 2) + "-" + pad(total[2], 2) + "T00:00:00.000000000";
            } else {
                alert("Unknown prompt type!");
                return "ERROR";
            }
        }
    }
}
var data = function data(id) {
    return row_data[id];
}
var survey = "org.opendatakit.survey"
var global_screen_idx = -1;
var do_xhr = function do_xhr(choice_id, filename, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var all = []
            var s = this.responseText.split("\\n")
            var cols = s[0].split(",");
            var s = s.slice(1);
            for (var i = 0; i < s.length; i++) {
                var cs = s[i].split(",");
                var choice = {};
                var valid = false;
                for (var j = 0; j < cols.length; j++) {
                    // Strip quotes, not really parsing it correctly
                    if (cols[j][0] = '"' && cols[j][cols[j].length - 1] == '"') {
                        cols[j] = cols[j].substr(1, cols[j].length - 2);
                    }
                    if (j >= cs.length) break;
                    if (cs[j][0] = '"' && cs[j][cs[j].length - 1] == '"') {
                        cs[j] = cs[j].substr(1, cs[j].length - 2);
                    }
                    cols[j] = cols[j].trim().replace("\\r", "");
                    var this_col = cs[j].trim().replace("\\r", "");
                    if (cols[j].length > 0 && this_col.length > 0) {
                        choice[cols[j]] = this_col
                        valid = true;
                    }
                }
                if (valid) {
                    all = all.concat(choice);
                }
            }
            try {
                var context = all
                var new_choices = eval(callback);
                for (var i = 0; i < new_choices.length; i++) {
                    new_choices[i]["choice_list_name"] = choice_id;
                    new_choices[i]["notranslate"] = "fake";
                }
                //console.log(new_choices);
                choices = choices.concat(new_choices);
            } catch (e) {
                // ignore
                console.log(e);
            }
            update(0);
        }
    };
    xhr.open("GET", filename, true);
    xhr.send();
}
var get_choices = function get_choices(which, not_first_time) {
    // first thing in the returned array is a boolean, true if the results are all there, false if they will be added to choices later
    var found = false;
    // TODO HANDLE CHOICE_FILTER !!
    var result = [false];
    for (var j = 0; j < choices.length; j++) {
        if (choices[j].choice_list_name == which) {
            // concat on a list will merge them
            result = result.concat(0);
            var displayed = choices[j].display;
            if (choices[j].notranslate == undefined) {
                displayed = display(choices[j].display)
            } else {
                displayed = fake_translate(choices[j].display);
                //console.log("Translation skipped for " + displayed)
            }
            result[result.length - 1] = [choices[j].data_value, displayed];
            result[0] = true; // we found at least one thing
        }
    }
    if (result.length > 1) return result;
    if (not_first_time) return [false];
    for (var j = 0; j < queries.length; j++) {
        if (queries[j].query_name == which) {
            found = true;
            if (queries[j].query_type == "linked_table") {
                start_get_rows(which, queries[j]);
                return [false];
            }
            if (queries[j].query_type == "csv") {
                var filename = queries[j].uri.replace('"', "").replace('"', "");
                do_xhr(which, filename, queries[j].callback);
                return [false]
            }
            return [false, ["ERROR", "Unknown query type " + queries[j].query_type]]
        }
    }
}
var start_get_rows = function start_get_rows(which, query) {
    var sql = "SELECT * FROM " + query.linked_table_id;
    if (query.selection) {
        sql = sql.concat(" WHERE " + query.selection + " ");
    }
    var selectionArgs = [];
    if (query.selectionArgs) {
        try {
            selectionArgs = jsonParse(query.selectionArgs);
        } catch (e) {
            alert("Failed to start cross-table query: " + e);
            console.log(e);
            return;
        }
    }
    odkData.arbitraryQuery(query.linked_table_id, sql, selectionArgs, 1000, 0, function success_callback(d) {
        for (var i = 0; i < d.getCount(); i++) {
            choices = choices.concat(0);
            // var val = d.resultObj.data[i][16]
            //console.log(query.yanked_col);
            var text = d.getData(i, query.yanked_col);
            var val = d.getData(i, "_id")
            choices[choices.length - 1] = {"choice_list_name": which, "data_value": val, "display": text, notranslate: true};
            //console.log(choices[choices.length - 1]);
        }
        update(0);
    }, function failure_callback() {
        alert("Unexpected failure");
    });
}
var populate_choices = function populate_choices(selects, callback) {
    for (var i = 0; i < selects.length; i++) {
        var select = selects[i];
        if (select.getAttribute("data-populated") == "done") {
            continue;
        }
        var stuffs = null;
        var which = select.getAttribute("data-values-list");
        if (select.getAttribute("data-populated") == "loading") {
            stuffs = get_choices(which, true);
        } else {
            stuffs = get_choices(which, false);
        }
        if (stuffs[0]) {
            select.setAttribute("data-populated", "done");
        } else {
            select.setAttribute("data-populated", "loading");
        }
        stuffs = stuffs.slice(1);
        callback(stuffs, select);
    }
}
var changeElement = function changeElement(elem, newdata) {
    if (elem.getAttribute("data-populated") == "loading") {
        setTimeout(100, function(){changeElement(elem, newdata)})
        return true;
    }

    if (elem.tagName == "INPUT") {
        elem.value = newdata;
    } else if (elem.tagName == "SELECT") {
        if (typeof(newdata) == "boolean") {
            // for acknowledges
            newdata = newdata.toString();
        }
        if (newdata != null) {
            newdata = newdata.trim();
        }
        if (newdata == null || newdata.trim().length == 0) {
            // we won't be able to find null in the options list
            return false;
        }
        var options = elem.options;
        var index = -1;
        for (var i = 0; i < options.length; i++) {
            var val = options[i].value
            if (val != null) val = val.trim()
            if (val == newdata || (newdata == "1" && val == "true") || (newdata == "0" && val == "false")) {
                index = i;
                break;
            }
        }
        if (index == -1) {
            // !!! THIS IS BAD !!!
            console.log("Couldn't set selected option for " + elem.getAttribute("data-dbcol"))
        }
        elem.selectedIndex = index;
    } else if (elem.classList.contains("select-multiple")) {
        if (!newdata || newdata.length == 0) {
            newdata = [];
        } else {
            newdata = jsonParse(newdata);
            for (var k = 0; k < newdata.length; k++) {
                newdata[k] = newdata[k].trim();
            }
        }
        var children = elem.getElementsByTagName("input");
        for (var k = 0; k < children.length; k++) {
            if (newdata.indexOf(children[k].value.trim()) >= 0) {
                children[k].checked = true;
            }
        }
    } else if (elem.classList.contains("select-one") || elem.classList.contains("select-one-with-other")) {
        var children = elem.getElementsByTagName("input");
        var found = false;
        for (var k = 0; k < children.length; k++) {
            if (newdata == children[k].value) {
                children[k].checked = true;
                found = true;
            }
            if (newdata == null) { // if we're setting this field to null, uncheck everything
                children[k].checked = false;
            }
        }
        if (!found && elem.classList.contains("select-one-with-other")) {
            document.getElementById(elem.getAttribute("data-dbcol") + "_" + "_other" + "_tag").value = newdata;
            document.getElementById(elem.getAttribute("data-dbcol") + "_" + "_other").checked = true;
        }
    } else if (elem.classList.contains("date")) {
        var total = ["-1", "-1", "-1"]
        if (newdata != null) {
            total = newdata.split("-"); // total is now [YYYY, MM, DD plus some garbage]? I actually have no idea
        }
        total[2] = total[2].split("T")[0]; // should now be [YYYY, MM, DD]
        var fields = elem.getElementsByTagName("select");
        for (var i = 0; i < fields.length; i++) {
            total[i] = Number(total[i]).toString(); // "06" -> "6"
            var field = fields[i]; // the select element for day, month or year
            changeElement(field, total[i]);
        }
    } else {
        alert("This shouldn't be possible, don't know how to update screen column " + elem.getAttribute("data-dbcol"));
    }
    return false;
}
var toArray = function toArray(i) {
    return Array.prototype.slice.call(i, 0);
}
var makeIntent = function makeIntent(package, activity, optional_dbcol) {
    var i = {action: "android.intent.action.MAIN", componentPackage: package, componentActivity: activity, extras: {tableId: table_id, instanceId: row_id}};
    //i.extras.uriFragmentNewFileBase: "opendatakit-macro(uriFragmentNewInstanceFile)";
    if (optional_dbcol != undefined && optional_dbcol != null) {
        // This will fail when making a new selection with a SQLiteError - android.database.sqlite.SQLiteConstraintException: column _data is not unique (code 19)
        // column _data is set to /storage/emulated/0/opendatakit/default/data/tables/:table_id/instances/:row_id/:db_col.jpg
        // so just pass a new uuid instead
        //i.extras["uriFragmentNewFileBase"] = optional_dbcol;
        i.extras["uriFragmentNewFileBase"] = newGuid();
    }
    return i;
}
var noop = true;
var updateOrInsert = function updateOrInsert() {
    if (!row_exists) {
        odkData.addRow(table_id, row_data, row_id, function(d) {
            row_exists = true;
        }, function(d) {
            if (d.indexOf("ActionNotAuthorizedException") >= 0) {
                alert("ActionNotAuthorizedException")
            }
            if (d.indexOf("is already present in table") >= 0) {
                row_exists = true;
                updateOrInsert();
                return;
            }
            console.log("Unexpected error on ADD row");
            noop = d;
            if (!noop) noop = true;
        });
    } else {
        odkData.updateRow(table_id, row_data, row_id, function(){}, function() {
            alert("Unexpected failure to save row");
            console.log(arguments);
        });
    }
    // null -> will prompt to finish making changes on opening a tool
    // INCOMPLETE -> saved incomplete, can resume editing later but won't be sync'd (?)
    var setTo = "INCOMPLETE"
    // var setTo = null;
    // Escape the LIMIT 1
    odkData.arbitraryQuery(table_id, "UPDATE " + table_id + " SET _savepoint_type = ? WHERE _id = ?;--", [setTo, row_id], 1000, 0, function success_callback(d) {
        console.log("Set _savepoint_type to "+setTo+" successfully");
    }, function failure(d) {
        alert("Error saving row: " + d);
    });
}
var update = function update(delta) {
    console.log("Update called " + delta);
    // If we failed to load the data from the database in the first place,
    if (noop) {
        var error = "An error occured while loading the page. ";
        if (noop !== true) {
            error = error.concat(noop);
        }
        document.getElementById("odk-container").innerHTML = error;
        return;
    }
    // DOACTION RESULT LOGIC
    while (true) {
        var a = odkCommon.viewFirstQueuedAction();
        if (a == null) {
            break;
        } else {
            console.log(a);
            console.log(a.jsonValue);
            console.log(a.jsonValue.result);
            var s = a["dispatchStruct"];
            if (s != undefined && s != null && s.type != undefined) {
                if (s.type == "geopoint") {
                    if (a.jsonValue.status == 0) {
                        alert("Error, location providers are disabled.")
                    } else {
                        var suffixes = ["latitude", "longitude", "altitude", "accuracy"];
                        for (var i = 0; i < suffixes.length; i++) {
                            var suffix = suffixes[i];
                            var shp_result = screen_has_prompt(s.dbcol + "_" + suffix)
                            // Returned via intent extras, one double for each suffix with the same suffix names I use here
                            if (shp_result[0]) {
                                changeElement(shp_result[1], a.jsonValue.result[suffix]);
                            } else {
                                row_data[s.dbcol + "_" + suffix] = a.jsonValue.result[suffix];
                            }
                        }
                    }
                } else if (s.type == "image") {
                    if (a.jsonValue.status == 0) {
                        // cancelled
                    } else if (a.jsonValue.result != undefined) {
                        var suffixes = ["uriFragment", "contentType"];
                        for (var i = 0; i < suffixes.length; i++) {
                            var suffix = suffixes[i];
                            if (a.jsonValue.result[suffix] == undefined) continue;
                            var shp_result = screen_has_prompt(s.dbcol + "_" + suffix);
                            // Returned via intent extras, one double for each suffix with the same suffix names I use here
                            if (shp_result[0]) {
                                changeElement(shp_result[1], a.jsonValue.result[suffix]);
                            } else {
                                row_data[s.dbcol + "_" + suffix] = a.jsonValue.result[suffix];
                            }
                        }
                    } else {
                        console.log("No result in result object!");
                    }
                } else if (s.type == "barcode") { // TOTALLY UNTESTED
                    if (a.jsonValue.status == 0) {
                        // cancelled
                    } else if (a.jsonValue.result != undefined) {
                        var suffixes = ["uriFragment", "contentType"];
                        var shp_result = screen_has_prompt(s.dbcol);
                        if (shp_result[0]) {
                            changeElement(shp_result[1], a.jsonValue.result.SCAN_RESULT_BYTES);
                        } else {
                            row_data[s.dbcol] = a.jsonValue.result.SCAN_RESULT_BYTES;
                        }
                    } else {
                        console.log("No result in result object!");
                    }
                } else {
                    alert("Unknown type in dispach struct!")
                }
            }
            odkCommon.removeFirstQueuedAction();
        }
    }
    // EVENT LISTENER LOGIC
    var elems = toArray(document.getElementsByTagName("select")).concat(toArray(document.getElementsByTagName("input")));
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].getAttribute("data-has_event_listener") == "1") {
            continue;
        }
        elems[i].addEventListener("blur", function() { update(0); });
        if (elems[i].tagName == "SELECT") {
            elems[i].addEventListener("change", function() { update(0); });
        }
        elems[i].setAttribute("data-has_event_listener", "1");
    }

    // TRANSLATION LOGIC
    var elems = document.getElementsByClassName("translate");
    var len = elems.length;
    for (var i = 0; i < len; i++) {
        var text = elems[0].innerText;
        try {
            var json = jsonParse(text);
            elems[0].outerHTML = display(json);
        } catch (e) {
            console.log(e)
            elems[0].outerHTML = "Error translating " + text; 
        }
    }

    // SET UP SELECT ONE, SELECT MULTIPLE AVAILABLE CHOICES LOGIC
    populate_choices(document.getElementsByTagName("select"), function(stuffs, select) {
        for (var j = 0; j < stuffs.length; j++) {
            var elem = document.createElement("option")
            elem.setAttribute("value", stuffs[j][0]);
            elem.innerHTML = stuffs[j][1];
            select.appendChild(elem);
        }
    });
    populate_choices(document.getElementsByClassName("select-multiple"), function(stuffs, select) {
        for (var j = 0; j < stuffs.length; j++) {
            var id = select.getAttribute("data-dbcol") + "_" + stuffs[j][0];
            var elem = document.createElement("div")
            //elem.classList.add("option")
            var inner = document.createElement("input")
            inner.type = "checkbox";
            inner.setAttribute("value", stuffs[j][0]);
            inner.setAttribute("id", id);
            inner.setAttribute("name", select.getAttribute("data-dbcol"));
            inner.addEventListener("change", function() {update(0);});
            elem.appendChild(inner);
            var label = document.createElement("label");
            label.setAttribute("for", id);
            var n = document.createElement("span");
            n.style.width = "100%";
            n.innerHTML = stuffs[j][1];
            label.appendChild(n);
            label.id = id + "_tag";
            elem.appendChild(label);
            //elem.appendChild(document.createElement("br"));
            select.appendChild(elem);
            label.style.width = (elem.clientWidth - inner.clientWidth - 10).toString() + "px"
        }
    });
    var pop_choices_for_select_one = function(stuffs, select) {
        for (var j = 0; j < stuffs.length; j++) {
            var id = select.getAttribute("data-dbcol") + "_" + stuffs[j][0];
            var elem = document.createElement("div")
            //elem.classList.add("option")
            var inner = document.createElement("input")
            inner.type = "radio";
            inner.setAttribute("value", stuffs[j][0]);
            inner.setAttribute("id", id);
            inner.setAttribute("name", select.getAttribute("data-dbcol"));
            inner.addEventListener("change", function() {update(0);});
            elem.appendChild(inner);
            var label = document.createElement("label");
            var n = document.createElement("span");
            n.style.width = "100%";
            n.innerHTML = stuffs[j][1];
            label.appendChild(n);
            label.setAttribute("for", id);
            label.id = id + "_tag";
            elem.appendChild(label);
            //elem.appendChild(document.createElement("br"));
            select.appendChild(elem);
            label.style.width = (elem.clientWidth - inner.clientWidth - 10).toString() + "px"
        }
    };
    populate_choices(document.getElementsByClassName("select-one-with-other"), function(stuffs, select) {
        pop_choices_for_select_one(stuffs, select);

        var elem = document.createElement("div")
        //elem.classList.add("option")
        var id = select.getAttribute("data-dbcol") + "_" + "_other";
        var radio = document.createElement("input")
        radio.type = "radio";
        radio.setAttribute("value", "_other");
        radio.id = id
        radio.setAttribute("name", select.getAttribute("data-dbcol"));
        radio.addEventListener("change", function() {update(0);});
        textbox = document.createElement("input");
        textbox.type = "text";
        textbox.id = id + "_tag"
        textbox.setAttribute("name", select.getAttribute("data-dbcol"));
        textbox.addEventListener("blur", function() {document.getElementById(select.getAttribute("data-dbcol") + "__other").checked = true; update(0);});
        elem.appendChild(radio);
        elem.appendChild(textbox);
        select.appendChild(elem);
    });
    populate_choices(document.getElementsByClassName("select-one"), pop_choices_for_select_one);

    // DATA UPDATE LOGIC
    var num_updated = 0;
    var to_set = [];
    var elems = document.getElementsByClassName("prompt");
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var col = elem.getAttribute("data-dbcol");
        if (elem.getAttribute("data-populated") == "loading") {
            // if it's a select one or select multiple, and it doesn't have any choices yet, don't touch it
            continue;
        } else if (elem.getAttribute("data-data_populated") == "loading") {
            continue;
        } else if (elem.getAttribute("data-data_populated") == "done") {
            var newdata = screen_data(col);
            if (newdata != null) {
                newdata = newdata.toString();
            }
            if (row_data[col] != newdata) {
                num_updated++;
                // fix acknowledges
                if (newdata == "true") newdata = "1";
                if (newdata == "false") newdata = "0";
                row_data[col] = newdata;
                console.log("Updating database value for " + col + " to screen value " + row_data[col]);
            }
        } else {
            to_set = to_set.concat(col);
        }
    }
    if (to_set.length > 0) {
        for (var i = 0; i < to_set.length; i++) {
            var col = to_set[i];
            var elems = document.getElementsByClassName("prompt");
            for (var j = 0; j < elems.length; j++) {
                var elem = elems[j];
                if (elem.getAttribute("data-dbcol") == col) {
                    if (typeof(row_data[col]) == "boolean") {
                        // this fixes acknowledges, otherwise we would changeElement to true (boolean) then screen_data would return true (string)
                        row_data[col] = row_data[col].toString();
                    }
                    console.log("Updating " + col + " to saved value " + row_data[col]);
                    var loading = changeElement(elem, row_data[col]);
                    var sdat = screen_data(col);
                    if (sdat == "true") sdat = "1"
                    if (sdat == "false") sdat = "0"
                    if (row_data[col] !== null && sdat != row_data[col] && !loading && screen_has_prompt(col)[0]) {
                        // This can happen when the database says a select one should be set to "M55" or something, but that's not one of the possible options.
                        //noop = "Unexpected failure to set screen value of " + col + ". Tried to set it to " + row_data[col] + " but it came out as " + sdat;
                        console.log("Unexpected failure to set screen value of " + col + ". Tried to set it to " + row_data[col] + " ("+typeof(row_data[col])+") but it came out as " + sdat + " ("+typeof(sdat)+")");
                        row_data[col] = sdat;
                        //update(0);
                        //return;
                    } else {
                        elem.setAttribute("data-data_populated", "done");
                    }
                }
            }
        }
        //update(0);
        //return;
    }


    // VALIDATION LOGIC
    var valid = true;
    var elems = document.getElementsByClassName("constraint-message");
    for (var i = 0; i < elems.length; i++) {
        elems[i].outerHTML = ""; // remove the element
    }
    var elems = document.getElementsByClassName("prompt");
    for (var i = 0; i < elems.length; i++) {
        var this_valid = true;
        var col = elems[i].getAttribute("data-dbcol");
        if (elems[i].getAttribute("data-validate") == "double") {
            var num = Number(elems[i].value);
            if (isNaN(num) || !elems[i].validity.valid) {
                this_valid = false;
            }
        }
        if (elems[i].getAttribute("data-validate") == "integer") {
            var num = Number(elems[i].value);
            if (isNaN(num) || (num | 0) != num || !elems[i].validity.valid) {
                this_valid = false;
            }
        }
        if (elems[i].getAttribute("data-required") != null) {
            var entered = screen_data(col);
            if (entered == null || entered.length == 0) {
                this_valid = false;
            }
        }
        if (elems[i].getAttribute("data-constraint") != null) {
            if (!eval(elems[i].getAttribute("data-constraint"))) {
                this_valid = false;
            }
        }
        if (!this_valid) {
            valid = false;
            elems[i].style.backgroundColor = "pink";
            if (elems[i].getAttribute("data-constraint_message") != null) {
                var message = document.createElement("div");
                message.classList.add("constraint-message");
                message.innerText = display(jsonParse(elems[i].getAttribute("data-constraint_message")));
                elems[i].parentNode.insertBefore(message, elems[i].nextSibling);
            }
        } else {
            elems[i].style.backgroundColor = ""; // Default
        }
    }
    if (!valid) {
        document.getElementById("next").disabled = true;
        document.getElementById("back").disabled = true;
        document.getElementById("finalize").disabled = true;
        delta = 0;
    }

    // DATABASE UPDATE
    if (num_updated > 0 && valid) {
        updateOrInsert()
    }

    // IF STATEMENTS LOGIC
    var spans = document.getElementsByClassName("validate");
    for (var i = 0; i < spans.length; i++) {
        var rule = spans[i].getAttribute("data-validate-rule");
        if (eval(rule)) {
            spans[i].style.display = "block";
        } else {
            spans[i].style.display = "none";
        }
    }

    // DISPLAY IMAGES
    var elems = document.getElementsByClassName("image");
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var dbcol = elem.getAttribute("data-dbcol") + "_uriFragment";
        if (data(dbcol) == null || data(dbcol) == undefined || data(dbcol).trim().length == 0) {
            continue;
        }
        var newsrc = odkCommon.getRowFileAsUrl(table_id, row_id, data(dbcol));
        if (elem.src != newsrc) {
            if (elem.classList.contains("audio")) {
                elem.innerHTML = "";
                var newsource = document.createElement("source");
                newsource.src = newsrc
                elem.appendChild(newsource)
            } else if (elem.classList.contains("video")) {
                elem.innerHTML = "";
                var newsource = document.createElement("source");
                newsource.src = newsrc
                elem.appendChild(newsource)
            } else {
                elem.src = newsrc;
            }
            elem.style.display = "block";
        }
    }

    // ENABLE/DISABLE NEXT/BACK/FINALIZE BUTTON LOGIC
    if (!valid) return; // buttons have already been disabled
    global_screen_idx += delta;
    odkCommon.setSessionVariable(table_id + ":" + row_id + ":global_screen_idx", global_screen_idx);
    if (global_screen_idx <= 0) {
        global_screen_idx = 0;
        document.getElementById("back").disabled = true;
    } else {
        document.getElementById("back").disabled = false;
    }
    if (global_screen_idx >= screens.length - 1) {
        global_screen_idx = screens.length - 1;
        document.getElementById("next").disabled = true;
        document.getElementById("next").style.display = "none";
        document.getElementById("finalize").style.display = "block";
        document.getElementById("finalize").disabled = false;
    } else {
        document.getElementById("finalize").style.display = "none";
        document.getElementById("next").disabled = false;
        document.getElementById("next").style.display = "block";
    }
    if (delta != 0) {
        var container = document.getElementById("odk-container");
        container.innerHTML = screens[global_screen_idx];
        update(0);
    }
}
var screen_has_prompt = function screen_has_prompt(id) {
    var elems = document.getElementsByClassName("prompt");
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].getAttribute("data-dbcol") == id) {
            return [true, elems[i]];
        }
    }
    return [false, null];
}
var finalize = function finalize() {  
    // ASSIGN LOGIC
    // ASSUMES ALL THE ASSIGNS ARE ON THE LAST PAGE!
    var elems = document.getElementsByClassName("assign");
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var col = elem.getAttribute("data-dbcol");
        if (row_data[col] == "") {
            row_data[col] = eval(elem.getAttribute("data-calculation")).toString()
            //num_updated++;
        }
    }
    odkCommon.setSessionVariable(table_id + ":" + row_id + ":global_screen_idx", 0);
    update(0);
    // Escape the LIMIT 1
    odkData.arbitraryQuery(table_id, "UPDATE " + table_id + " SET _savepoint_type = ? WHERE _id = ?;--", ["COMPLETE", row_id], 1000, 0, function success_callback(d) {
        console.log("Set _savepoint_type to COMPLETE successfully");
        page_back();
    }, function failure(d) {
        // TODO
        alert(d);
        if (d) {
            noop = d
        } else {
            noop = true
        }
    });
};
var cancel = function cancel() {
    if (!opened_for_edit) {
        if (row_exists) {
            if (confirm("Are you sure? All entered data will be deleted.")) {
                // Escape the LIMIT 1
                odkData.arbitraryQuery(table_id, "DELETE FROM " + table_id + " WHERE _id = ?;--", [row_id], 100, 0, function() {
                    page_back();
                }, function(err) {
                    alert("Unexpected error deleting row " + JSON.stringify(err));
                    page_back();
                });
            }
        } else {
            page_back();
        }
    } else {
        page_back();
    }
}
var page_back = function page_back() {
    //window.history.back();
    odkCommon.closeWindow(-1, null);
}
var row_exists = true;
var doAction = function doAction(dStruct, act, intent) {
    var result = odkCommon.doAction(dStruct, act, intent);
    if (result == "OK" || result == "IGNORED") {
        return;
    }
    alert("Error launching " + act + ": " + result);
}
var ol = function onLoad() {
    if (has_dates) {
        // won't be localized, so we can set display to i instead of {text: i}
        for (var i = 1; i <= 31; i++) {
            choices = choices.concat({choice_list_name: "_day", data_value: i.toString(), display: i.toString(), notranslate: true})
        }
        for (var i = 1; i <= 12; i++) {
            choices = choices.concat({choice_list_name: "_month", data_value: i.toString(), display: i.toString(), notranslate: true})
        }
        for (var i = 2020; i >= 1940; i--) {
            choices = choices.concat({choice_list_name: "_year", data_value: i.toString(), display: i.toString(), notranslate: true})
        }
    }
    choices = choices.concat({"choice_list_name": "_yesno", "data_value": "true", "display": {"text": "yes"}});
    choices = choices.concat({"choice_list_name": "_yesno", "data_value": "false", "display": {"text": "no"}});
    row_id = window.location.hash.substr(1);
    if (row_id.length == 0) {
        row_id = newGuid();
        alert("No row id in uri, beginning new instance with id " + row_id);
        opened_for_edit = false;
    }
    global_screen_idx = Number(odkCommon.getSessionVariable(table_id + ":" + row_id + ":global_screen_idx"));
    if (isNaN(global_screen_idx)) {
        global_screen_idx = 0;
    }
    global_screen_idx -= 1;
    odkData.getRows(table_id, row_id, function success(d) {
        try {
            var cols = d.getColumns();
            var generator = function(i) {
                //if (defaults[i] != undefined) {
                    //return defaults[i];
                //}
                return null;
            }
            if (d.getCount() == 0) {
                row_exists = false;
                opened_for_edit = false;
            } else {
                row_exists = true;
                opened_for_edit = true;
                generator = function(i) { return d.getData(0, cols[i]); }
            }
            for (var i = 0; i < cols.length; i++) {
                if (cols[i][0] != "_") {
                    row_data[cols[i]] = generator(i);
                }
            }
            var cancel = document.getElementById('cancel');
            if (opened_for_edit) {
                cancel.innerText = "Save incomplete";
            } else {
                cancel.innerText = "Cancel and delete row"
            }
            cancel.disabled = false;
            //console.log(row_data);
            noop = false;
        } catch (e) {
            noop = e.toString();
        }
        update(1);
        odkCommon.registerListener(function doaction_listener() {
            var a = odkCommon.viewFirstQueuedAction();
            if (a != null) {
                console.log(a);
                odkCommon.removeFirstQueuedAction();
                update(0);
            }
        });
    }, function failure(d) {
        console.log(d);
        noop = d;
        if (!d) noop = true;
        update(1); // Display the error
    });
};
    </script>
</head>
<body onLoad='ol();'>
    <div class="odk-toolbar" id="odk-toolbar">
        <button id='cancel' onClick='cancel()' disabled=true>Loading...</button>
        <button id='back' onClick='update(-1)'>Back</button>
        <button id='next' onClick='update(1)'>Next</button>
        <button id='finalize' style='display: none;' onClick='finalize()'>Finalize</button>
    </div>
    <div class="odk-container" id="odk-container">Please wait...</div>
    <!--
        <script type="text/javascript" data-main="survey/js/main" src="libs/require.2.3.2.js"></script>
    -->
</body>
</html>
        """
        if os.path.exists(table):
            subprocess.check_call(["rm", "-rf", table])
        os.mkdir(table);
        open(table + "/index.html", "w").write(basehtml)
        for f in glob.glob("/home/niles/Documents/odk/app-designer/app/config/tables/" + table + "/forms/" + table + "/*"):
            fn = os.path.basename(f);
            if fn in ["formDef.json", "properties.csv", "definition.csv", "customStyles.css"] or fn.endswith(".xls") or fn.endswith(".xlsx"):
                #print("Not copying file " + f)
                continue
            #subprocess.check_call(["cp", "-rv", f, table + "/" + fn])
            src = "/sdcard/opendatakit/default/config/tables/" + table + "/forms/" + table + "/" + fn
            dest_folder = "/sdcard/opendatakit/default/config/assets/formgen/" + table + "/"
            dest = dest_folder + fn
            subprocess.check_call(["adb", "shell", "mkdir", "-p", dest_folder])
            #print("Linking " + src + " to " + dest)
            #subprocess.check_call(["adb", "shell", "ln", "-s", src, dest])
            subprocess.check_call(["adb", "shell", "cp", "-rv", src, dest])
    except:
        if failed:
            print("Skipping " + table)
        else:
            print("Unexpected exception in " + table)
            print(traceback.format_exc())
            sys.exit(1)

