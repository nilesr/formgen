import sys, os, subprocess
sys.path.append(".")
import utils
import generate_table
import generate_detail
def make_table(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    generate_table.make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/"+utils.appname+"/config/assets/" + filename])
    os.remove(filename);
def make_detail(filename, customHtml, customCss, customJsOl, customJsGeneric):
    generate_detail.make(filename, customHtml, customCss, customJsOl, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/"+utils.appname+"/config/assets/" + filename])
    os.remove(filename);
# in customJsOl you MUST SET table_id to something, like
# table_id = "Tea_houses"
# Strongly recommend setting display_col, like
# display_col = "Name"
# Tip - if you set "allowed_tables = []" in onload, it will open/edit in survey instead of formgen no matter what
# Can set display_subcol if you want more things displayed, like this
# display_subcol = [["Specialty: ", "ttName", true], ["", "District", false], [", ", "Neighborhood", true]];
# That display "Specialty: Ulong" on one line then "Seattle, Belltown" on the next
# Second thing in the triplet is the column ID, third thing in the triplet is whether to add a newline after that triplet
# If the first thing in the triplet is a string, the string is printed followed by the value of the given column
#       ^ unless the column is null, in which case it will just print the text
# If the first thing is a function, it's called with the second argument set to the column value, and whatever the function returns is displayed. For example
# var sc_callback = function(e, d) {
#       if (d == "Ulong") {
#           return "This tea house specializes in Ulong - Yuck!"
#       } else {
#           return "Specialty: " +  d;
#       }
# };
# display_subcol = [[sc_callback, "ttName", true]]
# would display a snide remark about the tea houses specialty if it specializes in ulong, otherwise display it normally
# Another example from selects
# var cb = function(elem, bird) {
#     if (bird == null || bird == undefined || bird.trim().length == 0) return "Didn't see anything";
#     var n = ""
#     if ("aeiou".indexOf(bird[0].toLowerCase()) >= 0) n = "n"
#     return "Saw a" + n + " " + bird;
# }
# display_subcol = [[cb, "bird", true]];
# will be able to show things like "Didn't see anything", "Saw a robin", and "Saw an egret"
# TODO find out whether the callback functions can return html or not




# To do a cross table query, set a JOIN, example from tea houses
# global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
# In this case, Tea_houses and Tea_types both have a column called Name, so you need to tell the sql how to differentiate them. Do that by setting
# global_which_cols_to_select = "*, Tea_types.Name as ttName"
# Unless your column names actually conflict this is usually unneccesary. If you need to do this, you'll know, it will display a big error when you try and load the list view

# By default it will allow you to group on any column, and display the translated/prettified name in the listing. To configure which ones are allowed, set something like this
# allowed_group_bys = [["Specialty", true], ["District", "District of the tea house"]]
# Then your users won't be able to group by silly things like the column name
# First string in each pair is the column id, second one is a bit special. If it's a string, that string is displayed in the dropdown menu
# If it's true, the translated column id is used
# If it's false, the literal column id is used (same as duplicating the first argument)
# If there's only one pair in the list of allowed_group_bys, it's launched automatically if the user clicks the group by button.
# If you set allowed_group_bys to an empty list, the group by button won't be displayed

# For make_detail, you almost certianly need to set main_col to something, so for tea houses
# main_col = "Name"
# By default, it will display every single column in the list. To configure how it gets shown, set colmap
# TODO more documentation

# Cold chain demo
if utils.appname == "coldchain":
    make_table("refrigerator_types_list.html", "", "", """
        display_subcol = [["Manufacturer: ", "manufacturer", true]];
        allowed_group_bys = [["manufacturer", "Manufacturer"]]
        display_col = "catalog_id"
        table_id = "refrigerator_types";
""", "", "")

    make_table("refrigerators_list.html", "", "", """
        global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
        display_subcol = [["", "model_id", true], ["Healthcare Facility: ", "facility_name", true]];
        display_col = "refrigerator_id"
        table_id = "refrigerators";
        allowed_group_bys = [["facility_row_id", "Facility"], ["model_row_id", "Model"], ["reason_not_working", true], ["utilization", "Use"], ["working_status", true], ["year", true]]
""", "", "")
    make_detail("refrigerators_detail.html", "<div id='h4-wrapper'><h4>Basic Refrigerator Information<h4></div>", open("refrigerator_detail.css").read(),
    """
        document.getElementById("main-col").classList.add("main-col-wrapper")
        document.getElementById("main-col").style.display = "block";
        var new_elem = document.createElement("div");
        document.getElementById("main-col").appendChild(new_elem)
        document.getElementById("main-col").id = ""
        new_elem.id = "main-col"
        var h4 = document.getElementById("h4-wrapper")
        document.body.insertBefore(h4, document.getElementById("rest"));
        document.body.insertBefore(document.getElementsByClassName("main-col-wrapper")[0], h4);
        main_col = "refrigerator_id";
        global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
        colmap = [
            ["power_type", function(e, c, d) {return "<b>Power:</b> " + pretty(c);}],
            ["facility_row_id", function(e, c, d) {return "<b>Facility:</b> " + d.getData(0, "facility_name");}], // from join, not actually the facility id
            ["model_row_id", function(e, c, d) {return "<b>Model:</b> " + d.getData(0, "catalog_id");}], // from join, not actually the model id
            ["working_status", function(e, c, d) {return "<b>Status:</b> " + pretty(c);}],
            ["utilization", true],
            ["voltage_regulator", true],
            ["power_source", true],
            ["reason_not_working", true],
            ["utilization", "In use?"],
            ["working_status", "Working?"],
            ["refrigerator_id", function(e, c, d) {return "Refrigerator " + c}]
        ]
    """, "")
    # TODO ADD View Model Information, View Facility Information buttons


if utils.appname == "default":
    make_table("plot.html", "", "", """
        var planting_callback = function planting_callback(elem, val) {
            if (val == null || val.trim().length == 0) {
                return "Not planting";
            }
            return val[0].toUpperCase() + val.substr(1);
        }
        display_subcol = [[planting_callback, "planting", false], [", ","plot_size", false], [" hectares", null, true]];
        table_id = "plot";
""", "", "")


    make_table("Tea_houses.html", "", "", """
        global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
        //global_which_cols_to_select = "Tea_houses.Name as Name, Tea_types.Name as ttName, District, Neighborhood, Tea_houses._savepoint_type as _savepoint_type"
        global_which_cols_to_select = "*, Tea_types.Name as ttName"
        display_subcol = [["Specialty: ", "ttName", true], ["", "District", false], [", ", "Neighborhood", true]];
        table_id = "Tea_houses";
""", "", "")

#make_detail("Tea_houses_detail.html", "", "", "", "")

# For testing that sure it opens survey for forms I can't generate yet. This one has sections or something and formgen hates it
#make_detail("exampleForm_detail.html", "", "", "", "")
#make_table("exampleForm_list.html", "", "", """
#        display_subcol = [["", "rating", false], ["/10", null, true]];
#        display_col = "name"
#        table_id = "exampleForm";
#""", "", "")


#make_detail("selects_detail.html", "", "", "", "")
    make_table("selects_list.html", "", "", """
        var cb = function(elem, bird) {
            if (bird == null || bird == undefined || bird.trim().length == 0) return "Didn't see anything";
            var n = ""
            if ("aeiou".indexOf(bird[0].toLowerCase()) >= 0) n = "n"
            return "Saw a" + n + " " + bird;
        }
        display_subcol = [[cb, "bird", true]];
        display_col = "user_name"
        table_id = "selects";
""", "", "")

