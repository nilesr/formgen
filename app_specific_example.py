import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();


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
	var check = function(col, accepting, type) {
		if (accepting === undefined) {
			accepting = function(e, c, d) {
				return c.toUpperCase() == "YES";
			}
		}
		if (type === undefined) type = "checkbox"
		return function(e, c, d) {
			return "<input disabled type='"+type+"' " + (accepting(e, c, d) ? "checked=checked" : "") + " /><b>" + col + "</b>";
		};
	}
	var selected = function(a, b) {
		if (a == null) return false;
		if (a[0] == "[") {
			return jsonParse(a).indexOf(b) >= 0;
		}
		return a.toUpperCase() == b.toUpperCase();
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
no_button_title = """
#title {
	width: 100%;
	display: block;
	box-shadow: none;
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
}"""

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
	color: white;
}
""" + no_button_title)
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
#title {
	color: black;
}
""")
helper.make_index("plot_index.html", """
	list_views = {
		"plot": "config/assets/plot_list.html",
		"visit": "config/assets/visit_list.html",
	}
	var todo = function() {alert("TODO")};
	menu = ["Plots Demo", null, [
		["View Plots", "plot", ""],
		["View Plots on a Map", "_js", function() { odkTables.openTableToMapView(null, "plot", null, null, "config/assets/plot_list.html#plot") }],
		["View Visits", "visit", ""],
		["View Reports", null, [
			["View Overall Data", "_html", "config/assets/view_overall_data.html"],
			["View Single Plot Data", "_js", todo],
			["View Comparison Data", null, [
				["Compare by plant type", "_js", todo],
				["Compare by soil type", "_js", todo],
				["Compare all plots", "_html", "config/assets/compare_all_plots.html"],
			]],
		]]
	]]
""", """
body {
	background: url('img/Agriculture_in_Malawi_by_Joachim_Huber_CClicense.jpg') no-repeat center/cover fixed;
}
""" + no_button_title)
helper.static_files.append("view_overall_data.html")
helper.static_files.append("compare_all_plots.html")

helper.make_table("plot_list.html", "", "", """
	var planting_cb = function(elem, planting) {
		if (planting == null || planting == "null") return "Not planting"
		return "Planting " + planting.toLowerCase() + " corn"
	}
	display_col = "plot_name";
	display_subcol = [[planting_cb, "planting", false], [", ","plot_size", false], [" hectares", null, true]];
	table_id = "plot";
""", "", "")
helper.make_table("visit_list.html", "", """
.li {
	width: 140px;
	height: 140px;
	margin: 5px;
	display: inline-block;
	border-radius: 10px;
	background-color: #E0FFFF;
	text-align: center;
	color: black;
}
body {
	color: white;
	background-color: #004656;
}
.status, .buttons/*, #navigation, #header, #search*/ {
	display: none;
}
#list {
	padding: 0;
}
.main-display {
	padding-top: 40px;
	padding-bottom: 15px;
}
""", """
	display_col = "date";
	display_col_wrapper = function display_col_wrapper(d, i, c) {
		return c.split("T")[0];
	}
	global_cols_to_select = "visit.*, plot.plot_name AS plot_name";
	global_join = "plot ON plot._id = visit.plot_id";
	display_subcol = [["", "plot_name", true]];
	table_id = "visit";
""", """
	stuff = document.getElementsByClassName("displays");
	for (var i = 0; i < stuff.length; i++) {
		stuff[i].style.width = "100%";
	}
""", "")



helper.make_detail("plot_detail.html", "", """
	body {
		text-align: center;
	}
	ul {
		list-style-type: none;
	}
	button {
		background-color: lightgrey;
		border: 3px solid darkgrey;
		color: black;
		border-radius: 6px;
		padding: 9px 30px;
	}
	#rest {
		font-size: 125%;
	}
""" + no_button_title, detail_helper_js + """
	main_col = "plot_name";
	table_id = "plot";
	global_which_cols_to_select = "plot.*, COUNT(*) AS num_visits"
	global_join = "visit ON plot._id = visit.plot_id"
	colmap = [
		["plot_name", function(e, c, d) { return c }],
		["location_latitude", "Latitude: "],
		["location_longitude", br("Longitude")],
		["planting", "Crop: "],
		["num_visits", function(e, c, d) {
			num = Number(c);
			return "<span style=\\"color: blue; text-decoration: underline;\\" onClick='openVisits(\\""+d.getData(0, 'plot_name')+"\\")'>" + c + " visit" + (num == 1 ? "" : "s") + "</span>";
		}],
		[null, function(e, c, d) { return makeIframe(); }],
		[null, function(e, c, d) { return makeButtons(); }],
	]
	document.getElementById("header").id = "title"
""", """
	var openVisits = function(id) {
		odkTables.openTableToListView(null, "visit", "plot_name = ?", [id], "config/assets/visit_list.html#visit/plot_name = ?/" + id);
	}
	var newVisit = function() {
		odkTables.addRowWithSurvey({}, "visit", "visit", null, {"plot_id": row_id, "date": odkCommon.toOdkTimeStampFromDate(new Date())});
	}
	var raw = "SELECT date, plant_height FROM visit WHERE plot_id = ?";
	var makeIframe = function() {
		var src = "plot_graph.html#bar/visit/" + JSON.stringify(["date", "plant_height"]) + "/"+raw+"/" + JSON.stringify([row_id]) + "/History of plot " + cached_d.getData(0, "plot_name");
		return "<iframe scrolling='no' style='width: 70vw; min-height: 100vw; border: none;' id='iframe' src='"+src+"' onLoad='doGraphQuery();' />";
	}
	var makeButtons = function() {
		return "<button onClick='newVisit()'>New Visit</button><br /><button onClick='alert(\\"TODO\\")'>Compare Plots</button>"
	}
	var doGraphQuery = function() {
		document.getElementById("iframe").contentWindow.show_value = function(num, percent) { return num + " cm" };
		odkData.arbitraryQuery("visit", raw, [row_id], 10000, 0, document.getElementById("iframe").contentWindow.success, function(e) {
			alert(e);
		});
	}
""")
helper.make_detail("visit_detail.html", "", "", detail_helper_js + """
	main_col = "date";
	table_id = "visit";
	global_which_cols_to_select = "visit.*, plot.plot_name AS plot_name"
	global_join = "plot ON plot._id = visit.plot_id"
	colmap = [
		["date", function(e, c, d) { return "Visit on " + c.split("T")[0]; }],
		["plot_name", true],
		["plant_height", br("Plant height", "cm")],
		["plant_health", function(e, c, d) {
			var retVal = "<b>Plant Health</b>:<br />";
			retVal += check("Good", function(e, c, d) { return selected(c, "good"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Fair", function(e, c, d) { return selected(c, "fair"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Bad", function(e, c, d) { return selected(c, "bad"); }, "radio")(e, c, d);
			return retVal;
		}],
		["soil", function(e, c, d) {
			var retVal = "<b>Soil</b>: <br />";
			retVal += check("Medium Sand", function(e, c, d) { return selected(c, "medium_sand"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Fine Sand", function(e, c, d) { return selected(c, "fine_sand"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Sandy Loam", function(e, c, d) { return selected(c, "sandy_loam"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Loam", function(e, c, d) { return selected(c, "loam"); }, "radio")(e, c, d);
			return retVal;
		}],
		["pests", function(e, c, d) {
			var retVal = "<b>Pests</b>: <br />"
			retVal += check("Earworm", function(e, c, d) { return selected(c, "earworm"); })(e, c, d) + "<br />";
			retVal += check("Stink Bug", function(e, c, d) { return selected(c, "stink_bug"); })(e, c, d) + "<br />";
			retVal += check("Beetle", function(e, c, d) { return selected(c, "beetle"); })(e, c, d) + "<br />";
			retVal += check("Cutworm", function(e, c, d) { return selected(c, "cutworm"); })(e, c, d) + "<br />";
			retVal += "<h3>Observations: </h3>"
			return retVal;
		}],
		["observations", function(e, c, d) { return c; }],
	]
""", "")

helper.make_graph("plot_graph.html", """
#bg {
	background-color: rgba(0, 0, 0, 0); /* transparent */
}
#title {
	display: none;
}
body {
	color: black;
}
canvas {
	padding-top: 32px;
}
""", """
window.iframeOnly = true;
window.all_colors = ["#85ac85", "#993300", "#37393d", "#e58755", "#ff8080", "#4891d9", "#cc2e2d", "#9900ff", "#1f4864"]
""")

