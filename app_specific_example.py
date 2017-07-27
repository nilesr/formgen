import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();


helper.make_table("plot.html", "", "", """
	var planting_cb = function(elem, planting) {
		if (planting == null || planting == "null") return "Not planting"
		return "Planting " + planting.toLowerCase() + " corn"
	}
	display_subcol = [[planting_cb, "planting", false], [", ","plot_size", false], [" hectares", null, true]];
	table_id = "plot";
""", "", "")


helper.make_table("Tea_houses_list.html", "", "", """
	clicked = function clicked(table_id, row_id) {
		odkTables.openDetailWithListView(null, table_id, row_id, "config/assets/Tea_houses_detail.html");
	}
	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName"
	display_subcol = [["Specialty: ", "ttName", true], ["", "District", false], [", ", "Neighborhood", true]];
	display_col = "thName";
	table_id = "Tea_houses";
	allowed_group_bys = [
		"District", "Neighborhood", "State", "WiFi", "Hot", "Iced", "State", ["ttName", "Specialty"]
	]
""", "", "")
helper.make_table("Tea_inventory_list.html", "", "", """
	global_join = "Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName"
	display_subcol = [["Tea House: ", "thName", true], ["Type: ", "ttName", true]];
	display_col = "tiName";
	table_id = "Tea_inventory";
	allowed_group_bys = [
		["thName", "House"], ["ttName", "Type"], "Iced", "Hot", "Bags", "Loose_Leaf"
	]
""", "", "")
helper.make_table("Tea_types_list.html", "", "", """
	var extras_cb = function extras_cb(e, c, d, i) {
		var caffeinated = d.getData(i, "Caffeinated").toUpperCase() == "YES"
		var fermented = d.getData(i, "Fermented").toUpperCase() == "YES"
		var extras = []
		if (caffeinated) extras = extras.concat("Caffeinated");
		if (fermented) extras = extras.concat("Fermented");
		return extras.join(", ");
	}
	display_subcol = [["Origin: ", "Origin", true], [extras_cb, "_id", true]];
	display_col = "Name";
	table_id = "Tea_types";
	allowed_group_bys = [
		"Origin", "Caffeinated, "Fermented"
	]
""", "", "")
detail_helper_js = """
	var br = function(col, extra) {
		return function(e, c, d) { return "<b>" + col + "</b>: " + c + (extra ? extra : "<br />"); };
	}
	var check = function(col) {
		return function(e, c, d) {
			return "<input disabled type='checkbox' " + (c.toUpperCase() == "YES" ? "checked=checked" : "") + " /><b>" + col + "</b>";
		};
	}
"""
helper.make_detail("Tea_houses_detail.html", "", "", detail_helper_js + """
	main_col = "thName";
	table_id = "Tea_houses";
	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, (SELECT COUNT(*) FROM Tea_inventory WHERE Tea_inventory.House_id = Tea_houses._id) AS num_teas"
	var opened = function(e, c, d) { return "<b>Opened</b>: " + (c == null ? "" : c).split("T")[0]; };
	colmap = [
		["thName", function(e, c, d) { return c }],
		["State", true],
		["Region", true],
		["District", true],
		["Neighborhood", br("Neighborhood")],
		["ttName", br("Specialty")],
		["Date_Opened", opened],
		["Customers", "Number of Customers: "],
		["Visits", br("Total Number of Visits")],
		["Location_latitude", "Latitude (GPS): "],
		["Location_longitude", br("Longitude (GPS)", "<br /><br /><b>Services</b>:")],
		["Iced", check("Iced")],
		["Hot", check("Hot")],
		["WiFi", function(e, c, d) { return check("WiFi")(e, c, d) + "<br /><h3>Contact Information</h3>"; }],
		["Store_Owner", true],
		["Phone_Number", "Mobile number: "],
		["num_teas", function (e, c, d) {
			odkTables.setSubListView("Tea_inventory", "House_id = ?", [row_id], "config/assets/Tea_inventory_list.html#Tea_inventory/thName = ?/" + d.getData(0, "thName"));
			return "<span onClick='openTeas();' style='color: blue; text-decoration: underline;'>" + c + " tea" + (c.toString() == 1 ? "" : "s") + "</span>";
		}],
	]
	window.openTeas = function openTeas() {
		odkTables.openTableToListView({}, "Tea_inventory", "House_id = ?", [row_id], "config/assets/Tea_inventory_list.html#Tea_inventory/thName = ?/" + cached_d.getData(0, "thName"));
	}
""", "")
helper.make_detail("Tea_inventory_detail.html", "", "", detail_helper_js + """

	main_col = "tiName";
	table_id = "Tea_inventory";
	global_join = "Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName"
	colmap = [
		["tiName", function(e, c, d) { return c }],
		["ttName", "Type: "],
		["Price_8oz", "8oz: "],
		["Price_12oz", "12oz: "],
		["Price_16oz", function(e, c, d) { return "<b>16oz</b>: " + c + "<br /><br /><b>Offered</b>:" }],
		["Iced", check("Iced")],
		["Hot", check("Hot")],
		["Loose_Leaf", check("Loose Leaf")],
		["Bags", check("Bags")],
	]
""", "")
helper.make_detail("Tea_types_detail.html", "", "", detail_helper_js + """

	main_col = "Name";
	table_id = "Tea_types";
	colmap = [
		["Name", function(e, c, d) { return c }],
		["Origin", br("Origin", "<br /><br />Details:")],
		["Caffeinated", check("Caffeinated")],
		["Fermented", check("Fermented")],
	]
""", "")

helper.make_detail("example_detail.html", "", "", "", "")
helper.make_table("example_list.html", "", "", """
		var ack = function(_, c) {
			if (c == true) {
				return "Does acknowledge <i><span style='color: red; font-weight: bold;'>html</html>";
			}
			return "Doesn't acknowledge!";
		}
		display_subcol = [[ack, "has_html", true], ["Admin region: ", "adminRegion", true]];
		display_col = "name"
		table_id = "exampleForm";
""", "", "")


helper.make_detail("selects_detail.html", "", "", "", "")
helper.make_table("selects_list.html", "", "", """
	var cb = function(elem, bird, d, i) {
		if (bird == null || bird == undefined || bird.trim().length == 0) return "Didn't see anything";
		var color = d.getData(i, "color");
		var n = ""
		if ("aeiou".indexOf(color[0].toLowerCase()) >= 0) n = "n"
		return "Saw a" + n + " " + color + " " + bird;
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
		["Plot Demo", "plot_index.html"]
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
		["View Teas", "Tea_inventory", ""],
		["View Teas by Tea House", "Tea_inventory", "thName"],
		["Add Tea", "_js", newinstance("Tea_inventory")],
		["View Tea Types", "Tea_types", ""],
		["Add Tea Type", "_js", newinstance("Tea_types")],
	]]
""", """
body {
	background: url('img/teaBackground.jpg') no-repeat center/cover fixed;
}
#title {
	width: 100%;
	display: block;
	box-shadow: none;
	color: white;
	font-family: arial;
	border-bottom: 2px solid #38c0f4;
	background: none;
	margin-left: 0px;
	margin-right: 0px;
	font-size: 35px;
	padding-top: 5px;
	padding-bottom: 5px;
	margin-bottom: 25px;
	font-weight: bold;
}
""")
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
""", """
body {
	background: url('img/hallway.jpg') no-repeat center/cover fixed;
}
""")
helper.make_index("selects_index.html", """
	list_views = {
		"selects": "config/assets/selects_list.html"
	}
	var newinstance = function newinstance() {
		var id = newGuid();
		odkTables.launchHTML(null, "config/assets/formgen/selects#" + id);
	}
	menu = ["Selects Demo", null, [
		["New Instance", "_js", newinstance],
		["View Responses", "selects", ""]
	]]
""", """
body {
	background: url('img/bird.png') no-repeat center/cover fixed;
}
""")
helper.make_index("plot_index.html", """
	list_views = {
		//"selects": "config/assets/selects_list.html"
	}
	var todo = function() {alert("TODO")};
	menu = ["Plots Demo", null, [
		["View Plots", "_js", todo],
		["View Visits", "_js", todo],
		["View Reports", "_js", todo]
	]]
""", """
body {
	background: url('img/Agriculture_in_Malawi_by_Joachim_Huber_CClicense.jpg') no-repeat center/cover fixed;
}
""")

