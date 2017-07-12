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
        display_subcol = [["", "planting", false], [", ","plot_size", false], [" hectares", null, true]];
        table_id = "plot";
""", "", "")


    make_table("Tea_houses.html", "", "", """
        global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
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

