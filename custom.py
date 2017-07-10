import sys, os, subprocess
sys.path.append(".")
import generate_table
import generate_detail
def make_table(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    generate_table.make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/default/config/assets/" + filename])
    os.remove(filename);
def make_detail(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    generate_detail.make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/default/config/assets/" + filename])
    os.remove(filename);
# in customJsOl
# MUST SET table_id
# Strongly reccommend setting display_col
# Can set display_subcol if you want more things displayed
# example from Tea_houses
# display_subcol = [["Specialty: ", "State", true], ["", "District", false], [", ", "Neighborhood", true]];
make_table("Tea_houses.html", "", "", """
        display_subcol = [["Specialty: ", "State", true], ["", "District", false], [", ", "Neighborhood", true]];
        table_id = "Tea_houses";
""", "", "")


make_table("refrigerators.html", "", "", """
        display_subcol = [["Condition: ", "refrigerator_condition", true]];
        display_col = "refrigerator_id"
        table_id = "refrigerators";
""", "", "")


make_table("plot.html", "", """
        #table_id {display: none;}
""", """
        display_subcol = [["", "planting", false], [", ","plot_size", false], [" hectares", null, true]];
        table_id = "plot";
""", "", "")


make_detail("Tea_houses_detail.html", "", "", """
// TODO!!
""", "", "")

