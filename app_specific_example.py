import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();


helper.make_table("plot.html", "", "", """
	var plating_cb = function(elem, planting) {
		if (planting == null || planting == "null") return "Not planting"
		return "Planting " + planting.toLowerCase() + " corn"
	}
	display_subcol = [[planting_cb, "planting", false], [", ","plot_size", false], [" hectares", null, true]];
	table_id = "plot";
""", "", "")


helper.make_table("Tea_houses_list.html", "", "", """
	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
	global_which_cols_to_select = "*, Tea_types.Name as ttName"
	display_subcol = [["Specialty: ", "ttName", true], ["", "District", false], [", ", "Neighborhood", true]];
	table_id = "Tea_houses";
""", "", "")
helper.make_detail("Tea_houses_detail.html", "", "", """
	main_col = "Name";
	table_id = "Tea_houses";
""", "")

helper.make_detail("exampleForm_detail.html", "", "", "", "")
helper.make_table("exampleForm_list.html", "", "", """
		//display_subcol = [["", "rating", false], ["/10", null, true]];
		display_col = "name"
		table_id = "exampleForm";
""", "", "")


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


helper.make_tabs("index.html", """
	var tabs = [
		["General Demo", "general.html"],
		["Tea Houses", "th_index.html"],
		// TODO
		["Selects Demo", "404.html"],
		["Plot Demo", "404.html"],
	]
""", "")

helper.make_index("th_index.html", """
	list_views = {
		"Tea_houses": "Tea_houses_list.html",
		"Tea_types": "Tea_types_list.html",
		"Tea_inventory": "Tea_inventory_list.html",
	}
	menu = ["TODO", null, []];
""", "")
helper.make_index("general.html", """
	list_views = {
		"exampleForm": "exampleForm_list.html"
	}
	var newinstance = function newinstance() {
		var id = newGuid();
		odkTables.launchHTML(null, "config/assets/formgen/exampleForm#" + id);
	}
	menu = ["Example Form", null, [
		["New Instance", "_js", newinstance],
		["View Responses", "exampleForm", ""]
	]]
""", "")
