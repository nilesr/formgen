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

	display_subcol = [
		{"column": "ttName", "display_name": "Specialty: ", "newline": true},
		{"column": "District", "newline": false},
		{"column": "Neighborhood", "display_name": ", ", "newline": true}
	]
	display_col = "thName";
	table_id = "Tea_houses";
	allowed_group_bys = [
		{"column": "District"},
		{"column": "Neighborhood"},
		{"column": "State"},
		{"column": "WiFi"},
		{"column": "Hot"},
		{"column": "Iced"},
		{"column": "State"},
		{"column": "ttName", "display_name": "Specialty"},
	]
""", "", "")
helper.make_table("Tea_inventory_list.html", "", "", """
	global_join = "Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id"
	global_which_cols_to_select = "*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName"
	display_subcol = [["Tea House: ", "thName", true], ["Type: ", "ttName", true]];

	display_subcol = [
		{"column": "thName", "display_name": "Tea House: ", "newline": true},
		{"column": "ttName", "display_name": "Type: ", "newline": true}
	]
	display_col = "tiName";
	table_id = "Tea_inventory";
	allowed_group_bys = [
		{"column": "thName", "display_name": "House"},
		{"column": "ttName", "display_name": "Type"},
		{"column": "Iced"},
		{"column": "Hot"},
		{"column": "Bags"},
		{"column": "Loose_Leaf"}
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

	display_subcol = [
		{"column": "Origin", "display_name": "Origin: ", "newline": true},
		{"column": "_id", "callback": extras_cb, "newline": true}
	]
	display_col = "Name";
	table_id = "Tea_types";
	allowed_group_bys = [
		{"column": "Origin"},
		{"column": "Caffeinated"},
		{"column": "Fermented"}
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
	colmap = [
		{"column": "thName", "callback": function(e, c, d) { return c; }},
		{"column": "State"},
		{"column": "Region"},
		{"column": "District"},
		{"column": "Neighborhood", "callback": br("Neighborhood")},
		{"column": "ttName", "callback": br("Specialty")},
		{"column": "Date_Opened", "callback": opened},
		{"column": "Customers", "display_name": "Number of Customers: "},
		{"column": "Visits", "callback": br("Total Number of Visits")},
		{"column": "Location_latitude", "display_name": "Latitude (GPS): "},
		{"column": "Location_longitude", "callback": br("Longitude (GPS)", "<br /><br /><b>Services</b>:")},
		{"column": "Iced", "callback": check("Iced")},
		{"column": "Hot", "callback": check("Hot")},
		{"column": "WiFi", "callback": function(e, c, d) { return check("WiFi")(e, c, d) + "<br /><h3>Contact Information</h3>"; }},
		{"column": "Store_Owner"},
		{"column": "Phone_Number", "display_name": "Mobile number: "},
		{"column": "num_teas", "callback": function(e, c, d) {
			odkTables.setSubListView("Tea_inventory", "House_id = ?", [row_id], "config/assets/Tea_inventory_list.html#Tea_inventory/thName = ?/" + d.getData(0, "thName"));
			return "<span onClick='openTeas();' style='color: blue; text-decoration: underline;'>" + c + " tea" + (c.toString() == 1 ? "" : "s") + "</span>";
		}}
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
	colmap = [
		{"column": "tiName", "callback": function(e, c, d) { return c; }},
		{"column": "ttName", "display_name": "Type: "},
		{"column": "Price_8oz", "display_name": "8oz: "},
		{"column": "Price_12oz", "display_name": "12oz: "},
		{"column": "Price_16oz", "callback": function(e, c, d) { return "<b>16oz</b>: " + c + "<br /><br /><b>Offered</b>:"; }},
		{"column": "Iced", "callback": check("Iced")},
		{"column": "Hot", "callback": check("Hot")},
		{"column": "Loose_Leaf", "callback": check("Loose Leaf")},
		{"column": "Bags", "callback": check("Bags")}
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
	colmap = [
		{"column": "Name", "callback": function(e, c, d) { return c; }},
		{"column": "Origin", "callback": br("Origin", "<br /><br />Details:")},
		{"column": "Caffeinated", "callback": check("Caffeinated")},
		{"column": "Fermented", "callback": check("Fermented")}
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
		display_subcol = [
			{"column": "has_html", "callback": ack, "newline": true},
			{"column": "adminRegion", "display_name": "Admin region: ", "newline": true},
		]
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
	display_subcol = [{"column": "bird", "callback": cb, "newline": true}]
	display_col = "user_name"
	table_id = "selects";
""", "", "")

# client list view - untested
# 	add client - untested
# 	graph view - untested
# 	client detail view - untested
# 		styling - untested
# 		client forms - untested
# 			home locator - untested
# 				geopoints list view with where clause - untested
# 					map view - untested
# 					add waypoint - untested
# 					geopoint list view - untested
# 						styling - untested
# 			six week - untested
# 			six month - untested
# 		partner forms - untested
# 			partner screening - untested
# 			six month - untested

helper.make_tabs("index.html", """
	var tabs = [
		{"title": "General", "file": "general.html"},
		{"title": "Tea", "file": "th_index.html"},
		{"title": "Selects", "file": "selects_index.html"},
		{"title": "Plot", "file": "plot_index.html"},
		//["Hope", "hope_index.html"]
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
	menu = {"label": "Tea Demo", "type": "menu", "contents": [
		{"label": "View Tea Houses (try searching for \\"Hill\\")", "type": "list_view", "table": "Tea_houses"},
		{"label": "View Tea Houses on a Map", "type": "js", "function": function() { odkTables.openTableToMapView(null, "Tea_Houses", null, null, "config/assets/Tea_houses_list.html"); }},
		{"label": "New tea house", "type": "js", "function": newinstance("Tea_houses")},
		{"label": "View Teas", "type": "list_view", "table": "Tea_inventory"},
		{"label": "View Teas by Tea House", "type": "group_by", "table": "Tea_inventory", "grouping": "thName"},
		{"label": "Add Tea", "type": "js", "function": newinstance("Tea_inventory")},
		{"label": "View Tea Types", "type": "list_view", "table": "Tea_types"},
		{"label": "Add Tea Type", "type": "js", "function": newinstance("Tea_types")},
	]}
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
		"exampleForm": "config/assets/example_list.html",
		"datesTest": "config/assets/table.html"
	}
	var newinstance = function newinstance(table) {
		return function() {
			var id = newGuid();
			odkTables.launchHTML(null, "config/assets/formgen/"+table+"#" + id);
		}
	}
	menu = {"label": "Example Form", "type": "menu", "contents": [
		{"label": "New Instance", "type": "js", "function": newinstance("exampleForm")},
		{"label": "View Responses", "type": "list_view", "table": "exampleForm"},
		{"label": "Custom prompt types", "type": "js", "function": newinstance("datesTest")},
		{"label": "ETHIOPIA", "type": "js", "function": newinstance("Ethiopia_household")},
	]}
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
	menu = {"label": "Selects Demo", "type": "menu", "contents": [
		{"label": "New Instance", "type": "js", "function": function() { newinstance("selects"); }},
		{"label": "View Responses", "type": "list_view", "table": "selects"},
	]}
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
	menu = {"label": "Plots demo", "type": "menu", "contents": [
		{"label": "View Plots", "type": "list_view", "table": "plot"},
		{"label": "View Plots on a Map", "type": "js", "function": function() { odkTables.openTableToMapView(null, "plot", null, null, "config/assets/plot_map.html#plot"); }},
		{"label": "View Visits", "type": "list_view", "table": "visit"},
		{"label": "View Reports", "type": "menu", "contents": [
			{"label": "View Overall Data", "type": "html", "file": "config/assets/view_overall_data.html"},
			{"label": "View Single Plot Data", "type": "html", "file": "config/assets/single_plot_data_list.html"},
			{"label": "View Comparison Data", "type": "menu", "contents": [
				{"label": "Compare by plant type", "type": "html", "file": "config/assets/compare_list_planting.html#plot/STATIC/SELECT * FROM plot GROUP BY planting/[]/distinct values of planting"},
				{"label": "Compare by soil type", "type": "html", "file": "config/assets/compare_list_soil.html#plot/STATIC/SELECT * FROM plot JOIN visit ON visit.plot_id = plot._id GROUP BY soil/[]/distinct values of soil type"},
				{"label": "Compare all plots", "type": "html", "file": "config/assets/compare_all_plots.html"},
			]}
		]}
	]}
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
	display_subcol = [
		{"column": "planting", "callback": planting_cb, "newline": false},
		{"column": "plot_size", "display_name": ", ", "newline": false},
		{"display_name": " hectares", "newline": true},
	]
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
	display_subcol = [{"column": "plot_name"}];
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
		background-color: #E0FFFF;
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
		{"column": "plot_name", "callback": function(e, c, d) { return c; }},
		{"column": "location_latitude", "display_name": "Latitude: "},
		{"column": "location_longitude", "callback": br("Longitude")},
		{"column": "planting", "display_name": "Crop: "},
		{"column": "num_visits", "callback": function(e, c, d) {
			num = Number(c);
			return "<span style=\\"color: blue; text-decoration: underline;\\" onClick='openVisits(\\""+d.getData(0, 'plot_name')+"\\")'>" + c + " visit" + (num == 1 ? "" : "s") + "</span>";
		}},
		{"callback": makeIframe},
		{"callback": makeButtons},
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
helper.make_detail("visit_detail.html", "", """
	body {
		background-color: #E0FFFF;
	}
""", detail_helper_js + """
	main_col = "date";
	table_id = "visit";
	global_which_cols_to_select = "visit.*, plot.plot_name AS plot_name"
	global_join = "plot ON plot._id = visit.plot_id"
	colmap = [
		{"column": "date", "callback": function(e, c, d) { return "Visit on " + c.split("T")[0]; }},
		{"column": "plot_name"},
		{"column": "plant_height", "callback": br("Plant height", "cm")},
		{"column": "plant_health", "callback": function(e, c, d) {
			var retVal = "<b>Plant Health</b>:<br />";
			retVal += check("Good", function(e, c, d) { return selected(c, "good"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Fair", function(e, c, d) { return selected(c, "fair"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Bad", function(e, c, d) { return selected(c, "bad"); }, "radio")(e, c, d);
			return retVal;
		}},
		{"column": "soil", "callback": function(e, c, d) {
			var retVal = "<b>Soil</b>: <br />";
			retVal += check("Medium Sand", function(e, c, d) { return selected(c, "medium_sand"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Fine Sand", function(e, c, d) { return selected(c, "fine_sand"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Sandy Loam", function(e, c, d) { return selected(c, "sandy_loam"); }, "radio")(e, c, d) + "<br />";
			retVal += check("Loam", function(e, c, d) { return selected(c, "loam"); }, "radio")(e, c, d);
			return retVal;
		}},
		{"column": "pests", "callback": function(e, c, d) {
			var retVal = "<b>Pests</b>: <br />"
			retVal += check("Earworm", function(e, c, d) { return selected(c, "earworm"); })(e, c, d) + "<br />";
			retVal += check("Stink Bug", function(e, c, d) { return selected(c, "stink_bug"); })(e, c, d) + "<br />";
			retVal += check("Beetle", function(e, c, d) { return selected(c, "beetle"); })(e, c, d) + "<br />";
			retVal += check("Cutworm", function(e, c, d) { return selected(c, "cutworm"); })(e, c, d) + "<br />";
			retVal += "<h3>Observations: </h3>"
			return retVal;
		}},
		{"column": "observations", "callback": function(e, c, d) { return c; }}
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
#key {
	background-color: rgba(255, 255, 255, 0.5);
}
""", """
window.iframeOnly = true;
// stripped out the beige color, doesn't look good on a light background
window.all_colors = ["#85ac85", "#993300", "#37393d", "#e58755", "#ff8080", "#4891d9", "#cc2e2d", "#9900ff", "#1f4864"]
""")

helper.extend("plot_list.html", "plot_map.html", """
	forMapView = true;
""")

helper.extend("plot_list.html", "single_plot_data_list.html", """
		clicked = function clicked(table_id, row_id, d, i) {
			odkTables.launchHTML(null, "config/assets/plot_data.html#" + d.getData(i, "plot_name"));
		}
""")
helper.static_files.append("plot_data.html")
helper.make_table("compare_list_base.html", "", "", """
	display_subcol = [];
	table_id = "plot";
""", "", "")
helper.extend("compare_list_base.html", "compare_list_planting.html", """
		display_col = "planting";
		clicked = function clicked(table_id, row_id, d, i) {
			odkTables.launchHTML(null, "config/assets/plot_data.html#" + all_with_this_type[d.getData(i, "planting")].join("/"));
		}
		odkData.arbitraryQuery("plot", "SELECT plot_name, planting FROM plot", [], 10000, 0, function(d) {
			for (var i = 0; i < d.getCount(); i++) {
				var planting = d.getData(i, "planting");
				if (all_with_this_type[planting] === undefined) {
					all_with_this_type[planting] = []
				}
				all_with_this_type[planting] = all_with_this_type[planting].concat(d.getData(i, "plot_name"))
			}
		}, function(e) { alert(e); });
""", newJsGeneric = """
	var all_with_this_type = {};
""")
helper.extend("compare_list_base.html", "compare_list_soil.html", """
		display_col = "soil";
		clicked = function clicked(table_id, row_id, d, i) {
			odkTables.launchHTML(null, "config/assets/plot_data.html#" + all_with_this_type[d.getData(i, "soil")].join("/"));
		}
		odkData.arbitraryQuery("plot", "SELECT plot_name, soil AS planting FROM plot JOIN visit ON visit.plot_id = plot._id GROUP BY plot._id", [], 10000, 0, function(d) {
			for (var i = 0; i < d.getCount(); i++) {
				var planting = d.getData(i, "planting");
				if (all_with_this_type[planting] === undefined) {
					all_with_this_type[planting] = []
				}
				all_with_this_type[planting] = all_with_this_type[planting].concat(d.getData(i, "plot_name"))
			}
		}, function(e) { alert(e); });
""", newJsGeneric = """
	var all_with_this_type = {};
""")


helper.make_index("hope_index.html", """
	var send = function() {
		odkCommon.doAction(null, "org.opendatakit.services.sync.actions.activities.SyncActivity", {"componentPackage": "org.opendatakit.services", "componentActivity": "org.opendatakit.services.sync.actions.activities.SyncActivity"});
	}
	var newinstance = function newinstance(table, form) {
		return function() {
			var id = newGuid();
			if (form == table) form = "index";
			odkTables.launchHTML(null, "config/assets/formgen/"+table+"/" + form + ".html#" + id);
		}
	}
	list_views = {
		"femaleClients": "config/assets/femaleClients_list.html"
	}
	menu = {"label": "Hope Study" + "<br />xlsx not copied over yet, nothing will work", "type": "menu", "contents": [
		{"label": "Screen Female Client", "type": "js", "function": newinstance("femaleClients", "screenClient")},
		{"label": "Follow Up with Exsting Client", "type": "list_view", "table": "femaleClients"},
		{"label": "Send Data", "type": "js", "function": send}
	]};
""", """
	body {
		background-color: white;
		font-family: arial;
	}
	.button {
		color: #5c5c5c;
		width: 90%;
		margin-left: 5%;
		box-shadow: none;
		-webkit-box-shadow: none;
		background-color: #f1f1f1;
	}
	.button:first-child {
		border-left: 15px solid #003d5c;
		border-bottom: 1px solid #003d5c;
	}
	.button:nth-child(2) {
		border-left: 15px solid #006699;
		border-bottom: 1px solid #006699;
	}
	.button:nth-child(3) {
		border-left: 15px solid #66a3c2;
		border-bottom: 1px solid #66a3c2;
	}
	#title {
		font-weight: bold;
		margin-top: 20px;
		margin-bottom: 20px;
		font-size: 40pt;
		font-family: arial;
		border: none;
		background-color: white;
		color: #5c5c5c;
	}
""")
helper.make_table("femaleClients_list.html", "", "", """
	display_col = "client_id";
	display_subcol = [["Age: ", "age", true], ["Randomization: ", "randomization", true]];
	display_subcol = [
		{"column": "age", "display_name": "Age: ", "newline": true},
		{"column": "randomization", "display_name": "Randomization: ", "newline": true}
	]
	table_id = "femaleClients";

	document.getElementById("search").insertAdjacentHTML("beforeend", "<button onClick='addClient()' style='margin-left: 15%; min-height: 1.5em; width: 70%; display: block;'>Add Client</button>")
	document.getElementById("search").insertAdjacentHTML("beforeend", "<button onClick='graphView()' style='margin-left: 15%; min-height: 1.5em; width: 70%; display: block;'>Graph View</button>")
""", "", """
	var addClient = function() {
		odkTables.launchHTML(null, "config/assets/formgen/femaleClients/screenClient.html#" + newGuid());
	}
	var graphView = function() {
		odkTables.launchHTML(null, "config/assets/hope_graph_view.html");
	}
""")
helper.make_table("geopoints_list.html", "", """
	.header, .search {
		display: none;
	}
""", """
	display_col = "client_id";
	global_join = "femaleClients ON femaleClients.client_id = geopoints.client_id"
	global_which_cols_to_select = "geopoints.*"
	var transpo = function(e, c, d, i) {
		if (c == null) c = d.getData(i, "transportation_mode_other");
		return "Transportation: " + c;
	}
	display_subcol = [["Step: ", "step", true], [transpo, "transportation_mode", true]];
	display_subcol = [
		{"column": "step", "display_name": "Step: ", "newline": true},
		{"column": "transportation_mode", "callback": transpo, "newline": true}
	]
	table_id = "geopoints";

	var add = document.createElement("button");
	add.style.display = "block";
	add.style.width = "70%";
	add.innerText = "Add Waypoint";
	add.addEventListener("click", function() {
		alert("TODO"); // CACHED_D DOESN'T EXIST THIS IS A LIST VIEW
		var id = newGuid();
		odkData.addRow("geopoints", {"client_id": cached_d.getData(0, "client_id"), "_id": id})
		odkTables.launchHTML(null, "config/assets/formgen/geopoints/index.html#" + id);
	});
	var map = document.createElement("button");
	map.style.display = "block";
	map.style.width = "70%";
	map.innerText = "Map View";
	map.addEventListener("click", function() {
		alert("TODO");
		odkTables.openTableToMapView(null, global_where_clause, [global_where_arg], clean_href() + "#" + table_id + "/" + global_where_clause + "/" + global_where_arg);
	});
	document.insertBefore(map, document.getElementById("list"));
	document.insertBefore(add, document.getElementById("list"));
""", "", "")
helper.static_files.append("hope_graph_view.html")
helper.make_detail("femaleClients_detail.html", """
	<button disabled class='title-button'>Client Forms</button>
		<button onClick='homeLocator();' class='smaller-button'>Home Locator</button>
		<button onClick='newinstance("femaleClients", "client6Week");' class='smaller-button'>Six Week Follow-Up</button>
		<button onClick='newinstance("femaleClients", "client6Month");' class='smaller-button'>Six Month Follow-Up</button>
	<button disabled class='title-button'>Partner Forms</button>
		<button onClick='newinstance("maleClients", "screenPartner");' class='smaller-button'>Partner Screening</button>
		<button onClick='newinstance("maleClients", "partner6Month");' class='smaller-button'>Six Month Follow-Up</button>
""", """
	body {
		text-align: center;
	}
	ul {
		list-style-type: none;
		border: 1px solid black;
		opacity: 0.6;
	}
	.title-button, .smaller-button {
		display: block;
	}
	.title-button {
		width: 80%;
		padding-left: 10%;
		background-color: #003d5c;
		color: white;
	}
	.smaller-button {
		width: 60%;
		padding-left: 20%;
		background-color: lightgrey;
	}
""", """
	main_col = "client_id";
	table_id = "femaleClients";
	// TODO NEEDS A GLOBAL JOIN FOR THE PARTNER ID
	colmap = [
		["client_id", function(e, c, d) { return c }],
		["age", "AGE"],
		["randomization", "RANDOMIZATION"]
	];
	colmap = [
		{"column": "client_id", callback: function(e, c, d) { return c; }},
		{"column": "age", "display_name": "AGE"},
		{"column": "randomization", "display_name": "RANDOMIZATION"},
	];
	var newinstance = function(table, form) {
		if (form == table) form = "index";
		odkTables.launchHTML(null, "config/assets/formgen/" + table + "/" + form + ".html#" + newGuid());
	};
	var homeLocator = function homeLocator() {
		var where = "client_id = ?"
		var args = [cached_d.getData(0, "client_id")]
		odkTables.openTableToListView(null, "geopoints", where, args, "config/assets/geopoints_list.html#geopoints/" + where + "/" + args[0]);
	}
""","");
helper.make_detail("geopoints_detail.html", "", """
	body {
		text-align: center;
	}
	ul {
		list-style-type: none;
		border: 1px solid black;
		opacity: 0.6;
	}
""", """
	main_col = "client_id";
	table_id = "geopoints";
	colmap = [
		{"column": "client_id", "callback": function(e, c, d) { return c; }},
		{"column": "transportation_mode", "callback": function(e, c, d) {
			if (c == null) c = d.getData(0, "transportation_mode_other")
			return "MODE OF TRANSPORTATION: " + c;
		}},
		{"column": "description", "display_name": "DESCRIPTION"},
		{"column": "coordinates_latitude", "callback": function(e, c, d) {
		 	return "COORDINATES: " + c + " " + d.getData(0, "coordinates_longitude");
		}}
	]
	var newinstance = function(table, form) {
		if (form == table) form = "index";
		odkTables.launchHTML(null, "config/assets/formgen/" + table + "/" + form + ".html#" + newGuid());
	};
	var homeLocator = function homeLocator() {
		var where = "client_id = ?"
		var args = [cached_d.getData(0, "client_id")]
		odkTables.openTableToListView(null, "geopoints", where, args, "config/assets/geopoints_list.html#geopoints/" + where + "/" + args[0]);
	}
""","");

