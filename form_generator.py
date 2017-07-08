import json, sys, os, glob, traceback, subprocess
# TODO items
# Must have before release!
#   - Store dates in database correctly
# 	- Some css would be nice
# 	- A way to view the data, a list with add/edit buttons
#   - Save row without finalizing it or provide defaults that won't cause number format exceptions
# Other things not implemented
# 	- Text notification with validation fail message
# 	- Real translation
# 	- bargraph, linegraph, piechart
# 	- image (EASY!)
# 	- goto (EASY!)
# 	- sections (could be hard)
# 	- geopoint (could be hard)
# 	- send_sms
# 	- read_only_image
# 	- datetime, time
# 	- user_branch
# 	- signature
# 	- barcode
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
#       - Javascript based (i.e. "selected(data('acknowledged') === 'yes')" or "data('age') > 18", etc...)
#       - Required field constraints
#       - Won't let you next, back, finalize or save to the database until validation passes for the current screen
#   - Basic data types, text/string, integer, number/decimal
#   - Select one, select one dropdown (actually implemented as very different widgets)
#   - Select multiple, select multiple inline
#   - Select one grid, select one with other
#   - acknowledge (alias for select_one with yes/no options)
#   - date
#   - assign, with javascript expressions in xlsx, evaluated at start of form
#   - save on prompt value change but also on next/back/finalize
#   - Auto generate row id and insert new row if no row id given in hash
#   - Automatically load prompt values from database abd save new values to database only when changed on the screen
def die():
    global failed
    failed = True
    raise Exception()
def falsey(r):
    r = str(r).strip().lower();
    if r.endswith(";"):
        r = r[:-1].strip()
    return r == "0" or r == "false";
def yank_instance_col(table, form):
    formDef = json.loads(open("/home/niles/Documents/odk/app-designer/app/config/tables/" + table + "/forms/" + form + "/formDef.json", "r").read())
    try:
        return [x for x in formDef["xlsx"]["settings"] if x["setting_name"] == "instance_name"][0]["value"]
    except:
        pass
    try:
        return formDef["xlsx"]["specification"]["settings"]["instance_name"]["value"]
    except:
        print("ERROR could not yank instance col for " + table + "/" + form)
        return "_id"
tables = [os.path.basename(x) for x in glob.glob("/home/niles/Documents/odk/app-designer/app/config/tables/*")]
for table in tables:
    global failed
    failed = False
    try:
        formDef = json.loads(open("/home/niles/Documents/odk/app-designer/app/config/tables/" + table + "/forms/" + table + "/formDef.json", "r").read())
        screens = []
        rules = []
        screen = []
        assigns = []
        for item in formDef["xlsx"]["survey"]:
            #print(item)
            if "clause" in item:
                clause = item["clause"].split("//")[0].strip();
                if clause == "begin screen":
                    if len(screen) > 0:
                        screens.append("".join(screen))
                    screen = []
                elif clause == "end screen":
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
                if "constraint_message" in item:
                    constraint_message = "data-constraint_message=\"" + item["constraint_message"] + "\""
                attrs = " " + " ".join([dbcol, required, calculation, hint, constraint, constraint_message]) + " "
                wrapped_class = "prompt"
                _class = " class=\"prompt\" "
                if item["type"] == "note":
                    pass
                elif item["type"] == "text" or item["type"] == "string":
                    screen.append("<input type=\"text\" " + attrs + _class + " />")
                elif item["type"] in ["linegraph", "bargraph", "geopoint"]:
                    screen.append("TODO")
                elif item["type"] == "integer":
                    screen.append("<input type=\"number\" " + attrs + _class + " />")
                elif item["type"] == "number" or item["type"] == "decimal":
                    screen.append("<input type=\"text\" data-validate=\"double\" " + attrs + _class + " />")
                elif item["type"] == "image":
                    screen.append("TODO")
                elif item["type"] == "select_multiple" or item["type"] == "select_multiple_inline":
                    screen.append("<br /><span style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-multiple "+wrapped_class+"\"" + attrs + "></span>")
                elif item["type"] in ["select_one", "select_one_grid", "select_one_with_other"]:
                    screen.append("<br /><span style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-one "+wrapped_class+"\"" + attrs + "></span>")
                elif item["type"] == "select_one_dropdown":
                    screen.append("<select data-values-list=\""+item["values_list"]+"\"")
                    if "choice_filter" in item:
                        screen.append(" data-choice-filter=\""+item["choice_filter"]+"\"")
                    screen.append(attrs + _class + "></select>")
                elif item["type"] == "acknowledge":
                    screen.append("<select data-values-list=\"_yesno\" " + attrs + _class + "></select>")
                elif item["type"] == "date":
                    screen.append("<span " + attrs + "class=\"date "+wrapped_class+"\">" )
                    screen.append("<select data-values-list=\"_year\"></select>")
                    screen.append(" / ")
                    screen.append("<select data-values-list=\"_month\"></select>")
                    screen.append(" / ")
                    screen.append("<select data-values-list=\"_day\"></select>")
                    screen.append("</span>")
                elif item["type"] == "assign":
                    # The only one that's not a prompt
                    assigns.append("<span class=\"assign\" "+attrs+"></span>")
                else:
                    print("bad type " + item["type"]); die()
                screen.append("<br /><br />")
                if len(rules) > 0:
                    for rule in rules:
                        screen.append("</span>")
        if len(screen) > 0: screens.append("".join(screen));
        screens[0] += "".join(assigns)

        queries = "[]";
        choices = "[]"
        if "queries" in formDef["xlsx"]:
            for query in formDef["xlsx"]["queries"]:
                if query["query_type"] == "linked_table":
                    query["yanked_col"] = yank_instance_col(query["linked_table_id"], query["linked_form_id"])
            queries = json.dumps(formDef["xlsx"]["queries"]);
        if "choices" in formDef["xlsx"]:
            choices = json.dumps(formDef["xlsx"]["choices"]);
        basehtml = """
<!doctype html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <!-- <meta content='width=device-width; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;' name='viewport' /> -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenDataKit Common Javascript Framework</title>
    <script type="text/javascript" src="../../../../system/js/odkCommon.js"></script>
    <script type="text/javascript" src="../../../../system/js/odkData.js"></script>
    <!-- One of these will work -->
    <script type="text/javascript" src="../../../../system/libs/underscore.1.4.4.js"></script> <!-- cold-chain zips -->
    <script type="text/javascript" src="../../../../system/libs/underscore.1.8.3.js"></script> <!-- development zips -->
    <!--
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.5.1/underscore-min.js"></script>
    -->
    <noscript>This page requires javascript and a Chrome or WebKit browser</noscript>
    <script>
        var display = function display(thing) {
            var res = ""
            if (thing.text !== undefined) {
                res += thing.text; // TODO localize
            }
            if (thing.image != undefined) {
                res += "<img src='" + thing.image + "'>";
            }
            if (thing.audio != undefined) {
                res += "<audio controls='controls'><source src='" + thing.audio + "' /></audio>";
            }
            if (res.length > 0) return res;
            if (thing.prompt !== undefined) {
                return display(thing.prompt);
            }
            if (thing.title !== undefined) {
                return display(thing.title);
            }
            return "Couldn't translate " + JSON.stringify(thing);
        }
        var screens = """ + json.dumps(screens) + """;
        var choices = """ + choices + """;
        var queries = """ + queries + """;
        var table_id = '""" + table + """';
        var row_id = "";
        var row_data = {};
        var S4 = function S4() {
            return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
        }
        var newGuid = function newGuid() {
            return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
        }

        var selected = function selected(id, value) {
            if (typeof(id) == typeof([])) {
                for (var i = 0; i < id.length; i++) {
                    if (id[i] == value) return true;
                }
            }
            return id == value
        }
        var screen_data = function screen_data(id) {
            var elems = document.getElementsByClassName("prompt");
            for (var i = 0; i < elems.length; i++) {
                if (elems[i].getAttribute("data-dbcol") == id) {
                    if (elems[i].tagName == "INPUT") {
                        if (elems[i].type == "number") {
                            return Number(elems[i].value);
                        }
                        return elems[i].value
                    } else if (elems[i].tagName == "SELECT") {
                        if (elems[i].selectedOptions.length > 0) {
                            return elems[i].selectedOptions[0].value;
                        }
                        return "";
                    } else if (elems[i].classList.contains("select-multiple") || elems[i].classList.contains("select-one")) {
                        var result = [];
                        var subs = elems[i].getElementsByTagName("input");
                        for (var j = 0; j < subs.length; j++) {
                            // TODO will only return first element selected in a select multiple
                            if (subs[j].checked) {
                                result = result.concat(subs[j].value);
                            }
                        }
                        return result;
                    } else if (elems[i].classList.contains("date")) {
                        var fields = elems[i].getElementsByTagName("select");
                        var total = [0, 0, 0];
                        for (var j = 0; j < fields.length; j++) {
                            var field = fields[j]; // the select element for day, month or year
                            total[j] = field.selectedOptions[0].value;
                        }
                        // fields on the screen are in the order YYYY/MM/DD
                        // but return here as YYYY-MM-DDT00:00:00.000000000 for storage in the database
                        return total[0] + "-" + total[1] + "-" + total[2] + "T00:00:00.000000000";
                    } else {
                        alert("Unknown prompt type!");
                        return "ERROR";
                    }
                }
            }
            return false;
        }
        var data = function data(id) {
            return row_data[id];
        }
        var jsonParse = function jsonParse(text) {
            try {
                text = text.replace(/\\'/g, '"');
                return JSON.parse(text);
            } catch (e) {
                console.log(e);
                return text;
            }
        }
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
                            cols[j] = cols[j].trim();
                            if (cols[j].length > 0) {
                                choice[cols[j]] = cs[j];
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
                    result[result.length - 1] = [choices[j].data_value, display(choices[j].display)];
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
                    return [false, ["TODO", "Unknown query type"]]
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
                // TODO wrap in try/catch
                selectionArgs = jsonParse(query.selectionArgs);
            }
            odkData.arbitraryQuery(query.linked_table_id, sql, selectionArgs, 1000, 0, function success_callback(d) {
                for (var i = 0; i < d.getCount(); i++) {
                    choices = choices.concat(0);
                    // TODO TODO TODO
                    // TODO 16 is a magic number, not specified in formDef
                    // var val = d.resultObj.data[i][16]
                    //console.log(query.yanked_col);
                    var text = d.getData(i, query.yanked_col);
                    var val = d.getData(i, "_id")
                    choices[choices.length - 1] = {"choice_list_name": which, "data_value": val, "display": {"text": text}};
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
            if (elem.tagName == "INPUT") {
                elem.value = newdata;
            } else if (elem.tagName == "SELECT") {
                var options = elem.options;
                var index = -1;
                for (var i = 0; i < options.length; i++) {
                    if (options[i].value == newdata) {
                        index = i;
                        break;
                    }
                }
                if (index == -1) {
                    // !!!
                    console.log("Couldn't figure out selected option for " + elem.getAttribute("data-dbcol"))
                }
                elem.selectedIndex = index;
            } else if (elem.classList.contains("select-multiple")) {
                if (!newdata || newdata.length == 0) {
                    newdata = [];
                } else {
                    newdata = jsonParse(newdata);
                }
                var children = elem.getElementsByTagName("input");
                for (var k = 0; k < children.length; k++) {
                    if (newdata.contains(children[k].value)) {
                        children[k].checked = true;
                    }
                }
            } else if (elem.classList.contains("select-one")) {
                var children = elem.getElementsByTagName("input");
                for (var k = 0; k < children.length; k++) {
                    if (newdata == children[k].value) {
                        children[k].checked = true;
                    }
                }
            } else if (elem.classList.contains("date")) {
                var fields = elem.getElementsByTagName("select");
                var total = newdata.split("-"); // total is now [YYYY, MM, DD plus some garbage]? I actually have no idea
                total[2] = total[2].split("T")[0]; // should now be [YYYY, MM, DD]
                for (var i = 0; i < fields.length; i++) {
                    var field = fields[i]; // the select element for day, month or year
                    changeElement(field, total[i]);
                }
            } else {
                alert("This shouldn't be possible, don't know how to update screen column " + elem.getAttribute("data-dbcol"));
            }
        }
        var toArray = function toArray(i) {
            return Array.prototype.slice.call(i, 0);
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
            // INCOMPLETE -> saved incomplete, can resume editing later but won't be sync'd
            // var setTo = "INCOMPLETE"
            var setTo = null;
            odkData.arbitraryQuery(table_id, "UPDATE " + table_id + " SET _savepoint_type = ? WHERE row_id = ?", [set_to, row_id], 1000, 0, function success_callback(d) {
                console.log("Set _savepoint_type to "+set_to+" successfully");
            }, function failure(d) {
                // TODO
                alert(d);
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
            var lock = false;
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
                    var elem = document.createElement("span")
                    var inner = document.createElement("input")
                    inner.type = "checkbox";
                    inner.setAttribute("value", stuffs[j][0]);
                    inner.setAttribute("id", id);
                    inner.setAttribute("name", select.getAttribute("data-dbcol"));
                    inner.addEventListener("change", function() {update(0);});
                    elem.appendChild(inner);
                    var label = document.createElement("label");
                    var n = document.createElement("span");
                    n.innerHTML = stuffs[j][1];
                    label.appendChild(n);
                    label.setAttribute("for", id);
                    elem.appendChild(label);
                    elem.appendChild(document.createElement("br"));
                    select.appendChild(elem);
                }
            });
            populate_choices(document.getElementsByClassName("select-one"), function(stuffs, select) {
                for (var j = 0; j < stuffs.length; j++) {
                    var id = select.getAttribute("data-dbcol") + "_" + stuffs[j][0];
                    var elem = document.createElement("span")
                    var inner = document.createElement("input")
                    inner.type = "radio";
                    inner.setAttribute("value", stuffs[j][0]);
                    inner.setAttribute("id", id);
                    inner.setAttribute("name", select.getAttribute("data-dbcol"));
                    inner.addEventListener("change", function() {update(0);});
                    elem.appendChild(inner);
                    var label = document.createElement("label");
                    var n = document.createElement("span");
                    n.innerHTML = stuffs[j][1];
                    label.appendChild(n);
                    label.setAttribute("for", id);
                    elem.appendChild(label);
                    elem.appendChild(document.createElement("br"));
                    select.appendChild(elem);
                }
            });

            // VALIDATION LOGIC
            var valid = true;
            var elems = document.getElementsByTagName("input");
            for (var i = 0; i < elems.length; i++) {
                var this_valid = true;
                if (elems[i].getAttribute("data-validate") == "double") {
                    var num = Number(elems[i].value);
                    if (isNaN(num)) {
                        this_valid = false;
                    }
                }
                if (elems[i].getAttribute("data-validate") == "integer") {
                    var num = Number(elems[i].value);
                    if (isNaN(num) || num | 0 != num) {
                        this_valid = false;
                    }
                }
                if (elems[i].getAttribute("data-required") != null) {
                    if (elems[i].value.length == 0) {
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
                        // TODO
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
                lock = true;
            }

            // DATABASE SAVE/LOAD LOGIC
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
                    if (row_data[col] != newdata.toString()) {
                        num_updated++;
                        row_data[col] = newdata.toString();
                        console.log("Updating database value for " + col + " to screen value " + row_data[col]);
                    }
                } else {
                    to_set = to_set.concat(col);
                }
            }
            // ASSIGN LOGIC
            var elems = document.getElementsByClassName("assign");
            for (var i = 0; i < elems.length; i++) {
                var elem = elems[i];
                var col = elem.getAttribute("data-dbcol");
                if (row_data[col] == "") {
                    row_data[col] = eval(elem.getAttribute("data-calculation")).toString()
                    num_updated++;
                }
            }
            if (to_set.length > 0) {
                for (var i = 0; i < to_set.length; i++) {
                    var col = to_set[i];
                    var elems = document.getElementsByClassName("prompt");
                    for (var j = 0; j < elems.length; j++) {
                        var elem = elems[j];
                        if (elem.getAttribute("data-dbcol") == col) {
                            console.log("Updating " + col + " to saved value " + row_data[col]);
                            changeElement(elem, row_data[col]);
                            if (screen_data(col) != row_data[col]) {
                                noop = "Unexpected failure to set screen value of " + col + ". Tried to set it to " + row_data[col] + " but it came out as " + screen_data(col);
                                update(0);
                                return;
                            } else {
                                elem.setAttribute("data-data_populated", "done");
                            }
                        }
                    }
                }
                update(0);
                return;
            }
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

            // ENABLE/DISABLE NEXT/BACK/FINALIZE BUTTON LOGIC
            if (lock) return;
            global_screen_idx += delta;
            if (global_screen_idx <= 0) {
                global_screen_idx = 0;
                document.getElementById("back").disabled = true;
            } else {
                document.getElementById("back").disabled = false;
            }
            if (global_screen_idx >= screens.length - 1) {
                global_screen_idx = screens.length - 1;
                document.getElementById("next").disabled = true;
                document.getElementById("finalize").style.display = "inline-block";
                document.getElementById("finalize").disabled = false;
            } else {
                document.getElementById("finalize").style.display = "none";
                document.getElementById("next").disabled = false;
            }
            if (delta != 0) {
                var container = document.getElementById("odk-container");
                container.innerHTML = screens[global_screen_idx];
                update(0);
            }
        }
        var finalize = function finalize() {  
            //row_data["_savepoint_type"] = "COMPLETE";
            odkData.arbitraryQuery(table_id, "UPDATE " + table_id + " SET _savepoint_type = ? WHERE row_id = ?", ["COMPLETE", row_id], 1000, 0, function success_callback(d) {
                console.log("Set _savepoint_type to COMPLETE successfully");
            }, function failure(d) {
                // TODO
                alert(d);
            });
            update(0);
            window.history.back();
        };
        var row_exists = true;
        var ol = function onLoad() {
            document.getElementById("odk-toolbar").innerHTML = "<button id='back' onClick='update(-1)'>Back</button><button id='next' onClick='update(1)'>Next</button><button id='finalize' style='display: none;' onClick='finalize()'>Finalize</button>"
            var str = function str(i) { return Number(i).toString(); };
            for (var i = 1; i <= 31; i++) {
                choices = choices.concat({"choice_list_name": "_day", "data_value": str(i), "display": {"text": str(i)}})
            }
            for (var i = 1; i <= 12; i++) {
                choices = choices.concat({"choice_list_name": "_month", "data_value": str(i), "display": {"text": str(i)}})
            }
            for (var i = 2020; i >= 1940; i--) {
                choices = choices.concat({"choice_list_name": "_year", "data_value": str(i), "display": {"text": str(i)}})
            }
            choices = choices.concat({"choice_list_name": "_yesno", "data_value": "true", "display": {"text": "yes"}});
            choices = choices.concat({"choice_list_name": "_yesno", "data_value": "false", "display": {"text": "no"}});
            row_id = window.location.hash.substr(1);
            if (row_id.length == 0) {
                row_id = newGuid();
                alert("No row id in uri, beginning new instance with id " + row_id);
            }
            odkData.getRows(table_id, row_id, function success(d) {
                try {
                    var cols = d.getColumns();
                    var generator = function(i) { return ""; }
                    if (d.getCount() == 0) {
                        row_exists = false;
                    } else {
                        row_exists = true;
                        generator = function(i) { return d.getData(0, cols[i]); }
                    }
                    for (var i = 0; i < cols.length; i++) {
                        if (cols[i][0] != "_") {
                            row_data[cols[i]] = generator(i);
                        }
                    }
                    //row_data["_savepoint_type"] = "INCOMPLETE";
                    noop = false;
                } catch (e) {
                    noop = e.toString();
                }
                update(1);
            }, function failure(d) {
                noop = d;
                if (!d) noop = true;
                update(1); // Display the error
            });
        };
    </script>
</head>
<body onLoad='ol();'>
    <div class="odk-toolbar" id="odk-toolbar"></div>
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
            output = subprocess.check_output(["adb", "shell", "ln", "-s", "/sdcard/opendatakit/default/config/tables/" + table + "/forms/" + table + "/" + fn, "/sdcard/opendatakit/default/config/assets/formgen/" + table + "/" + fn])
            if "no such file or directory" in output.decode('utf-8').lower():
                print("Failed to link " + f + " - " + output.decode("utf-8"))
                print("Did you adbpush after switch app-designer branches?")
                raise Exception();
    except:
        if failed:
            print("Skipping " + table)
        else:
            print("Unexpected exception in " + table)
            print(traceback.format_exc())
            sys.exit(1)

