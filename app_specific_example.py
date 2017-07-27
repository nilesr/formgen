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
	clicked = function clicked(table_id, row_id) {
		odkTables.openDetailWithListView(null, table_id, row_id, "config/assets/Tea_houses_detail.html");
	}
	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName"
	display_subcol = [["Specialty: ", "ttName", true], ["", "District", false], [", ", "Neighborhood", true]];
	display_col = "thName";
	table_id = "Tea_houses";
""", "", "")
helper.make_table("Tea_inventory_list.html", "", "", """
	global_join = "Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName"
	display_subcol = [["Tea House: ", "thName", true], ["Type: ", "ttName", true]];
	display_col = "tiName";
	table_id = "Tea_inventory";
""", "", "")
helper.make_detail("Tea_houses_detail.html", "", "", """
	main_col = "thName";
	table_id = "Tea_houses";
	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName"
	var br = function(col, extra) {
		return function(e, c, d) { return "<b>" + col + "</b>: " + c + (extra ? extra : "<br />"); };
	}
	var check = function(col) {
		return function(e, c, d) {
			return "<input disabled type='checkbox' " + (c.toUpperCase() == "YES" ? "checked=checked" : "") + " /><b>" + col + "</b>";
		};
	}
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
		["_id", function(e, c, d) {
			odkData.arbitraryQuery("Tea_inventory", "SELECT COUNT(*) FROM Tea_inventory WHERE House_id = ?", [row_id], 1, 0, function(d) {
				var count = d.getData(0, "COUNT(*)");
				var teas = document.getElementById("teas")
				teas.style.color = "blue";
				teas.style.textDecoration = "underline";
				teas.innerText = count + " Tea" + (count == 1 || count == "1" ? "" : "s");
				teas.addEventListener("click", function() {
					odkTables.openTableToListView({}, "Tea_inventory", "House_id = ?", [c], "config/assets/Tea_inventory_list.html#Tea_inventory/House_id = ?/" + c);
				});
			}, function(e) {
				alert(e);
			});
			odkTables.setSubListView("Tea_inventory", "House_id = ?", [c], "config/assets/Tea_inventory_list.html#Tea_inventory/House_id = ?/" + c);
			return "<span onClick='odkTables.openTableToListView(null, \\'Tea_inventory\\', null, null, \\'Tea_inventory_list.html#Tea_inventory/House_id = ?/"+c+"\\')' id='teas'>Loading...</span>"
		}]
	]
""", "")
helper.make_detail("Tea_inventory_detail.html", "", "", """

	main_col = "tiName";
	table_id = "Tea_inventory";
	global_join = "Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName"
	var check = function(col) {
		return function(e, c, d) {
			return "<input disabled type='checkbox' " + (c.toUpperCase() == "YES" ? "checked=checked" : "") + " /><b>" + col + "</b>";
		};
	}
	colmap = [
		["tiName", function(e, c, d) { return c }],
		["ttName", "Type: "],
		["Price_8oz", false],
		["Price_12oz", false],
		["Price_16oz", function(e, c, d) { return "<b>16oz</b>: " + c + "<br /><br /><b>Offered</b>:" }],
		["Iced", check("Iced")],
		["Hot", check("Hot")],
		["Loose_Leaf", check("Loose Leaf")],
		["Bags", check("Bags")],
	]
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
		["View Teas", "Tea_inventory", ""],
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
""", "")
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
""", "")

