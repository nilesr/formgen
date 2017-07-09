import sys, os, subprocess
sys.path.append(".")
import generate_table
def make_and_push(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    generate_table.make(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric)
    subprocess.call(["adb", "push", filename, "/sdcard/opendatakit/default/config/assets/" + filename])
    os.remove(filename);
make_and_push("Tea_houses.html", "", "", """
display_subcol = [["Specialty: ", "State", true], ["", "District", false], [", ", "Neighborhood", true]];
table_id = "Tea_houses";
""", "", "")
