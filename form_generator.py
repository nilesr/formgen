import json, sys, os, glob, traceback, subprocess, random, collections
# TODO items
# Must have before release!
#   - Display sync state in table, sync state and savepoint type in detail
# Other things not implemented
#   - take picture is broken - SURVEY BUG
# 	- datetime, time - IMPORTANT
#   - Figure out when to calculate assigns (and implement calculates object)
# 	- linegraph, piechart
# 	- goto (EASY!)
# 	- sections (could be hard)
# 	- send_sms
# 	- read_only_image
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
skipped = True
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
    all_choices = collections.defaultdict(lambda: [])
    columns_that_need_choices = collections.defaultdict(lambda: {})
    for table in tables:
        global skipped
        skipped = False
        try:
            formDef = json.loads(open(utils.appdesigner + "/app/config/tables/" + table + "/forms/" + table + "/formDef.json", "r").read())
            screens = []
            rules = []
            screen = []
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
                            if falsey(tokens[rule]):
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
                        columns_that_need_choices[table][item["name"]] = item['values_list'];
                        screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-multiple "+wrapped_class+"\"" + attrs + "></div>")
                    # Same thing but with radio buttons instead of checkboxes
                    elif item["type"] in ["select_one", "select_one_grid"]:
                        columns_that_need_choices[table][item["name"]] = item['values_list'];
                        screen.append("<br /><div style='display: inline-block;' data-values-list=\""+item["values_list"]+"\" class=\"select-one "+wrapped_class+"\"" + attrs + "></div>")
                    # Same thing but an extra _other choice will be added, with a text box for the label
                    elif item["type"] == "select_one_with_other":
                        columns_that_need_choices[table][item["name"]] = item['values_list'];
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
                all_choices[table] += json.loads(choices);
            basehtml = """
<!doctype html>
""" + utils.warning + """
<html>
<head>
    <style>
    """ + open("form_generator.css", "r").read() + """
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
    <script type="text/javascript" src="../../../../system/libs/underscore.1.8.3.js"></script>
    <script>
// Copy out screens, choices, queries, table id, tokens and has_dates from the python side
var screens = """ + json.dumps(screens) + """;
var choices = """ + choices + """;
var queries = """ + queries + """;
var table_id = '""" + table + """';
var tokens = """ + json.dumps(tokens) + """
var has_dates = """ + ("true" if has_dates else "false") + """
""" + open("form_generator.js", "r").read() + """
    </script>
</head>
<body onLoad='ol();'>
    <div class="odk-toolbar" id="odk-toolbar">
        <button id='cancel' onClick='cancel()' disabled>Loading...</button>
        <button id='back' onClick='update(-1)'></button>
        <button id='next' onClick='update(1)'></button>
        <button id='finalize' style='display: none;' onClick='finalize()'></button>
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
    return filenames, all_choices, columns_that_need_choices
