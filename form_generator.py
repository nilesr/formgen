import json, sys, os, glob, traceback, subprocess, random
# TODO items
# Must have before release!
#   - query filters
#   - More filtering options in generate_table (or new pages)
#   - Display sync state in table, sync state and savepoint type in detail
#   - Better documentation for generate_table, generate_detail
# Other things not implemented
#   - take picture is broken - SURVEY BUG
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

# Throws an exception but sets skipping to true so we don't actually stop, we just skip the table and move on
def die():
    global skipped
    skipped = True
    raise Exception()
# This function tries to optimize "if" clauses, if the user wrote something like false or 0 in the clause, then don't bother loading it at all. This saves us from some pretty expensive queries in one of the cold chain tables
def falsey(r):
    r = str(r).strip().lower();
    if r.endswith(";"):
        r = r[:-1].strip()
    return r == "0" or r == "false";
# like S4 in formgen_common.js, just makes four random 0-9a-f digits, used in gensym
def genpart(): return hex(random.randint(0, 2**(8*2)))[2:]
# returns a random guid, used for translation tokens
def gensym(): return genpart() + genpart() + "-4" + genpart()[1:] + "-" + genpart() + "-" + genpart() + genpart() + genpart()
def generate_all(utils, filenames):
    if not os.path.exists("formgen"): os.mkdir("formgen");
    tables = utils.get_tables()
    for table in tables:
        global skipped
        skipped = False
        try:
            formDef = json.loads(open(utils.appdesigner + "/app/config/tables/" + table + "/forms/" + table + "/formDef.json", "r").read())
            screens = []
            rules = []
            screen = []
            #assigns = []
            # Used for translations, we json dump the translations because they're json objects.
            # In the past they were stringified and put in a span with the class translate, but html tags inside
            # translations were broken because the DOM molests them and I can't accurately retrieve the text I put in.
            # The new system keeps them always stored as javascript objects, which is what display takes anyways.
            tokens = {}
            # Small optimization, won't add all the choices for dates if there are no date prompts in the form
            has_dates = False
            for item in formDef["xlsx"]["survey"]:
                #print(item)
                if "clause" in item:
                    clause = item["clause"].split("//")[0].strip();
                    # Sometimes people write begin screen without putting end screen, sometimes they do
                    # the opposite, so just don't trust the user and insert a screen break no matter what if
                    # there's a begin or end screen clause. If there's two in a row it won't generate an empty
                    # screen because we check if the current screen's length is ok first.
                    if clause in ["begin screen", "end screen"]:
                        if len(screen) > 0:
                            screens.append("".join(screen))
                        screen = []
                    # Add the rule to tokens and add the token to the rules list on an if clause
                    elif clause == "if":
                        token = gensym()
                        # inserted as a string, json.dumps() and JSON.parse() will make sure it gets passed through unmolested
                        tokens[token] = item["condition"]
                        rules.insert(0, token)
                    # remove it on "end if"
                    elif clause == "end if":
                        rules = rules[1:]
                    # ignore empty clauses, will continue to check "type"
                    elif clause == "": pass
                    else:
                        print("bad clause " + item["clause"]); die()
                    continue
                # All prompts have a type
                if "type" in item:
                    # If we have any rules, wrapp the entire prompt in a series of spans, one for each rule
                    # update() will set style.visibility to "none" or "block" on those spans depending on whether the rule matches or not
                    if len(rules) > 0:
                        continue_out = False
                        for rule in rules:
                            if falsey(rule):
                                continue_out = True
                                break
                            screen.append("<span style='display: none;' class='validate' data-validate-rule=\"" + str(rule) + "\">")
                        if continue_out:
                            continue
                    if "display" in item:
                        token = str(gensym())
                        tokens[token] = item["display"]
                        screen.append("<span class='translate'>" + token + "</span> ")
                    dbcol = ""
                    if "name" in item:
                        dbcol = "data-dbcol=\""+item["name"]+"\"";
                    required = ""
                    calculation = ""
                    hint = ""
                    constraint = ""
                    constraint_message = ""
                    choice_filter = ""
                    # calculations, used basically only for assigns. Pulled from tokens and evaled in update
                    if "calculation" in item:
                        token = gensym()
                        tokens[token] = str(item["calculation"])
                        calculation = "data-calculation=\"" + token + "\"";
                    # If there's a hint, put the hint object in tokens and set the data-placeholder attribute.
                    # Update will go through, remove the data-placeholder attribute and set the placeholder (no data- prefix) attribute
                    # to the result of translating the token
                    if "display" in item and type(item["display"]) == type({}) and "hint" in item["display"]:
                        token = gensym()
                        tokens[token] = item["display"]["hint"]
                        hint = "data-placeholder=\""+token+"\""
                    # set if it's a required field
                    # if we already have a placeholder (that might be translated), don't change it, otherwise set
                    # placeholder to Required field
                    if "required" in item:
                        required = "data-required=\"required\" "
                        if len(hint) == 0: required += "placeholder=\"Required field\"";
                    # constraint, like "data('weight') < 20", stuff like that
                    if "constraint" in item:
                        token = gensym()
                        tokens[token] = item["constraint"]
                        constraint = "data-constraint=\"" + token + "\""
                    # if we have a message to display to the user if the constraint isn't met, pass it via tokens
                    if "display" in item and "constraint_message" in item["display"]:
                        token = gensym()
                        tokens[token] = item["display"]["constraint_message"]
                        constraint_message = "data-constraint_message=\"" + token + "\""
                    # Some eval'd javascript to filter which choices will be added as possible choices to a select one, select multiple, etc...
                    # For example in cold chain I think there's a csv query that gets a list of countries, and a previous prompt was the
                    # continent, and the filter is something like "context.continent == data('coninent')", then the only things you can
                    # select from the dropdown are countries on that continent
                    # Not actually implemented yet in update - TODO
                    if "choice_filter" in item:
                        token = gensym()
                        tokens[token] = item["choice_filter"]
                        choice_filter = " data-choice-filter=\""+token+"\""

                    # All the attributes that any element append to the screen should have
                    attrs = " " + " ".join([dbcol, required, calculation, hint, constraint, constraint_message, choice_filter]) + " "
                    # All prompts must have the class prompt. It can either just put "<div " + _class + ">their stuff</div>", or if it needs
                    # its own classes, it can use wrapped_class like "<div class='some-prompt-type " + wrapped_class + "'>stuff</div>"
                    wrapped_class = "prompt"
                    _class = " class=\"" + wrapped_class + "\" "
                    # Notes are only for the creator of the survey, shouldn't be shown to the user
                    if item["type"] == "note":
                        pass
                    # string/text elements are easy
                    elif item["type"] == "text" or item["type"] == "string":
                        screen.append("<input type=\"text\" " + attrs + _class + " />")
                    # a complicated one, a doaction
                    elif item["type"] in ["image", "audio", "video"]:
                        # hrtype is really just the type but with the first letter uppercased, so "Image", "Audio" or "Video"
                        hrtype = item["type"][0].upper() + item["type"][1:]
                        for action in ["Choose", "Capture"]:
                            # like MediaChooseImageActivity or MediaCaptureVideoActivity
                            act = "org.opendatakit.survey.activities.Media" + action + hrtype + "Activity"
                            # Button with text "Choose Picture" or "Take Picture" or "Choose Video", or etc...
                            screen.append("<button onClick='doAction({dbcol: \""+item["name"]+"\", type: \"image\"}, \""+act+"\", makeIntent(survey, \""+act+"\", \""+item["name"]+"\"));' data-dbcol='"+item["name"]+"'>" + action + " " + ("Picture" if hrtype == "Image" else hrtype) + "</button>")
                        # We will make two input elements, one with data-dbcol set to ":dbcol_uriFragment" and one with it set to ":dbcol_contentType"
                        # Both will be disabled so the user can't edit them. Neither will have a label, and the contentType one will be hidden so
                        # the user only sees the uri one 
                        for suffix in ["uriFragment", "contentType"]:
                            column_id = item["name"] + "_" + suffix
                            dbcol = "data-dbcol=\""+column_id+"\"";
                            attrs = " ".join([dbcol, required, calculation, hint, constraint, constraint_message])
                            # hide contentType
                            if suffix == "contentType":
                                attrs += " style='display: none;' "
                            screen.append("<br />")
                            screen.append("<input type=\"text\" disabled=true id='"+column_id+"' " + _class + attrs + " />")
                        # Now add an element to preview what the user selected. Will have a source set in update()
                        if hrtype == "Image":
                            screen.append("<img style='display: none; width: 50%;' class='image' data-dbcol='"+item["name"]+"' />")
                        elif hrtype == "Audio":
                            screen.append("<audio style='display: none;' class='image audio' data-dbcol='"+item["name"]+"'></audio>")
                        elif hrtype == "Video":
                            screen.append("<video style='display: none;' class='image video' data-dbcol='"+item["name"]+"'></video>")
                    elif item["type"] == "geopoint":
                        screen.append("<button class='geopoint' onClick='doAction({dbcol: \""+item["name"]+"\", type: \"geopoint\"}, \"org.opendatakit.survey.activities.GeoPointActivity\", makeIntent(survey, \"org.opendatakit.survey.activities.GeoPointActivity\"));' data-dbcol='"+item["name"]+"'>Record location</button>")
                        # Will make four input fields, each with data-dbcol set to ":dbcol_:suffix" for these four suffixes
                        for suffix in ["latitude", "longitude", "altitude", "accuracy"]:
                            column_id = item["name"] + "_" + suffix
                            dbcol = "data-dbcol=\""+column_id+"\"";
                            attrs = " ".join([dbcol, required, calculation, hint, constraint, constraint_message])
                            screen.append("<br />")
                            screen.append("<label for='"+column_id+"'>"+suffix[0].upper() + suffix[1:] +": </label>")
                            screen.append("<input type=\"text\" disabled=true id='"+column_id+"' " + _class + attrs + " />")
                    # BARCODE COMPLETELY UNTESTED
                    elif item["type"] == "barcode":
                        screen.append("<button class='geopoint' onClick='doAction({dbcol: \""+item["name"]+"\", type: \"geopoint\"}, \"com.google.zxing.client.android.SCAN\", {});' data-dbcol='"+item["name"]+"'>Scan barcode</button>")
                        screen.append("<br />")
                        screen.append("<input type=\"text\" disabled=true id='"+item["name"]+"' " + _class + attrs + " />")
                    # TODO
                    elif item["type"] in ["linegraph", "bargraph", "piechart"]:
                        screen.append("TODO")
                    # Numbers are easy, and we can query input.validity to check if the user input a number correctly
                    elif item["type"] == "integer":
                        screen.append("<input type=\"number\" data-validate=\"integer\" " + attrs + _class + " />")
                    # Same as integer but allow values between whole numbers (step = any), instead of the default integer only
                    elif item["type"] == "number" or item["type"] == "decimal":
                        screen.append("<input type=\"number\" step=\"any\" data-validate=\"double\" " + attrs + _class + " />")
                    # Div element that will have checkbox elements with labels appended to it in update. Store the choices_list value, 
                    # which might be something already in the choices list, or possibly 
                    elif item["type"] in ["select_multiple", "select_multiple_inline"]:
                        screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-multiple "+wrapped_class+"\"" + attrs + "></div>")
                    # Same thing but with radio buttons instead of checkboxes
                    elif item["type"] in ["select_one", "select_one_grid"]:
                        screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-one "+wrapped_class+"\"" + attrs + "></div>")
                    # Same thing but an extra _other choice will be added, with a text box for the label
                    elif item["type"] == "select_one_with_other":
                        screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-one-with-other "+wrapped_class+"\"" + attrs + "></div>")
                    # an actual select element, will display as a dropdown menu and contents will be populated with option items
                    elif item["type"] == "select_one_dropdown":
                        screen.append("<select data-values-list=\""+item["values_list"]+"\"")
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
                        screen.append("<span class=\"assign\" "+attrs+"></span>")
                    else:
                        print("bad type " + item["type"]); die()
                    # prevent an empty screen for pages with only assigns on them
                    if len(screen) > 0:
                        screen.append("<br /><br />")
                    if len(rules) > 0:
                        for rule in rules:
                            screen.append("</span>")
            if len(screen) > 0: screens.append("".join(screen));
            #screens[-1] += "".join(assigns)

            # Copy queries and choices from the formdef if they exist
            queries = "[]"
            choices = "[]"
            if "queries" in formDef["xlsx"]:
                for query in formDef["xlsx"]["queries"]:
                    # Try and guess which column to use as the displayed text in the populated options, usually doesn't work and defaults to "_id"
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
        padding: 8px 5% 100px 5%;
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
    @media screen and (max-width: 480px) {
        .select-one, .select-multiple, .select-one-with-other {
            min-width: 100%;
        }
    }
    input[type="checkbox"], input[type="radio"] {
        position: absolute;
        margin-top: 9px;
        text-align: center;
        display: block;
    }
    label {
        width: 85%;
        padding-left: 15%;
    }

    </style>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <!--
        <meta content='width=device-width; initial-scale=1.0; maximum-scale=1.0; user-scalable=0;' name='viewport' />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    -->
    <title>OpenDataKit Common Javascript Framework</title>
    <!-- we will typically be at /default/config/assets/formgen/:table_id/index.html, paths are relative to that -->
    <script type="text/javascript" src="../../formgen_common.js"></script>
    <script type="text/javascript" src="../../../../system/js/odkCommon.js"></script>
    <script type="text/javascript" src="../../../../system/js/odkData.js"></script>
    <script type="text/javascript" src="../../../../system/libs/underscore.1.8.3.js"></script> <!-- development zips -->
    <!--
        was for testing in a web browser before I had odkData support added
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.5.1/underscore-min.js"></script>
    -->
    <noscript>This page requires javascript and a Chrome or WebKit browser</noscript>
    <script>
// Copy out screens, choices, queries, table id, tokens and has_dates from the python side
var screens = """ + json.dumps(screens) + """;
var choices = """ + choices + """;
var queries = """ + queries + """;
var table_id = '""" + table + """';
var tokens = """ + json.dumps(tokens) + """
var has_dates = """ + ("true" if has_dates else "false") + """

// keeps track of which row we're editing
var row_id = "";
// keeps track of whether we were opened to edit an existing row or add a new row, automatically determined
var opened_for_edit = false;
// Stores the entire row we're editing right now
var row_data = {};
// Holds whether the row exists or not yet, set in onLoad (`ol`)
var row_exists = true;

// Helper package for doActions, used in makeIntent
var survey = "org.opendatakit.survey"
// The index of the currently displayed screen in `screens`. 
// Initially set to -1 and the onLoad function (`ol`) will call update(1) to force displaying of the screen at index 0, whereas
// if we just started it at zero and called update(0) it wouldn't change the current screen data
var global_screen_idx = -1;

// noop is a magic and special variable, if noop is set to true then update() will refuse to do anything and display an error message
// Set to true initially and set to false in onLoad (`ol`) before it calls update()
var noop = true;


// Helper function for constraints, so people can write like "selected(data('color'), 'blue')" and it will return true/false 
var selected = function selected(value1, value2) {
    if (value1 == null) {
        return value2 == null || value2.length == 0;
    }
    // If value1 is the result of data() on a select_multiple, decode it and return true if value2 is one of the selected options
    if (value1.indexOf("[") == 0) {
        try {
            value1 = jsonParse(value1);
            for (var i = 0; i < value1.length; i++) {
                if (value1[i] == value2) return true;
            }
        } catch (e) {
            // keep going
        }
    }
    // otherwise just check if they're equal
    return value1 == value2
}
// Given a dbcol, try and pull the data currently in the prompt object on the screen.
// Checked in update(), and if it differs from row_data then update knows to go update the database with row_data now
var screen_data = function screen_data(id) {
    // This will throw an error if the requested prompt isn't on the screen
    var gsp_result = get_screen_prompt(id);
    if (!gsp_result[0]) {
        alert("Prompt for database column " + id + " not found on the screen! Will be stored in the database as null!") 
        return null;
    }
    var elem = get_screen_prompt(id)[1]
    // If it's a text input
    if (elem.tagName == "INPUT") {
        // IMPORTANT!!
        // If it's empty, the user left it blank, so return null. If we return an empty string, and the field is a
        // double or something, we'll get a "column has multiple datatypes" over the aidl interface and it will actually
        // break the rest of the Tables tool too, it will crash any time it tries to select all the rows in the table
        if (elem.value.trim().length == 0) {
            return null;
        }
        // If it's supposed to be a number/double, cast it to a number and return it. IMPORTANT - If it's an invalid number/double,
        // the code will never reach here. If it's not a valid Number, then element.value will return an empty string instead of 
        // the invalid stuff the user put in the textbox, and we will have returned null already. The way you check if there's really
        // nothing in the box versus if there's something in the box but it's not a valid number is by checking elem.validity, and that's
        // exactly what the validation function does
        if (elem.getAttribute("data-validate") == "integer" || elem.getAttribute("data-validate") == "double") {
            return Number(elem.value);
        }
        // Otherwise return the contents of the text box
        return elem.value.trim();
    } else if (elem.tagName == "SELECT") {
        // Dropdown menu, pretty simple
        if (elem.selectedOptions.length > 0) {
            return elem.selectedOptions[0].value.trim();
        }
        return "";
    } else if (elem.classList.contains("select-multiple")) {
        // for select multiple, accumulate everything the user checked in a list, then stringify it
        // we stringify it because whatever we return will be put into row_data and then from row_data into the database by update()
        // When update() encounters a select multiple element that has no data yet, it will attempt to populate it from the database
        // by calling changeElement, which will expect something that it can jsonParse
        var result = [];
        // Selects all the input elements that have our span as a parent, in this case all checkboxes
        var subs = elem.getElementsByTagName("input");
        for (var j = 0; j < subs.length; j++) {
            if (subs[j].checked) {
                result = result.concat(subs[j].value.trim());
            }
        }
        return JSON.stringify(result);
    } else if (elem.classList.contains("select-one") || elem.classList.contains("select-one-with-other")) {
        // For select one and select one with an "Other: " option as a text box
        // Selects all the input elements that have our span as a parent, in this case all radio buttons
        var subs = elem.getElementsByTagName("input");
        for (var j = 0; j < subs.length; j++) {
            if (subs[j].checked) {
                // If the selected radio button corrisponds to the "Other: " text field, grab the label text box and return its value
                // Otherwise, just return the value of the radio button
                if (subs[j].value.trim() == "_other") {
                    return document.getElementById(id + "_" + "_other" + "_tag").value;
                } else {
                    return subs[j].value.trim();
                }
            }
        }
        // No radio buttons checked? Just leave it as null in the database, that's what survey does
        return null;
    } else if (elem.classList.contains("date")) {
        // Dates are a little complicated, they're made up of three dropdown menus. 
        // First, grab the three dropdowns
        var fields = elem.getElementsByTagName("select");
        // This will be used to store the result once we've scraped all three dropdown menus
        var total = ["0", "0", "0"];
        // For each dropdown, update total
        for (var j = 0; j < fields.length; j++) {
            var field = fields[j]; // the select element for day, month or year
            if (field.selectedOptions[0] == undefined) {
                // If there's nothing, set to "0", will be padded with zeroes later
                total[j] = "0"
            } else {
                // But if there was a value to pull, put it in the right place in totals
                total[j] = field.selectedOptions[0].value.trim();
            }
        }
        // fields on the screen are in the order YYYY/MM/DD
        // return here as YYYY-MM-DDT00:00:00.000000000 for storage in the database, will need to pad things to the
        // right length, e.g. "6" -> "06"
        var pad = odkCommon.padWithLeadingZeros
        return pad(total[0], 4) + "-" + pad(total[1], 2) + "-" + pad(total[2], 2) + "T00:00:00.000000000";
    } else {
        // fuck
        alert("Unknown prompt type!");
        return "ERROR";
    }
}
// Helper function used by assigns, validation, if statements, etc...
// For example, if some questions should only appear if the survey taker is under 18, so one if statement
// might have the clause "data('age') < 18"
// or a prompt's response might only be valid if "data('color') == 'red'" if the only possible favorite color is red
// that exact example is used in default/complex_validate_test
var data = function data(id) {
    return row_data[id];
}
// This function is called in get_choices if the choices list for a particular prompt is a csv query AND the choices for that
// query haven't been populated yet
var do_csv_xhr = function do_csv_xhr(choice_id, filename, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Appends each row to this list
            var all = []
            // split by lines
            var s = this.responseText.split("\\n")
            // split the first line by a comma to extract a list of the headers in the csv
            var cols = s[0].split(",");
            // remove the headers line from the data
            var s = s.slice(1);
            // for all the other rows, parse them to an object and put the object in `all`
            for (var i = 0; i < s.length; i++) {
                // holds each of the cells in the current row
                var cs = s[i].split(",");
                // the object we'll put the things in
                var choice = {};
                var found_at_least_one = false;
                // For each cell in this row of the csv, set choice[column] = cell
                for (var j = 0; j < cols.length; j++) {
                    // Strip quotes, not really parsing it correctly
                    // I commented it out because I haven't tested it yet, and also we don't need it for the CSVs I'm parsing so far
                    /*
                    if (cols[j][0] = '"' && cols[j][cols[j].length - 1] == '"') {
                        cols[j] = cols[j].substr(1, cols[j].length - 2);
                    }
                    if (j >= cs.length) break;
                    if (cs[j][0] = '"' && cs[j][cs[j].length - 1] == '"') {
                        cs[j] = cs[j].substr(1, cs[j].length - 2);
                    }
                    */
                    // Trim out the column name and the cell
                    cols[j] = cols[j].trim().replace("\\r", "");
                    var this_col = cs[j].trim().replace("\\r", "");
                    // If there's no trailing comma or something weird, put it in choice
                    if (cols[j].length > 0 && this_col.length > 0) {
                        choice[cols[j]] = this_col
                        found_at_least_one = true;
                    }
                }
                // we don't want to add an empty object, that would generate a yucky "Error translating {}" in the dropdown menu or whatever it is
                if (found_at_least_one) {
                    // put choice in all
                    all = all.concat(choice);
                }
            }
            try {
                // the callback is specified in the xlsx and expects the list to be called "context". It also expects it to have a choice_list_name
                // set to the name of the query, and I add "notranslate" in there so it will be evaluated with fake_translate rather than
                // display, which is faster but doesn't localize. I can't imagine that the callback that the users wrote will handle
                // translating the items in the csv to other languages.
                var context = all
                var new_choices = eval(callback);
                for (var i = 0; i < new_choices.length; i++) {
                    new_choices[i]["choice_list_name"] = choice_id;
                    new_choices[i]["notranslate"] = true;
                }
                // Add every choice to the choices list, then call update() to populate the prompts on the screen with our newly-generated choices
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
// Called in update() to return a list of choices to put in a select one or select multiple (or select one dropdown or select one with other) prompt
// It returns a list, first thing in the returned list is a boolean, true if the results are all there, false if they will be added to choices later
// Everything after that is a pair of [real_value, translated_display_name], and all of those pairs are added to the on-screen prompt's options
// in update()
var get_choices = function get_choices(which, not_first_time, filter) {
    // TODO HANDLE CHOICE_FILTER !!
    // Default result - we didn't find anything so check again later
    var result = [false];
    // For each choice
    for (var j = 0; j < choices.length; j++) {
        // If the choice's "choice_list_name" is the name of the choice list we're called upon to return, add it to the result
        if (choices[j].choice_list_name == which) {
            // If there's no filter, add it. If there is a filter, add it only if the filter matches
            var filter_result = true;
            if (filter != null) {
                choice_item = choices[j] // used in the eval
                var data = screen_data // This is a disgusting hack
                filter_result = eval(tokens[filter])
            }
            if (filter_result) {
                // concat on a list will merge them
                result = result.concat(0);
                var displayed = choices[j].display;
                // If there's no "notranslate" key, translate it using display, otherwise fake translate it
                if (choices[j].notranslate == undefined) {
                    displayed = display(choices[j].display)
                } else {
                    displayed = fake_translate(choices[j].display);
                }
                result[result.length - 1] = [choices[j].data_value, displayed];
                result[0] = true; // we found at least one thing
            }
        }
    }
    // If we found choices, return them
    if (result.length > 1) return result;
    // If the csv xhr or cross table query is still in progress, return false and we'll be asked again later
    if (not_first_time) return [false];
    // Otherwise check queries
    for (var j = 0; j < queries.length; j++) {
        if (queries[j].query_name == which) {
            if (queries[j].query_type == "linked_table") {
                do_cross_table_query(which, queries[j]);
                // false to let update() know that more choices will be added, so we'll be called again later
                return [false];
            }
            // If it's a csv query, start do_csv_xhr
            if (queries[j].query_type == "csv") {
                // I don't know why I have to strip the filename, but I do
                var filename = queries[j].uri.replace(/"/g, "").replace(/'/g, "");
                do_csv_xhr(which, filename, queries[j].callback);
                return [false]
            }
            // Don't know that kind of query
            return [true, ["ERROR", "Unknown query type " + queries[j].query_type]]
        }
    }
    // Wasn't in choices or queries, don't know what to do, just leave it as empty
    return [true];
}
// function that performs a cross table query based on the query in the formdef. Puts all its
// results in the global `choices` list and calls update(0), which should call get_choices again which should
// now have choices to return in the global `choices` list
// `which` is the choice_list_id, query is the entire json object
var do_cross_table_query = function do_cross_table_query(which, query) {
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
    // Perform the requested query
    odkData.arbitraryQuery(query.linked_table_id, sql, selectionArgs, 1000, 0, function success_callback(d) {
        // On success, add everything to "choices" and call update(0)
        for (var i = 0; i < d.getCount(); i++) {
            // The raw value to get stored in the database is the id of the row in the other table
            var val = d.getData(i, "_id")
            // the display text is the value of the instance column for that row in the other table, but guessing
            // the instance column is unreliable and a lot of times query.yanked_col might just be "_id"
            var text = d.getData(i, query.yanked_col);
            // append the entire thing to choices
            choices = choices.concat(0);
            // notranslate: true so that we don't try and localize it, which would be slow and I doubt the column in the other
            // row has multiple translations anyways
            choices[choices.length - 1] = {"choice_list_name": which, "data_value": val, "display": text, notranslate: true};
        }
        // make update() call get_choices again now that we've added things to the global `choices` list
        update(0);
    }, function failure_callback() {
        alert("Unexpected failure");
    });
}
// Helper function called by update, detects if a prompt in the given list of prompts has had choices added to it yet,
// and if it hasn't it calls get_choices, and pass the result to the given callback which handles the dirty dom element adding stuff
// If get_choices returns [true, [...], [...], ...] with some choices, then set "populated" to done. Otherwise,
// if it returns [false], set "populated" to "loading". When we encounter an element, if it was "done", skip it, if it was "loading",
// give that information to get_choices, otherwise it must not have been populated yet so just call get_choices
var populate_choices = function populate_choices(selects, callback) {
    for (var i = 0; i < selects.length; i++) {
        var select = selects[i];
        // if it's already populated, skip it
        if (select.getAttribute("data-populated") == "done" && !select.hasAttribute("data-choice-filter")) {
            continue;
        }
        var stuffs = null;
        // pulls the choice_list_name from the prompt
        var which = select.getAttribute("data-values-list");
        var filter = null;
        var saved = screen_data(select.getAttribute("data-dbcol"))
        if (select.hasAttribute("data-choice-filter")) {
            filter = select.getAttribute("data-choice-filter")
            select.innerHTML = ""; // Remove all children
        }
        if (select.getAttribute("data-populated") == "loading") {
            stuffs = get_choices(which, true, filter);
        } else {
            stuffs = get_choices(which, false, filter);
        }
        // If we got results, set "done", otherwise it must have started a csv xhr or cross table query, so set "loading"
        if (stuffs[0]) {
            select.setAttribute("data-populated", "done");
        } else {
            select.setAttribute("data-populated", "loading");
        }
        // remove the boolean from the beginning of get_choices's result
        stuffs = stuffs.slice(1);
        // give the list of choices to set and the element to put them on to the callback
        callback(stuffs, select);
        if (filter != null &&  saved != null && saved != undefined) {
            changeElement(select, saved);
        }
    }
}
// This takes a prompt and tries to set the data on that prompt to to `newdata`
// Returns false if successful, or true if the prompt couldn't be set because
// it's still in the process of fetching choices from a csv or another table
var changeElement = function changeElement(elem, newdata) {
    // We know data-populated will be set because changeElement gets called in the database handling, which is
    // after the populate_choices calls in update()
    // If it's not populated yet, loop until it is.
    if (elem.getAttribute("data-populated") == "loading") {
        setTimeout(100, function(){
            changeElement(elem, newdata);
        });
        return true;
    }

    // If it's a text box, just set the value
    if (elem.tagName == "INPUT") {
        elem.value = newdata;
    } else if (elem.tagName == "SELECT") {
        // This handles regular old dropdown menus

        // fix for acknowledges
        if (typeof(newdata) == "boolean") {
            newdata = newdata.toString();
        }
        // trim the data
        if (newdata != null) {
            newdata = newdata.trim();
        }
        // we won't be able to find null in the options list
        if (newdata == null || newdata.length == 0) {
            return false;
        }
        // Get the list of options in the dropdown menu
        var options = elem.options;
        var index = -1;
        // Try and find the option in the dropdown menu where the option's value is what we're trying to set the dropdown menu to
        for (var i = 0; i < options.length; i++) {
            var val = options[i].value
            if (val != null) val = val.trim()
            // If it's sele
            if (val == newdata || (newdata == "1" && val == "true") || (newdata == "0" && val == "false")) {
                index = i;
                break;
            }
        }
        if (index == -1) {
            // !!! THIS IS BAD !!!
            console.log("Couldn't set selected option for " + elem.getAttribute("data-dbcol"))
        }
        // Set the selected option on the dropdown menu
        elem.selectedIndex = index;
    } else if (elem.classList.contains("select-multiple")) {
        // For select multiples, json parse what we're supposed to set the prompt to
        if (!newdata || newdata.length == 0) {
            newdata = [];
        } else {
            newdata = jsonParse(newdata);
            for (var k = 0; k < newdata.length; k++) {
                newdata[k] = newdata[k].trim();
            }
        }
        // then loop through the checkboxes and set checked to true if it's in newdata, false otherwise
        var children = elem.getElementsByTagName("input");
        for (var k = 0; k < children.length; k++) {
            if (newdata.indexOf(children[k].value.trim()) >= 0) {
                children[k].checked = true;
            } else {
                children[k].checked = false;
            }
        }
    } else if (elem.classList.contains("select-one") || elem.classList.contains("select-one-with-other")) {
        // For select one, select one with other, get all the radio buttons and if a radio button's value is equal to newdata, select it
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
        // If we didn't find any radio buttons to select and it's a select one with other, select the "Other: " radio button and set
        // the text box's value to newdata
        if (!found && elem.classList.contains("select-one-with-other") && newdata != null) {
            document.getElementById(elem.getAttribute("data-dbcol") + "_" + "_other" + "_tag").value = newdata;
            document.getElementById(elem.getAttribute("data-dbcol") + "_" + "_other").checked = true;
        }
    } else if (elem.classList.contains("date")) {
        // For dates, first extract the year month and date from newdata, then set the three subfields to that data in order
        var total = ["-1", "-1", "-1"]
        if (newdata != null) {
            total = newdata.split("-"); // total is now [YYYY, MM, DD plus some garbage]
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
    // remember, false means success
    return false;
}
// helper function
var toArray = function toArray(i) {
    return Array.prototype.slice.call(i, 0);
}
// Makes and returns an intent that can be used to launch the given component
// package is usually the `survey` variable and activity is something like "org.opendatakit.survey.activities.GeoPointActivity" or something
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
// Helper function used by update() whenever something on the screen has changed and we should put row_data in the database
// Also sets savepoint type to incomplete
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
// This is the big function that expects to be called every time there's a change.
// First argument is a number to be added to global_screen_idx, and if it's not zero, it will redraw the screen with the new page and call update(0)
// It handles putting the results of doactions onto the screen, setting event listeners on input and select elements, assigns, translations
// populating choices for select one dropdown, select one, select one with other and select multiple prompts, putting data from the screen
// into row_data if it was changed and setting the prompt value on the screen to the value from row_data if it hasn't been populated yet,
// inserting or updating this row in the database if anything new was changed in row_data, screen validation and displaying translated validation failure
// messages, and displaying media that the user has selected
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
    var num_updated = 0;
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
                    // geopoint prompts are actually four seperate prompts, one :dbcol_:suffix for each suffix
                    if (a.jsonValue.status == 0) {
                        alert("Error, location providers are disabled.") // (or the action was cancelled)
                    } else {
                        var suffixes = ["latitude", "longitude", "altitude", "accuracy"];
                        // update the screen data for each suffix with the results of the action
                        for (var i = 0; i < suffixes.length; i++) {
                            var suffix = suffixes[i];
                            var gsp_result = get_screen_prompt(s.dbcol + "_" + suffix)
                            // If the prompt is on the screen, set the prompt to the result, and we will notice
                            // that it was changed and put the new value in row_data later in this function
                            // Otherwise, put it in row_data and remind us we need to call updateOrInsert
                            if (gsp_result[0]) {
                                changeElement(gsp_result[1], a.jsonValue.result[suffix]);
                            } else {
                                row_data[s.dbcol + "_" + suffix] = a.jsonValue.result[suffix];
                                num_updated++; // let it know we have at least one changed cell to update into the database
                            }
                        }
                    }
                } else if (s.type == "image") {
                    // image prompts are actually two seperate prompts, one :dbcol_:suffix for each suffix
                    if (a.jsonValue.status == 0) {
                        // cancelled
                    } else if (a.jsonValue.result != undefined) {
                        var suffixes = ["uriFragment", "contentType"];
                        for (var i = 0; i < suffixes.length; i++) {
                            var suffix = suffixes[i];
                            if (a.jsonValue.result[suffix] == undefined) continue;
                            var gsp_result = get_screen_prompt(s.dbcol + "_" + suffix);
                            // If the prompt is on the screen, set the prompt to the result, and we will notice
                            // that it was changed and put the new value in row_data later in this function
                            // Otherwise, put it in row_data and remind us we need to call updateOrInsert
                            if (gsp_result[0]) {
                                changeElement(gsp_result[1], a.jsonValue.result[suffix]);
                            } else {
                                row_data[s.dbcol + "_" + suffix] = a.jsonValue.result[suffix];
                                num_updated++; // let it know we have at least one changed cell to update into the database
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
                        var gsp_result = get_screen_prompt(s.dbcol);
                        if (gsp_result[0]) {
                            changeElement(gsp_result[1], a.jsonValue.result.SCAN_RESULT_BYTES);
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
    // Set an onblur event listener on all selects, and an onchange event listener for all dropdown menus
    var elems = toArray(document.getElementsByTagName("select")).concat(toArray(document.getElementsByTagName("input")));
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].getAttribute("data-has_event_listener") == "1") {
            continue;
        }
        var listener = function() {setTimeout(function(){update(0);},0);};
        elems[i].addEventListener("blur", listener);
        if (elems[i].tagName == "SELECT") {
            elems[i].addEventListener("change", listener);
        }
        elems[i].setAttribute("data-has_event_listener", "1");
    }

    // ASSIGNS LOGIC
    // If an assign hasn't been put in the database yet, eval it and put that in,
    // then remind ourselves that we need to call updateOrInsert later
    var elems = document.getElementsByClassName("assign");
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var col = elem.getAttribute("data-dbcol");
        if (row_data[col] == null || row_data[col] == undefined || row_data[col].trim().length == 0) {
            // the "data-calculation" attribute holds a key to a string in `tokens` that we can eval to get the result
            row_data[col] = eval(tokens[elem.getAttribute("data-calculation")]).toString()
            num_updated++;
        }
    }

    // TRANSLATION LOGIC
    // First, iterate through anything with a `data-placeholder` attribute set, pull the real placeholder from
    // tokens using the value of `data-placeholder` translate it and set it as the regular old `placeholder` attribute
    // then clear the `data-placeholder` attribute so we don't hit it twice
    var elems = document.getElementsByTagName("input");
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].getAttribute("data-placeholder") != undefined && elems[i].getAttribute("data-placeholder").length > 0) {
            elems[i].setAttribute("placeholder", display(tokens[elems[i].getAttribute("data-placeholder")]));
            elems[i].setAttribute("data-placeholder", "");
        }
    }
    // First, iterate through anything with a class name of `translate` set, pull the real string from
    // tokens using the innerText, translate it and set it as the outer html (translation tokens can contain html)
    // when we set outerHTML it removes the "translate" class
    var elems = document.getElementsByClassName("translate");
    // IMPORTANT - DO NOT INLINE `len`, as `elems.length` will shrink by one on every iteration
    var len = elems.length;
    for (var i = 0; i < len; i++) {
        var text = tokens[elems[0].innerText];
        try {
            // YES elems[0] NOT elems[i]
            elems[0].outerHTML = display(text);
        } catch (e) {
            console.log(e)
            elems[0].outerHTML = "Error translating " + JSON.stringify(text);
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
    // Helper functiont that takes a list of pairs and a prompt element, then adds radio buttons or
    // checkboxes (depending on the type) with labels to the given element
    var pop_choices_for_select_one = function(stuffs, select, type) {
        for (var j = 0; j < stuffs.length; j++) {
            var id = select.getAttribute("data-dbcol") + "_" + stuffs[j][0];
            var elem = document.createElement("div")
            elem.style.width = "100%";
            //elem.classList.add("option")
            var inner = document.createElement("input")
            inner.type = type;
            inner.setAttribute("value", stuffs[j][0]);
            inner.setAttribute("id", id);
            inner.setAttribute("name", select.getAttribute("data-dbcol"));
            inner.addEventListener("change", function() {update(0);});
            elem.appendChild(inner);
            var label = document.createElement("label");
            //var n = document.createElement("span");
            //n.style.width = "100%";
            //n.innerHTML = stuffs[j][1];
            //label.appendChild(n);
            label.innerHTML = stuffs[j][1]
            label.setAttribute("for", id);
            label.id = id + "_tag";
            elem.appendChild(label);
            //elem.appendChild(document.createElement("br"));
            select.appendChild(elem);
            //label.style.width = (elem.clientWidth - inner.clientWidth - 10).toString() + "px"
        }
    };
    // For select multiple, populate using checkboxes
    populate_choices(document.getElementsByClassName("select-multiple"), function(stuffs, select) {
        pop_choices_for_select_one(stuffs, select, "checkbox")
    });
    // For select one, populate using radio buttons
    populate_choices(document.getElementsByClassName("select-one"), function(stuffs, select) {
        pop_choices_for_select_one(stuffs, select, "radio");
    });
    // For select one with other, populate normally then add an extra _other value with the label set to an input element
    populate_choices(document.getElementsByClassName("select-one-with-other"), function(stuffs, select) {
        pop_choices_for_select_one(stuffs, select, "radio");
        var dbcol = select.getAttribute("data-dbcol")
        pop_choices_for_select_one(["_other", "<input type='text' name='"+dbcol+"' id='"+dbcol+"__other_tag' onblur='document.getElementById(\\""+dbcol+"__other\\").checked = true; update(0);' />"], select);
        /*
        //var elem = document.createElement("div")
        ////elem.classList.add("option")
        //var id = select.getAttribute("data-dbcol") + "_" + "_other";
        //var radio = document.createElement("input")
        //radio.type = "radio";
        //radio.setAttribute("value", "_other");
        //radio.id = id
        //radio.setAttribute("name", select.getAttribute("data-dbcol"));
        //radio.addEventListener("change", function() {update(0);});
        //textbox = document.createElement("input");
        //textbox.type = "text";
        //textbox.id = id + "_tag"
        //textbox.setAttribute("name", select.getAttribute("data-dbcol"));
        //textbox.addEventListener("blur", function() {document.getElementById(select.getAttribute("data-dbcol") + "__other").checked = true; update(0);});
        //elem.appendChild(radio);
        //elem.appendChild(textbox);
        //select.appendChild(elem);
        */
    });

    // DATA UPDATE LOGIC
    // Scrapes all prompts on the screen, compares the result of screen_data(dbcol) against row_data[dbcol] for that prompt,
    // and if they differ, and the data is entirely populated, then update row_data to match and set num_changed so we know we
    // have to call updateOrInsert
    // If the data wasn't already populated (we've just changed screens and we need to load the value for this from the database)
    // then we put it in to_set, and then we loop through to_set and change the screen data to match the data in row_data
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
                // update row_data to match what's on the screen
                row_data[col] = newdata;
                console.log("Updating database value for " + col + " to screen value " + row_data[col]);
            }
        } else {
            to_set = to_set.concat(col);
        }
    }
    if (to_set.length > 0) {
        var elems = document.getElementsByClassName("prompt");
        for (var j = 0; j < elems.length; j++) {
            var elem = elems[j];
            if (to_set.indexOf(elem.getAttribute("data-dbcol")) >= 0) {
                col = elem.getAttribute("data-dbcol");
                if (typeof(row_data[col]) == "boolean") {
                    // this fixes acknowledges, otherwise we would changeElement to true (boolean) then screen_data would return true (string)
                    row_data[col] = row_data[col].toString();
                }
                console.log("Updating " + col + " to saved value " + row_data[col]);
                var loading = changeElement(elem, row_data[col]);
                var sdat = screen_data(col);
                if (row_data[col] !== null && sdat != row_data[col] && !loading) {
                    // This can happen when the database says a select one should be set to "M55" or something, but that's not one of the possible options.
                    // noop = "Unexpected failure to set screen value of " + col + ". Tried to set it to " + row_data[col] + " ("+typeof(row_data[col])+") but it came out as " + sdat + " ("+typeof(sdat)+")";
                    console.log("Unexpected failure to set screen value of " + col + ". Tried to set it to " + row_data[col] + " ("+typeof(row_data[col])+") but it came out as " + sdat + " ("+typeof(sdat)+")");
                    row_data[col] = sdat;
                } else {
                    elem.setAttribute("data-data_populated", "done");
                }
            }
        }
    }


    // VALIDATION LOGIC
    // A field can be invalid if it's required and empty, if it's supposed to be a number but it's not a valid number, or if
    // a user defined rule from the xlsx returns false. The user defined rules are often like "data('age') > 18", and they get evaled
    // `valid` is set to false if ANY of the prompts are invalid
    var valid = true
    // Remove all constraint warning messages, we're about to re-add them
    var elems = document.getElementsByClassName("constraint-message");
    for (var i = 0; i < elems.length; i++) {
        elems[i].outerHTML = ""; // remove the element
    }
    // Check validation for each prompt
    var elems = document.getElementsByClassName("prompt");
    for (var i = 0; i < elems.length; i++) {
        var this_valid = true;
        var col = elems[i].getAttribute("data-dbcol");
        if (elems[i].getAttribute("data-validate") == "double" || elems[i].getAttribute("data-validate") == "integer") {
            // This code can handle both doubles and ints because validity.valid's behavior depends on step, which defaults
            // to 1 but we set it to any for doubles
            var num = Number(elems[i].value);
            if (isNaN(num) || !elems[i].validity.valid) {
                this_valid = false;
            }
        }
        // Checks if the field is required
        if (elems[i].getAttribute("data-required") != null) {
            var entered = screen_data(col);
            if (entered == null || entered.length == 0) {
                this_valid = false;
            }
        }
        // Handles evaling the user defined constraints
        if (elems[i].getAttribute("data-constraint") != null) {
            if (!eval(tokens[elems[i].getAttribute("data-constraint")])) {
                this_valid = false;
            }
        }
        // If this prompt is invalid, set valid to false, display a warning message if there is one, and make it red so the user notices
        if (!this_valid) {
            valid = false;
            elems[i].style.backgroundColor = "pink";
            if (elems[i].getAttribute("data-constraint_message") != null) {
                var message = document.createElement("div");
                message.classList.add("constraint-message");
                message.innerText = display(tokens[elems[i].getAttribute("data-constraint_message")]);
                elems[i].parentNode.insertBefore(message, elems[i].nextSibling);
            }
        } else {
            elems[i].style.backgroundColor = ""; // Default
        }
    }
    // If the row was invalid, trap the user on the current screen
    if (!valid) {
        document.getElementById("next").disabled = true;
        document.getElementById("back").disabled = true;
        document.getElementById("finalize").disabled = true;
        delta = 0;
    }

    // DATABASE UPDATE
    // If the screen is valid and we changed something in row_data, updateOrInsert()
    if (num_updated > 0 && valid) {
        updateOrInsert()
    }

    // For each of the if statements, eval it then set the display style on it if applicable
    var spans = document.getElementsByClassName("validate");
    for (var i = 0; i < spans.length; i++) {
        var rule = spans[i].getAttribute("data-validate-rule");
        if (eval(tokens[rule])) {
            spans[i].style.display = "block";
        } else {
            spans[i].style.display = "none";
        }
    }

    // Displays media
    // For each "image" prompt, which includes image, video and audio prompt types, find that element on the
    // screen and if there is a uri fragment for that image in row_data, then set the source to that fragment
    var elems = document.getElementsByClassName("image");
    for (var i = 0; i < elems.length; i++) {
        var elem = elems[i];
        var dbcol = elem.getAttribute("data-dbcol") + "_uriFragment";
        if (row_data[dbcol] == null || row_data[dbcol] == undefined || row_data[dbcol].trim().length == 0) {
            // don't bother setting it if there's no source to set
            continue;
        }
        var newsrc = odkCommon.getRowFileAsUrl(table_id, row_id, data(dbcol));
        if (elem.src != newsrc) {
            if (elem.classList.contains("audio") || elem.classList.contains("video")) {
                elem.innerHTML = "";
                var newsource = document.createElement("source");
                newsource.src = newsrc;
                elem.appendChild(newsource);
            } else {
                elem.src = newsrc;
            }
            elem.style.display = "block";
        }
    }

    // ENABLE/DISABLE NEXT/BACK/FINALIZE BUTTON LOGIC
    if (!valid) return; // buttons have already been disabled
    // Update global_screen_idx to prepare to change the data on the screen to it
    global_screen_idx += delta;
    odkCommon.setSessionVariable(table_id + ":" + row_id + ":global_screen_idx", global_screen_idx);
    // If we're at the beginning, disable the back button, otherwise enable it
    if (global_screen_idx <= 0) {
        global_screen_idx = 0;
        document.getElementById("back").disabled = true;
    } else {
        document.getElementById("back").disabled = false;
    }
    if (global_screen_idx >= screens.length - 1) {
        // If we're at the end of the survey, disable the next button and show the finalize button
        global_screen_idx = screens.length - 1;
        document.getElementById("next").disabled = true;
        document.getElementById("next").style.display = "none";
        document.getElementById("finalize").style.display = "block";
        document.getElementById("finalize").disabled = false;
    } else {
        // Otherwise, enable the next button and hide the finalize button
        document.getElementById("finalize").style.display = "none";
        document.getElementById("next").disabled = false;
        document.getElementById("next").style.display = "block";
    }
    // If we're actually switching to a new screen, change the html on the page
    if (delta != 0) {
        var container = document.getElementById("odk-container");
        container.innerHTML = screens[global_screen_idx];
        update(0);
    }
}
// Helper function to determine if the screen has a particular prompt or not, and if so, return it as a dom element
var get_screen_prompt = function get_screen_prompt(id) {
    var elems = document.getElementsByClassName("prompt");
    for (var i = 0; i < elems.length; i++) {
        if (elems[i].getAttribute("data-dbcol") == id) {
            return [true, elems[i]];
        }
    }
    return [false, null];
}
// Function to insert the row into the database one last time (does that by calling update()), then sets savepoint type to complete and finishes
var finalize = function finalize() {  
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
// Cancels the add and deletes the intermediate row, asks for confirmation if we've already inserted data but if they didn't type anything yet, it doesn't
var cancel = function cancel() {
    if (!opened_for_edit) {
        if (row_exists) {
            if (confirm("Are you sure? All entered data will be deleted.")) {
                odkData.deleteRow(table_id, null, row_id, function() {
                    page_back();
                }, function(err) {
                    alert("Unexpected error deleting row: " + JSON.stringify(err));
                    page_back();
                })
            }
        } else {
            page_back();
        }
    } else {
        page_back();
    }
}
// Simple wrapper for odkCommon.doAction that shows a warning if the doAction fails.
var doAction = function doAction(dStruct, act, intent) {
    var result = odkCommon.doAction(dStruct, act, intent);
    if (result == "OK" || result == "IGNORED") {
        return;
    }
    alert("Error launching " + act + ": " + result);
}
// Function that runs on page load, sets up some initial choices, gets the row id from the uri, determines if the row
// we're editing exists or not and sets up opened_for_edit and row_exists based on that, 
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
    // Get the row id from the url, or makes a new id if it can't get it
    row_id = window.location.hash.substr(1);
    if (row_id.length == 0) {
        row_id = newGuid();
        alert("No row id in uri, beginning new instance with id " + row_id);
        opened_for_edit = false;
    }
    // Try to load global_screen_idx from a session variable, but default to zero (we will subtract one later)
    global_screen_idx = Number(odkCommon.getSessionVariable(table_id + ":" + row_id + ":global_screen_idx"));
    if (isNaN(global_screen_idx)) {
        global_screen_idx = 0;
    }
    // Set to default to -1 so we can update(1) to force displaying of the screen at index 0, whereas
    // if we just started it at zero and called update(0) it wouldn't change the current screen data
    global_screen_idx -= 1;
    // Get row data
    odkData.getRows(table_id, row_id, function success(d) {
        try {
            // Try to load all rows from the result object into row_data if we're editing a row
            var cols = d.getColumns();
            var generator = function(i) { return d.getData(0, cols[i]); };
            if (d.getCount() == 0) {
                row_exists = false;
                opened_for_edit = false;
                generator = function(i) { return null; };
            } else {
                row_exists = true;
                opened_for_edit = true;
            }
            for (var i = 0; i < cols.length; i++) {
                // Do not load columns that start with underscores
                if (cols[i][0] != "_") {
                    row_data[cols[i]] = generator(i);
                }
            }
            // Change the text in the cancel button based on whether we're adding or editing a row
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
        // Actually display the stuff on the screen
        update(1);
        // TODO left off here
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
</html>"""
            if os.path.exists("formgen/" + table):
                subprocess.check_call(["rm", "-rf", "formgen/" + table])
            os.mkdir("formgen/" + table);
            open("formgen/" + table + "/index.html", "w").write(basehtml)
            for f in glob.glob(utils.appdesigner + "/app/config/tables/" + table + "/forms/" + table + "/*"):
                fn = os.path.basename(f);
                if fn in ["formDef.json", "properties.csv", "definition.csv", "customStyles.css"] or fn.endswith(".xls") or fn.endswith(".xlsx"):
                    continue
                src = "/sdcard/opendatakit/" + utils.appname + "/config/tables/" + table + "/forms/" + table + "/" + fn
                dest_folder = "/sdcard/opendatakit/" + utils.appname + "/config/assets/formgen/" + table + "/"
                dest = dest_folder + fn
                utils.queue.append(["adb", "shell", "mkdir", "-p", dest_folder])
                utils.queue.append(["adb", "shell", "cp", "-rv", src, dest])
            filenames.append("formgen/" + table + "/index.html")
        except:
            if skipped:
                print("Skipping " + table)
            else:
                print("Unexpected exception in " + table)
                print(traceback.format_exc())
                sys.exit(1)
    return filenames
