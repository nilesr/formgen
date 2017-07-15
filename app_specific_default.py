import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();


helper.make_table("plot.html", "", "", """
    display_subcol = [["", "planting", false], [", ","plot_size", false], [" hectares", null, true]];
    table_id = "plot";
""", "", "")


helper.make_table("Tea_houses_list.html", "", "", """
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
helper.make_table("selects_list.html", "", "", """
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
