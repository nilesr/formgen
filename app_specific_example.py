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

helper.make_detail("example_detail.html", "", "", "", "")
helper.make_table("example_list.html", "", "", """
		var ack = function(_, c) {
			if (c == "true") {
				return "Does acknowledge <i><span style='color: red; font-weight: bold;>html</html>";
			}
			return "Doesn't acknowledge!";
		}
		display_subcol = [[ack, "has_html", false], ["/10", null, true]];
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
		["Selects Demo", "selects_index.html"],
		// TODO
		/*
		["Plot Demo", "404.html"],
		*/
	]
""", "")

helper.make_index("th_index.html", """
	list_views = {
		"Tea_houses": "config/assets/Tea_houses_list.html",
		"Tea_types": "config/assets/Tea_types_list.html",
		"Tea_inventory": "config/assets/Tea_inventory_list.html",
	}
	var newinstance = function newinstance(table) {
		return function() {
			var id = newGuid();
			odkTables.launchHTML(null, "config/assets/formgen/"+table+"#" + id);
		}
	}
	menu = ["Tea Demo", null, [
		["View Tea Houses (try searching for \\"Hill\\")", "Tea_houses", ""],
		["View Tea Houses on a Map", "_js", function() { odkTables.openTableToMapView(null, "Tea_Houses", null, null, "config/assets/Tea_houses_list.html"); }],
		["New tea house", "_js", newinstance("Tea_houses")],
		["View Tea Types", "Tea_types", ""],
		["Add Tea Type", "_js", newinstance("Tea_types")],
		["View Tea Inventory", "Tea_inventory", ""],
		["Add Tea Inventory Entry", "_js", newinstance("Tea_inventory")]
	]]
""", "")
helper.make_index("general.html", """
	list_views = {
		"exampleForm": "config/assets/example_list.html"
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
helper.make_index("selects_index.html", """
	list_views = {
		"exampleForm": "exampleForm_list.html"
	}
	var newinstance = function newinstance() {
		var id = newGuid();
		odkTables.launchHTML(null, "config/assets/formgen/selects#" + id);
	}
	menu = ["Selects Demo", null, [
		["New Instance", "_js", newinstance],
		["View Responses", "selects", ""]
	]]
""", "")

