# coding=utf-8
import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();


global_allowed_tables = "allowed_tables = [];\n"
global_block_add = "document.getElementById(\"add\").style.display = \"none\";\n"
hallway = """
body {
	background: url('/coldchain/config/assets/img/hallway.jpg') no-repeat center/cover fixed;
}"""
helper.make_table("aa_refrigerator_types_list.html", "", """
	.refrig-img {
		max-width: 45%;
	}
	.li {
		font-size: 150%;
	}
	.buttons > button {
		font-size: 22px;
	}
	.img-wrapper {
		text-align: center;
	}
""", global_allowed_tables + global_block_add + """
	var makepicture = function makepicture(e, c, d, i) {
		if (c == null || c == "null") return "No picture available";
		return "<div class='img-wrapper'><img class='refrig-img' src='" + odkCommon.getRowFileAsUrl(table_id, d.getData(i, "_id"), c) + "' /></div>";
	}
	//display_subcol = [["Manufacturer: ", "manufacturer", true], ["Model ID: ", "model_id", true], [makepicture, "refrigerator_picture_uriFragment", true]];
	display_subcol = [
		{"column": "manufacturer", "display_name": "Manufacturer: ", "newline": true},
		{"column": "model_id", "display_name": "Model ID: ", "newline": true},
		{"column": "refrigerator_picture_uriFragment", "callback": makepicture, "newline": true}
	]
	//allowed_group_bys = ["manufacturer", "climate_zone", "equipment_type"]
	allowed_group_bys = [
		{"column": "manufacturer"},
		{"column": "climate_zone"},
		{"column": "equipment_type"}
	]
	display_col = "catalog_id"
	table_id = "refrigerator_types";
""", """
	var stuff = document.getElementsByClassName("buttons");
	for (var i = 0; i < stuff.length; i++) {
		stuff[i].style.display = "none";
	}
	stuff = document.getElementsByClassName("displays");
	for (var i = 0; i < stuff.length; i++) {
		stuff[i].style.width = "100%";
	}
""", "")

helper.make_table("aa_refrigerators_list.html", "", "", global_allowed_tables + global_block_add + """
	global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
	//display_subcol = [["", "model_id", true], ["Healthcare Facility: ", "facility_name", true]];
	display_subcol = [
		{"column": "model_id", "newline": true},
		{"column": "facility_name", "display_name": "Healthcare Facility: ", "newline": true}
	]
	display_col = "tracking_id"
	table_id = "refrigerators";
	//allowed_group_bys = [["facility_row_id", "Facility"], ["model_row_id", "Model"], "reason_not_working", ["utilization", "Use"], "working_status", "year"]
	allowed_group_bys = [
		{"column": "facility_row_id", "display_name": "Facility"},
		{"column": "model_row_id", "display_name": "Model"},
		{"column": "reason_not_working"},
		{"column": "utilization", "display_name": "Use"},
		{"column": "working_status"},
		{"column": "year"}
	]
""", "", "")

#hf_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE facility_row_id = health_facility._id) AS refrigerator_count"
hf_cols_to_select = "*"

helper.make_table("aa_health_facility_list.html", "", "", global_allowed_tables + global_block_add + """
	display_col = "facility_name"
	table_id = "health_facility";
	//allowed_group_bys = ["admin_region", "climate_zone", "delivery_type", "electricity_source", ["facility_ownership", "Ownership"], "facility_type", "storage_type", "solar_suitable_climate", "solar_suitable_site", "vaccine_supply_mode", "vaccine_reserve_stock_requirement"];
	allowed_group_bys = [
		{"column": "admin_region"},
		{"column": "climate_zone"},
		{"column": "delivery_type"},
		{"column": "electricity_source"},
		{"column": "facility_ownership", "display_name": "Ownership"},
		{"column": "facility_type"},
		{"column": "storage_type"},
		{"column": "solar_suitable_climate"},
		{"column": "solar_suitable_site"},
		{"column": "vaccine_supply_mode"},
		{"column": "vaccine_reserve_stock_requirement"},
	]

	global_which_cols_to_select = \""""+hf_cols_to_select+"""\"
	//display_subcol = [
		//["Facility ID: ", "facility_id", true],
		//["Refrigerators: ", "refrigerator_count", true]
	//]
	display_subcol = [
		{"column": "facility_id", "display_name": "Facility ID: ", "newline": true},
	]
	document.getElementById("add").style.display = "none";
""", "", "")

helper.make_table("aa_m_logs_list.html", "", "", global_allowed_tables + global_block_add + """
	var notes_cb = function notes_cb(e, notes) {
		if (notes == undefined || notes == null) {
			return "";
		}
		return notes;
	}
	display_col_wrapper = function display_col_wrapper(d, i, c) {
		return c.split("T")[0];
	}
	display_col = "date_serviced"
	//display_subcol = [["", "refs_tracking_number", true], [notes_cb, "notes", true]];
	display_subcol = [
		{"column": "refs_tracking_number", "newline": true},
		{"column": "notes", "callback": notes_cb, "newline": true},
	]
	allowed_group_bys = [];
	table_id = "m_logs";
	global_join = "refrigerators ON refrigerators.refrigerator_id = m_logs.refrigerator_id"
	global_which_cols_to_select = "*, refrigerators.refrigerator_id AS refs_refid, refrigerators.tracking_id AS refs_tracking_number"
	document.getElementById("add").style.display = "none";
""", "", "")


helper.make_detail("aa_refrigerators_detail.html", """
	<div class="main-col-wrapper">
		<div id="inject-tracking_id">Loading...</div>
	</div>
	<div class='h4-wrapper'><h4 id='bfi'><h4></div>
	<ul>
		<li id='inject-facility_name'></li>
		<li id='inject-year'></li>
		<li id='inject-working_status'></li>
		<li id='inject-reason_not_working'></li>
		<li id='inject-model_id'></li>
		<!--
			<li id='inject-tracking_id'></li>
		-->
		<li id='inject-voltage_regulator'></li>
		<li id='inject-date_serviced'></li>
	</ul>
	<button disabled id='open_model'></button>
	<!--
		<br />
		<button disabled id='open_hf'></button>
	-->
	<br />
	<button disabled id='add_m_log'></button>
	<br />
	<button disabled id='view_m_log'></button>
	<br />
		""", open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + global_allowed_tables + """
	document.getElementById("bfi").innerText = _tu("Basic Refrigerator Information")
	var model_callback = function model_callback(e, c, d) {
		var btn = document.getElementById("open_model");
		btn.innerText = _tu("Model Information");
		var model = d.getData(0, "catalog_id"); // from join, not actually the model id
		var model_row_id = d.getData(0, "model_row_id");
		btn.disabled = false;
		btn.addEventListener("click", function() {
			odkTables.openDetailView(null, "refrigerator_types", model_row_id);
		});
		build_generic_callback("model_id", true, _tu("Model ID"))(e, c, d)
		return "";
	}
	var hf_callback = function hf_callback(e, c, d) {
		/*
			var btn = document.getElementById("open_hf");
			btn.innerText = _tu("Health Facility Information");
			var hf = d.getData(0, "facility_name"); // from join, not actually the hf id
			var hf_row_id = d.getData(0, "facility_row_id");
			btn.disabled = false;
			btn.addEventListener("click", function() {
				odkTables.openDetailView(null, "health_facility", hf_row_id, "config/assets/aa_health_facility_detail.html#health_facility/" + hf_row_id);
			});
		*/
		build_generic_callback("facility_name", true, "Facility")(e, c, d)
		document.getElementById("add_m_log").disabled = false;
		document.getElementById("add_m_log").innerText = _tu("Add Maintenance Record");
		var defaults = {"refrigerator_id": d.getData(0, "refrigerator_id"), "date_serviced": odkCommon.toOdkTimeStampFromDate(new Date())};
		defaults["_default_access"] = d.getData(0, "_default_access");
		defaults["_group_read_only"] = d.getData(0, "_group_read_only");
		defaults["_group_modify"] = d.getData(0, "_group_modify");
		defaults["_group_privileged"] = d.getData(0, "_group_privileged");
		document.getElementById("add_m_log").addEventListener("click", function add_m_log() {
			if (allowed_tables.indexOf("m_logs") >= 0) {
				var id = newGuid();
				odkData.addRow("m_logs", defaults, id, function() {
					// Escape the LIMIT 1
					odkData.arbitraryQuery("m_logs", "UPDATE m_logs SET _savepoint_type = ? WHERE _id = ?;--", ["INCOMPLETE", id], 100, 0, function success(d) {
						odkTables.launchHTML({}, "config/assets/formgen/m_logs#" + id);
					}, null);
				});
			} else {
				odkTables.addRowWithSurvey({}, "m_logs", "m_logs", null, defaults);
			}
		});
		document.getElementById("view_m_log").disabled = false;
		document.getElementById("view_m_log").innerText = _tu("View all maintenance logs")
		document.getElementById("view_m_log").addEventListener("click", function add_m_log() {
			odkTables.launchHTML(null, "config/assets/aa_m_logs_list.html#m_log/STATIC/SELECT *, refrigerators.refrigerator_id AS refs_refid, refrigerators.tracking_id AS refs_tracking_number FROM m_logs JOIN refrigerators ON refrigerators.refrigerator_id = m_logs.refrigerator_id WHERE refs_refid = ?/" + JSON.stringify([d.getData(0, "refrigerator_id")]) + "/maintenance records for the selected refrigerator");
		});

		return "";
	}

	main_col = "";
	global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
	global_which_cols_to_select = "*"
	var subquery = "(SELECT date_serviced FROM m_logs WHERE m_logs.refrigerator_id = refrigerators.refrigerator_id AND m_logs._savepoint_type != 'INCOMPLETE' ORDER BY date_serviced DESC LIMIT 1)"
	global_which_cols_to_select = global_which_cols_to_select.concat(", (CASE WHEN "+subquery+" IS NOT NULL THEN "+subquery+" ELSE 'No Records' END) as date_serviced")
	colmap = [
		{"column": "facility_name", "callback": hf_callback},
		{"column": "year", "callback": build_generic_callback("year", true, "Year Installed")},
		{"column": "working_status", "callback": build_generic_callback("working_status", true, "Status")},
		{"column": "reason_not_working", "callback": build_generic_callback("reason_not_working", true)},
		{"column": "model_row_id", "callback": model_callback},
		{"column": "tracking_id", "callback": build_generic_callback("tracking_id", false, "Tracking Number")},
		{"column": "voltage_regulator", "callback": build_generic_callback("voltage_regulator", true)},
		{"column": "date_serviced", "callback": build_generic_callback("date_serviced", function(i) {
			if (i == "No Records") {
				return _tu(i);
			}
			return i.split("T")[0];
		}, _tu("Date Serviced"))}
	]
""", "")

helper.make_detail("aa_refrigerator_types_detail.html", """
	<div class="main-col-wrapper">
		<div id="inject-model_id" style='line-height: 3em;'>Loading...</div>
		<div id="inject-catalog_id" style='line-height: 3em;'>Loading...</div>
	</div>
	<div class="h4-wrapper"><h4 id='mi'></h4></div>
	<ul>
		<li id='inject-manufacturer'></li>
		<li id='inject-power_source'></li>
		<li id='inject-refrigerator_gross_volume'></li>
		<li id='inject-freezer_gross_volume'></li>
		<li id='inject-equipment_type'></li>
		<li id='inject-climate_zone'></li>
		<li id='inject-refrigerator_net_volume'></li>
		<li id='inject-freezer_net_volume'></li>
	</ul>
	<div id="inject-refrigerator_picture" style="text-align: center;"></div>
	<div style="text-align: center;">
		<button disabled id='open_model'>Loading...</button>
	</div>
		""", open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + global_allowed_tables + """

	document.getElementById("mi").innerText = _tu("Model Information")
	document.getElementById("edit").style.display = "none";
	document.getElementById("delete").style.display = "none";

	main_col = "";
	global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE model_row_id = refrigerator_types._id) as refrig_with_this_model_count"
	var mid_callback = function mid_callback(e, c, d) {
		generic_callback(e, c, d, "model_id", true);
		document.getElementById("open_model").innerHTML = _tu("View All ") + c + _tu(" Refrigerators (<span id='refrig_with_this_model_count'>Loading...</span>)")
		document.getElementById("open_model").disabled = false;
		document.getElementById("open_model").addEventListener("click", function click() {
			odkTables.launchHTML(null, "config/assets/aa_refrigerators_list.html#refrigerators/model_row_id = ?/" + row_id);
		});
		document.getElementById("refrig_with_this_model_count").innerText = d.getData(0, "refrig_with_this_model_count");
	}
	colmap = [
		{"column": "manufacturer", "callback": build_generic_callback("manufacturer", true)},
		{"column": "power_source", "callback": build_generic_callback("power_source", function(i) { return pretty(jsonParse(i).join(", ")); })},
		{"column": "refrigerator_gross_volume", "callback": build_generic_callback("refrigerator_gross_volume", " litres")},
		{"column": "freezer_gross_volume", "callback": build_generic_callback("freezer_gross_volume", " litres")},
		{"column": "equipment_type", "callback": build_generic_callback("equipment_type", true)},
		{"column": "climate_zone", "callback": build_generic_callback("climate_zone", true)},
		{"column": "refrigerator_net_volume", "callback": build_generic_callback("refrigerator_net_volume", " litres")},
		{"column": "freezer_net_volume", "callback": build_generic_callback("freezer_net_volume", " litres")},
		{"column": "model_id", "callback": mid_callback},
		{"column": "catalog_id", "callback": build_generic_callback("catalog_id", true)},
		{"column": "refrigerator_picture", "callback": function(e,c,d){document.getElementById("inject-refrigerator_picture").appendChild(c)}}
	]
""", "")




helper.make_detail("aa_health_facility_detail.html", """
	<div class="main-col-wrapper">
		<div id="inject-facility_name">Loading...</div>
	</div>
	<div class="h4-wrapper"><h4 id="bfi"></h4></div>
	<ul>
		<li id='inject-facility_id'></li>
		<li id='inject-facility_type'></li>
		<li id='inject-facility_ownership'></li>
		<li id='inject-facility_population'></li>
		<li id='inject-facility_coverage'></li>
		<li id='inject-admin_region'></li>
	</ul>
	<div class="h4-wrapper"><h4 id="pi"></h4></div>
	<ul>
		<li id='inject-electricity_source'></li>
		<li id='inject-grid_power_availability'></li>
		<li id='inject-gas_availability'></li>
		<li id='inject-kerosene_availability'></li>
		<li id='inject-solar_suitable_climate'></li>
		<li id='inject-solar_suitable_site'></li>
	</ul>
	<div class="h4-wrapper"><h4 id="locationi"></h4></div>
	<ul>
		<li id='inject-Location_latitude'></li>
		<li id='inject-Location_longitude'></li>
		<li id='inject-climate_zone'></li>
	</ul>
	<div class="h4-wrapper"><h4 id="stocki"></h4></div>
	<ul>
		<li id='inject-distance_to_supply'></li>
		<li id='inject-vaccine_supply_interval'></li>
		<li id='inject-vaccine_reserve_stock_requirement'></li>
		<li id='inject-vaccine_supply_mode'></li>
	</ul>
	<div style="text-align: center;">
		<button disabled id='refrigerator_inventory'>Loading...</button>
		<br />
		<button id="addref"></button>
	</div>
		""", open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + global_allowed_tables + """

	main_col = "";
	global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE facility_row_id = health_facility._id) as refrig_with_this_hfid_count"
	var fname_callback = function fname_callback(e, c, d) {
		generic_callback(e, c, d, "facility_name", true, "Health Facility ID");
		document.getElementById("refrigerator_inventory").innerHTML = _tu("Refrigerator Inventory (<span id='refrig_with_this_hfid_count'>Loading...</span>)")
		document.getElementById("refrigerator_inventory").disabled = false;
		document.getElementById("refrigerator_inventory").addEventListener("click", function click() {
			odkTables.launchHTML(null, "config/assets/aa_refrigerators_list.html#refrigerators/health_facility.facility_name = ?/" + d.getData(0, "facility_name"));
		});
		document.getElementById("refrig_with_this_hfid_count").innerText = d.getData(0, "refrig_with_this_hfid_count");
		document.getElementById("addref").addEventListener("click", function() {
			var defaults = {"facility_row_id": d.getData(0, "_id")};
			defaults["refrigerator_id"] = newGuid();
			defaults["_default_access"] = d.getData(0, "_default_access");
			defaults["_group_read_only"] = d.getData(0, "_group_read_only");
			defaults["_group_modify"] = d.getData(0, "_group_modify");
			defaults["_group_privileged"] = d.getData(0, "_group_privileged");
			if (allowed_tables.indexOf("refrigerators") >= 0) {
				var id = newGuid();
				odkData.addRow("refrigerators", defaults, id, function() {
					// Escape the LIMIT 1
					odkData.arbitraryQuery("refrigerators", "UPDATE refrigerators SET _savepoint_type = ? WHERE _id = ?;--", ["INCOMPLETE", id], 100, 0, function success(d) {
						odkTables.launchHTML({}, "config/assets/formgen/refrigerators#" + id);
					}, null);
				});
			} else {
				odkTables.addRowWithSurvey({}, "refrigerators", "refrigerators", null, defaults);
			}
		});
	}
	colmap = [
		{"column": 'facility_name', "callback": fname_callback},
		{"column": 'facility_id', "callback": build_generic_callback("facility_id", true, "Health Facility ID")},
		{"column": 'facility_type', "callback": build_generic_callback("facility_type", true)},
		{"column": 'facility_ownership', "callback": build_generic_callback("facility_ownership", true, "Ownership")},
		{"column": 'facility_population', "callback": build_generic_callback("facility_population", true, "Population")},
		{"column": 'facility_coverage', "callback": build_generic_callback("facility_coverage", "%", "Coverage")},
		{"column": 'admin_region', "callback": build_generic_callback("admin_region", true, "Admin Region")},
		{"column": 'electricity_source', "callback": build_generic_callback("electricity_source", true)},
		{"column": 'grid_power_availability', "callback": build_generic_callback("grid_power_availability", true, "Grid Availability")},
		{"column": 'gas_availability', "callback": build_generic_callback("gas_availability", true)},
		{"column": 'kerosene_availability', "callback": build_generic_callback("kerosene_availability", true)},
		{"column": 'solar_suitable_climate', "callback": build_generic_callback("solar_suitable_climate", true, "Solar Suitable Climate?")},
		{"column": 'solar_suitable_site', "callback": build_generic_callback("solar_suitable_site", true, "Solar Suitable Site?")},
		{"column": 'Location_latitude', "callback": build_generic_callback("Location_latitude", true, "Latitude (GPS)")},
		{"column": 'Location_longitude', "callback": build_generic_callback("Location_longitude", true, "Longitude (GPS)")},
		{"column": 'climate_zone', "callback": build_generic_callback("climate_zone", true, "Climate")},
		{"column": 'distance_to_supply', "callback": build_generic_callback("distance_to_supply", true, "Distance to Supply Point")},
		{"column": 'vaccine_supply_interval', "callback": build_generic_callback("vaccine_supply_interval", true)},
		{"column": 'vaccine_reserve_stock_requirement', "callback": build_generic_callback("vaccine_reserve_stock_requirement", true, "Vaccine Reserve Stock Req")},
		{"column": 'vaccine_supply_mode', "callback": build_generic_callback("vaccine_supply_mode", true)},
	]
	document.getElementById("bfi").innerText = _tu("Basic Facility Information");
	document.getElementById("pi").innerText = _tu("Power Information");
	document.getElementById("locationi").innerText = _tu("Location Information");
	document.getElementById("stocki").innerText = _tu("Stock Information");
	document.getElementById("addref").innerText = _tu("Add Refrigerator");
""", "")
helper.make_detail("aa_m_logs_detail.html", "", "", """
	main_col = "refs_tracking_number";
	colmap = [
		{"column": 'refs_tracking_number', "callback": "Tracking Number: "},
		{"column": 'date_serviced', "callback": function(e, c, d) { return "<b>" + _tu("Date Serviced") + ":</b> " + c.split("T")[0]; }},
		{"column": 'notes', "callback": function(e, c, d) {
			if (c == null || c == "null") return "";
			return "<b>" + _tu("Notes: ") + "</b>" + c;
		}}
	]
	global_join = "refrigerators ON refrigerators.refrigerator_id = m_logs.refrigerator_id"
	global_which_cols_to_select = "*, refrigerators.tracking_id AS refs_tracking_number"
""", "")

import sqlite3, csv
db = sqlite3.connect(":memory:")
c = db.cursor()
c.execute("CREATE TABLE t1 (regionLevel1, regionLevel2);")
c.execute("CREATE TABLE t2 (regionLevel2, regionLevel3);")
rows = [[x["regionLevel1"], x["regionLevel2"]] for x in csv.DictReader(open("regions1-2.csv", "r"))]
c.executemany("INSERT INTO t1 (regionLevel1, regionLevel2) VALUES (?, ?);", rows);
rows = [[x["regionLevel2"], x["regionLevel3"]] for x in csv.DictReader(open("regions2-3.csv", "r"))]
c.executemany("INSERT INTO t2 (regionLevel2, regionLevel3) VALUES (?, ?);", rows);

import collections
hierarchy = collections.defaultdict(lambda: set())
levels = ["regionLevel1", "regionLevel2", "adminRegion"]
for i in range(len(levels) - 1):
	for row in c.execute("SELECT regionLevel1, t1.regionLevel2, regionLevel3 FROM t1 JOIN t2 ON t1.regionLevel2 = t2.regionLevel2;"):
		hierarchy["_start"].add(row[0])
		if row[i] != row[i + 1]:
			hierarchy[row[i]].add(row[i+1])
def make_admin_region(val):
	return [val, "_html", "config/assets/admin_region.html#" + val + ":"];
def make_map(val, depth = 0):
	if len(hierarchy[val]) == 0: return make_admin_region(val)
	# These two lines aren't needed, but they make it so the order in the list doesn't change every time you regenerate
	hierarchy[val] = list(hierarchy[val])
	hierarchy[val].sort()
	submenu = [make_map(hierarchy[val][i], depth + 1) for i in range(len(hierarchy[val]))]
	# if depth >= 2:
	if depth >= 2 or val == "North":
		submenu = [["Filter By Type", "_html", "config/assets/admin_region_filter.html#" + val + ":"]] + submenu
	return [val, None, submenu];
#print(hierarchy)
as_list = make_map("_start")
# as_list now like ["_start", null, [...]]
import json
as_list[0] = "PATH Cold Chain Demo"
# as_list now like ["PATH Cold Chain Demo", null, [...]]
# append to the [...] our own option

as_list[2].append(
	["All Regions", None, [[val[0], "_html", "config/assets/admin_region.html#" + val[0] + ":"] for val in c.execute("SELECT regionlevel3 from t2;")]]
)
helper.static_files.append("inv_by_grid_power.html");
helper.static_files.append("inv_by_age.html");
as_list[2].append(
	{"label": "View Data", "type": "menu", "contents": [
		{"label": "View Health Facilities", "type": "menu", "contents": [
			#["Filter By Region/Type", "_html", "config/assets/index.html"],
			{"label": "Search By Name/ID", "type": "list_view", "table": "health_facility"}
		]},
		{"label": "View Inventory", "type": "menu", "contents": [
			{"label": "Refrigerator Age", "type": "html", "page": "config/assets/inv_by_age.html"},
			{"label": "Facility Grid Power Availability", "type": "html", "page": "config/assets/inv_by_grid_power.html"}
		]},
		{"label": "View Refrigerator Models", "type": "group_by", "table": "refrigerator_types", "grouping": "equipment_type"},
		{"label": "More Options", "type": "menu", "contents": [
			{"label": "Health Facilities (Advanced)", "type": "menu", "contents": [
				{"label": "View All", "type": "list_view", "table": "health_facility"},
				{"type": "group_by", "table": "health_facility", "grouping": "admin_region"},
				{"type": "group_by", "table": "health_facility", "grouping": "facility_type"},
				{"label": "Ownership", "type": "group_by", "table": "health_facility", "grouping": "ownership"},
				{"label": "More", "type": "menu", "contents": [
					{"type": "group_by", "table": "health_facility", "grouping": "delivery_type"},
					{"type": "group_by", "table": "health_facility", "grouping": "electricity_source"},
					{"type": "group_by", "table": "health_facility", "grouping": "storage_type"},
					{"type": "group_by", "table": "health_facility", "grouping": "solar_suitable_climate"},
					{"type": "group_by", "table": "health_facility", "grouping": "solar_suitable_site"},
					{"type": "group_by", "table": "health_facility", "grouping": "vaccine_supply_mode"},
					{"label": "By Reserve Stock Requirement", "type": "group_by", "table": "health_facility", "grouping": "vaccine_reserve_stock_requirement"}
				]}
			]},
			{"type": "menu", "label": "Refrigerators (Advanced)", "contents": [
				{"label": "View All", "type": "list_view", "table": "refrigerators"},
				{"label": "By Facility", "type": "group_by", "table": "refrigerators", "grouping": "facility_name"},
				{"label": "By Model", "type": "group_by", "table": "refrigerators", "grouping": "catalog_id"},
				{"type": "group_by", "table": "refrigerators", "grouping": "year"},
				{"label": "More", "type": "menu", "contents": [
					{"label": "By Use", "type": "group_by", "table": "refrigerators", "grouping": "utilization"},
					{"type": "group_by", "table": "refrigerators", "grouping": "working_status"},
					{"type": "group_by", "table": "refrigerators", "grouping": "reason_not_working"},
				]}
			]},
			{"label": "Models (Advanced)", "type": "menu", "contents": [
				{"label": "View All", "type": "list_view", "table": "refrigerators_type"},
				{"type": "group_by", "table": "refrigerator_types", "grouping": "manufacturer"},
				{"type": "group_by", "table": "refrigerator_types", "grouping": "equipment_type"},
				{"label": "More", "type": "menu", "contents": [
					{"type": "group_by", "table": "refrigerator_types", "grouping": "climate_zone"},
				]}
			]}
		]}
	]}
)
as_list = {"label": as_list[0], "type": "menu", "contents": as_list[2]}

helper.make_index("index.html", """
list_views = {
	"health_facility": "config/assets/aa_health_facility_list.html",
	"refrigerators": "config/assets/aa_refrigerators_list.html",
	"refrigerator_types": "config/assets/aa_refrigerator_types_list.html",
}
menu = """+json.dumps(as_list)+""";
var addhf = function addhf() {
	odkTables.addRowWithSurvey(null, "health_facility", "health_facility", null, null);
}
var addrf = function addrf() {
	odkTables.addRowWithSurvey(null, "refrigerators", "refrigerators", null, null);
}
menu["contents"] = menu["contents"].concat(0);
menu["contents"][menu["contents"].length - 1] = {"label": "Administrative Actions", "type": "menu", "contents": [
		//["Add Health Facility", "_js", addhf],
		{"label": "Add Health Facility", "type": "html", "page": "config/assets/add_hf.html"},
		//["Add Refrigerator", "_js", addrf]
	]}

var make_path_from_string = function make_path_from_string(str, incomplete) {
	var submenu = make_submenu(incomplete);
	if (submenu["label"].toUpperCase() == str.toUpperCase()) {
		return incomplete;
	}
	if (submenu["type"] != "menu") {
		return null;
	}
	for (var i = 0; i < submenu["contents"].length; i++) {
		var found = make_path_from_string(str, incomplete.concat(i));
		if (found != null) {
			return found;
		}
	}
	return null;
}
if (window.location.hash.substr(1).length == 0) {
	var region_as_role = "";
	var all_regions = [];
	var redirect = function redirect() {
		if (region_as_role.length == 0) {
			// TODO LOCKOUT
			return;
		}
		var path = make_path_from_string(region_as_role, [])
		// TODO CHECK IF path IS NULL, IF IT IS WE COULDN'T FIND THE REGION
		menu_path = path;
		doMenu();
	}
	odkData.getDefaultGroup(function(r) {
		r = r.getDefaultGroup();
		if (r == null) {
			menu = ["Not logged in!", null, [
				["Log in", "_js", function() {
					odkCommon.doAction(null, "org.opendatakit.services.sync.actions.activities.SyncActivity", {"extras": {"showLogin": "true"}, "componentPackage": "org.opendatakit.services", "componentActivity": "org.opendatakit.services.sync.actions.activities.SyncActivity"});
				}]
			]];
			doMenu();
		} else if (r.indexOf("GROUP_REGION_") == 0) {
			var region = r.replace("GROUP_REGION_", "");
			// replace all occurrences
			region = region.replace(/_/g, " ");
			region_as_role = region;
			redirect();
		}
	});
}
		""", hallway)

def make_val_accepting_index(code):
	return """
	var hash = window.location.hash.substr(1);
	var val = ""
	if (hash.indexOf(":") == -1) {
		val = odkCommon.getSessionVariable("val");
	} else {
		val = hash.split(":")[0];
		window.location.hash = "#" + hash.split(":").slice(1)
	}
	odkCommon.setSessionVariable("val", val);
	menu = ["Loading...", null, []];
	""" + code

helper.make_index("admin_region.html", """
list_views = {
	"health_facility": "config/assets/aa_health_facility_list.html",
	"refrigerators": "config/assets/aa_refrigerators_list.html",
}
""" + make_val_accepting_index("""
var subquery = "(SELECT date_serviced FROM m_logs WHERE m_logs.refrigerator_id = refrigerators.refrigerator_id ORDER BY date_serviced DESC LIMIT 1)"
menu = {"label": val, "type": "menu", "contents": [
	{"label": "View All Health Facilities", "type": "js", "function": function() {
		var where = "admin_region = ?"
		odkTables.openTableToMapView(null, "health_facility", where, [val], "config/assets/hack_for_hf_map.html" + "#health_facility/" + where + "/" + val);
	}},
	{"label": "View All Refrigerators", "type": "static", "table": "refrigerators", "query": "SELECT * FROM refrigerators JOIN health_facility ON refrigerators.facility_row_id = health_facility._id JOIN refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id WHERE health_facility.admin_region = ?", "args": [val], "explanation": "refrigerators in health facilities in the admin region ?"},
	{"label": "View All Refrigerators Not Serviced In The Last Six Months", "type": "static", "table": "refrigerators", "query": "SELECT * FROM refrigerators JOIN health_facility ON refrigerators.facility_row_id = health_facility._id JOIN refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id WHERE health_facility.admin_region = ? AND ("+subquery+" IS NULL OR (julianday(datetime('now')) - julianday("+subquery+")) > (6 * 30))", "args": [val], "explanation": "refrigerators in health facilities in the admin region ? that haven't been serviced in the last 180 days or have no service records"},
	{"label": "Filter By Type", "type": "html", "page": "config/assets/admin_region_filter.html#" + val + ":"}
]};
		"""), hallway)

helper.make_index("admin_region_filter.html", """
list_views = {
	"health_facility": "config/assets/aa_health_facility_list.html",
}
""" + make_val_accepting_index("""
	odkData.arbitraryQuery("health_facility", "SELECT admin_region, facility_type, regionLevel2, COUNT(facility_type) as cnt, _id FROM health_facility WHERE UPPER(admin_region) = UPPER(?) OR UPPER(regionLevel2) = UPPER(?) GROUP BY facility_type ORDER BY cnt DESC", [val, val], 100, 0, function(d) {
		if (d.getCount() == 0) {
			menu = [_tu("Admin region ") + val + _tu(" has no health facilities!"), null, []];
			doMenu();
		} else {
			var distinct_admin_regions = 0;
			var all_regions = [];
			for (var i = 0; i < d.getCount(); i++) {
				var this_admin_region = d.getData(i, "admin_region")
				if (all_regions.indexOf(this_admin_region) == -1) {
					all_regions = all_regions.concat(this_admin_region);
					distinct_admin_regions++;
				}
			}
			var where = "";
			var args = "";
			var hr_text = "";
			var old_val = val;
			if (distinct_admin_regions == 1) {
				val = d.getData(0, "admin_region");
				menu = [_tu("Filtering ") + val, null, []]
				where = "UPPER(admin_region) = UPPER(?) AND facility_type = ?";
				hr_text = "health facilities in the admin region ? of the type ?";
			} else {
				val = d.getData(0, "regionLevel2");
				menu = [_tu("Filtering ") + val, null, []]
				where = "UPPER(regionLevel2) = UPPER(?) AND facility_type = ?";
				hr_text = "health facilities in the region level 2 ? of the type ?";
			}

			for (var i = 0; i < d.getCount(); i++) {
				var ftype = d.getData(i, "facility_type")
				args = [val, ftype];
				var count = d.getData(i, "cnt").toString();
				var id = d.getData(i, "_id");
				menu[2] = menu[2].concat(0);
				(function(val, where, args, count, id) {
					var cb = null;
					//if (count == 1) {
						//cb = function() {
							//odkTables.launchHTML(null, "config/assets/aa_health_facility_detail.html#health_facility/" + id);
						//};
					//} else {
						cb = function() {
							odkTables.openTableToMapView(null, "health_facility", where, args, "config/assets/hack_for_hf_map.html#health_facility/STATIC/SELECT """+hf_cols_to_select+""" FROM health_facility WHERE " + where + "/" + JSON.stringify(args) + "/" + hr_text);
						}
					//}
					menu["contents"][menu["contents"].length - 1] = {"label": _tc(d, "facility_type", ftype) + " (" + count + ")", "type": "js", "function": cb}
				})(val, where, args, count, id);
			}
			doMenu();
		}
	}, function(e) { alert(e); });
		"""), hallway + """
			.button {
				font-size: 60%;
			}
		""")

helper.make_graph("cc_graph.html", hallway, "");

helper.static_files.append("hack_for_hf_map.js")
helper.static_files.append("hack_for_hf_map.html")

helper.static_files.append("add_hf.html")

helper.translations = {
	"PATH Cold Chain Demo": {"text": {
		"default": True,
		"es": "Demo del app de vacunaciónes por PATH"
	}},
	"View Data": {"text": {
		"default": True,
		"es": "Ver Data"
	}},
	"View Health Facilities": {"text": {
		"default": True,
		"es": "Ver Facilidades de Salud",
	}},
	"View All": {"text": {
		"default": True,
		"es": "Ver Todos"
	}},
	"Ownership": {"text": {
		"default": True,
		"es": "Tipo de Propriedad"
	}},
	"More": {"text": {
		"default": True,
		"es": "Más"
	}},
	"By Reserve Stock Requirement": {"text": {
		"default": True,
		"es": "En Grupos de Requisito de Reserva"
	}},
	"View Refrigerators": {"text": {
		"default": True,
		"es": "Ver Frigorífico"
	}},
	"By Facility": {"text": {
		"default": True,
		"es": "De Facilidad"
	}},
	"By Model": {"text": {
		"default": True,
		"es": "De Modelo"
	}},
	"By Year": {"text": {
		"default": True,
		"es": "De Año"
	}},
	"By Use": {"text": {
		"default": True,
		"es": "De Uso"
	}},
	"By Working Status": {"text": {
		"default": True,
		"es": "De Trabajando"
	}},
	"By Reason Not Working": {"text": {
		"default": True,
		"es": "De Razón por no Trabajar"
	}},
	"View Refrigerator Models": {"text": {
		"default": True,
		"es": "Ver Modelos de frigorífico"
	}},
	"By Manufacturer": {"text": {
		"default": True,
		"es": "De Fabricante"
	}},
	"By Equipment Type": {"text": {
		"default": True,
		"es": "De Tipo"
	}},
	"By Climate Zone": {"text": {
		"default": True,
		"es": "De Zona de Clima"
	}},
	"Health Facility ID": {"text": {
		"default": True,
		"es": "ID de Facilidad"
	}},
	"Population": {"text": {
		"default": True,
		"es": "Poblacion"
	}},
	"Coverage": {"text": {
		"default": True,
		"es": "Cobertura"
	}},
	"Admin Region": {"text": {
		"default": True,
		"es": "Region de Administración"
	}},
	"Grid Availability": {"text": {
		"default": True,
		"es": "Disponibilidad de Electricidad del Red Eléctrica"
	}},
	"Solar Suitable Climate?": {"text": {
		"default": True,
		"es": "Clima Adecueto por Energía Solar"
	}},
	"Solar Suitable Site?": {"text": {
		"default": True,
		"es": "Edificio Equipado por Energía Solar"
	}},
	"Latitude (GPS)": {"text": {
		"default": True,
		"es": "Latitud (SUG)"
	}},
	"Longitude (GPS)": {"text": {
		"default": True,
		"es": "Longitud (SUG)"
	}},
	"Climate": {"text": {
		"default": True,
		"es": "Clima"
	}},
	"Distance to Supply Point": {"text": {
		"default": True,
		"es": "Distancia al Punto de Suministro"
	}},
	"Vaccine Reserve Stock Req": {"text": {
		"default": True,
		"es": "Tamaño Minimo de Reserva"
	}},
	"Basic Facility Information": {"text": {
		"default": True,
		"es": "Información Basica"
	}},
	"Refrigerator Inventory (<span id='refrig_with_this_hfid_count'>Loading...</span>)": {"text": {
		"default": True,
		"es": "Frigorificos Aquí (<span id='refrig_with_this_hfid_count'>Cargando Numero...</span>)"
	}},
	"Power Information": {"text": {
		"default": True,
		"es": "Información de Energía"
	}},
	"Location Information": {"text": {
		"default": True,
		"es": "Información de Ubicación"
	}},
	"Stock Information": {"text": {
		"default": True,
		"es": "Información de Reserva"
	}},
	"Add Refrigerator": {"text": {
		"default": True,
		"es": "Aggregar Frigorífico"
	}},
	"Date Serviced": {"text": {
		"default": True,
		"es": "Fecha de Ultimo Revisión (Mantener)"
	}},
	" Refrigerators (<span id='refrig_with_this_model_count'>Loading...</span>)": {"text": {
		"default": True,
		"es": " Frigoríficos (<span id='refrig_with_this_model_count'>Cargando...</span>)"
	}},
	"Model Information": {"text": {
		"default": True,
		"es": "Información de Modelo"
	}},
	"View all maintenance logs": {"text": {
		"default": True,
		"es": "Ver todos los registros de mantener"
	}},
	"Add Maintenance Record": {"text": {
		"default": True,
		"es": "Aggregar registro de mantener/servicio"
	}},
	"Health Facility Information": {"text": {
		"default": True,
		"es": "Información de la Facilidad de Salud"
	}},
	"Basic Refrigerator Information": {"text": {
		"default": True,
		"es": "Información Básica"
	}},
	"View All Health Facilities": {"text": {
		"default": True,
		"es": "Ver Todos los Facilidades de Salud"
	}},
	"View All Refrigerators Not Serviced In The Last Six Months": {"text": {
		"default": True,
		"es": "Ver Todos Frigoríficos Cuales no se han Mantenido en los 6 Meses Pasados"
	}},
	"refrigerators in health facilities in the admin region ? that haven't been serviced in the last 180 days or have no service records": {"text": {
		"default": True,
		"es": " Frigoríficos Cuales no se han Mantenido en los 6 Meses Pasados y los que Están en una Facilidad de Salud lo que Está en el Región de Administración ?"
	}},
	"Facility": {"text": {
		"default": True,
		"es": "Facilidad"
	}},
	"Model": {"text": {
		"default": True,
		"es": "Modelo"
	}},
	"Use": {"text": {
		"default": True,
		"es": "Uso"
	}},
	"Healthcare Facility: ": {"text": {
		"default": True,
		"es": "Facilidad: "
	}},
	"Facility ID: ": {"text": {
		"default": True,
		"es": "ID: "
	}},
	"South": {"text": {
		"default": True,
		"es": "Sur"
	}},
	"North": {"text": {
		"default": True,
		"es": "Norte"
	}},
	"Central": {"text": {
		"default": True,
		"es": True
	}},
	"South East": {"text": {
		"default": True,
		"es": "Sureste"
	}},
	"South West": {"text": {
		"default": True,
		"es": "Suroeste"
	}},
	"Central East": {"text": {
		"default": True,
		"es": "Este Central"
	}},
	"Central West": {"text": {
		"default": True,
		"es": "Oeste Central"
	}},
	"Refrigerators:": {"text": { # not in use right now
		"default": True,
		"es": "Frigoríficos: "
	}},
	"Tracking Number": {"text": {
		"default": True,
		"es": "Código de seguimiento"
	}},
	"Status": {"text": {
		"default": True,
		"es": "Estatus"
	}},
	"Year Installed": {"text": {
		"default": True,
		"es": "Año de instalación"
	}},
	"Manufacturer: ": {"text": {
		"default": True,
		"es": "Fabricante: "
	}},
	"refrigerators in health facilities in the admin region ?": {"text": {
		"default": True,
		"es": " frigoríficos los que Están en una Facilidad de Salud lo que Está en el Región de Administración ?"
	}},
	"Model ID": {"text": {
		"default": True,
		"es": "ID de Modelo"
	}},
	"View All Refrigerators": {"text": {
		"default": True,
		"es": "Ver Todos los Frigoríficos"
	}},
	"No Records": {"text": {
		"default": True,
		"es": "Sin Registro"
	}},
	"Model ID: ": {"text": {
		"default": True,
		"es": "ID de Modelo: "
	}},
	"View All ": {"text": {
		"default": True,
		"es": "Ver Todos los "
	}},
	"All Regions": {"text": {
		"default": True,
		"es": "Todos"
	}},
	"No picture available": {"text": {
		"default": True,
		"es": "Sin Foto"
	}},
	"health facilities in the admin region ? of the type ?": {"text": {
		"default": True,
		"es": "facilidades de salud en el región de administración ? del tipo ?"
	}},
	"None": {"text": {
		"default": True,
		"es": "Ninguno"
	}},
	"20+ years": {"text": {
		"default": True,
		"es": "Más que 20 años"
	}},
	"15-20 years": {"text": {
		"default": True,
		"es": "15-20 años"
	}},
	"12-15 years": {"text": {
		"default": True,
		"es": "12-15 años"
	}},
	"10-12 years": {"text": {
		"default": True,
		"es": "10-12 años"
	}},
	"9 years": {"text": {
		"default": True,
		"es": "9 años"
	}},
	"8 years": {"text": {
		"default": True,
		"es": "8 años"
	}},
	"7 years": {"text": {
		"default": True,
		"es": "7 años"
	}},
	"6 years": {"text": {
		"default": True,
		"es": "6 años"
	}},
	"5 years": {"text": {
		"default": True,
		"es": "5 años"
	}},
	"4 years": {"text": {
		"default": True,
		"es": "4 años"
	}},
	"3 years": {"text": {
		"default": True,
		"es": "3 años"
	}},
	"2 years": {"text": {
		"default": True,
		"es": "2 años"
	}},
	"1 years": {"text": {
		"default": "1 year",
		"es": "1 año"
	}},
	"Within 6 months": {"text": {
		"default": True,
		"es": "Menos que 6 meses"
	}},
	"More Options": {"text": {
		"default": True,
		"es": "Más"
	}},
	"Search By Name/ID": {"text": {
		"default": True,
		"es": "Buscar Usando Nombre/ID"
	}},
	"View Inventory": {"text": {
		"default": True,
		"es": "Ver Inventario"
	}},
	"Refrigerator Age": {"text": {
		"default": True,
		"es": "Antigüedad de Frigoríficos"
	}},
	"Facility Grid Power Availability": {"text": {
		"default": True,
		"es": "Disponibilidad de Electricidad del Red"
	}},
	"Add Health Facility": {"text": {
		"default": True,
		"es": "Aggregar Facilidad de Salud"
	}},
	"Admin region ": {"text": {
		"default": True,
		"es": "¡Región "
	}},
	" has no health facilities!": {"text": {
		"default": True,
		"es": " no tiene ningunos facilidades de salud!"
	}},
	"Filtering ": {"text": {
		"default": True,
		"es": "Filtrando "
	}},
	"View ": {"text": {
		"default": True,
		"es": "Ver Solo "
	}},
	"maintenance records for the selected refrigerator": {"text": {
		"default": True,
		"es": "recordias de mantener/servicio para el frigorífico seleccionado"
	}},
	" litres": {"text": {
		"default": True,
		"es": " litros"
	}},
	"Not logged in!": {"text": {
		"default": True,
		"es": "¡Sin iniciar sesión!"
	}},
	"Log in": {"text": {
		"default": True,
		"es": "Iniciar Sesion"
	}},
	"Health Facilities (Advanced)": {"text": {
		"default": True,
		"es": "Facilidades (Avanzado)"
	}},
	"Refrigerators (Advanced)": {"text": {
		"default": True,
		"es": "Frigoríficos (Avanzado)"
	}},
	"Models (Advanced)": {"text": {
		"default": True,
		"es": "Modelos (Avanzado)"
	}},
	"Notes: ": {"text": {
		"default": True,
		"es": "Notas: "
	}},
	"Filter By Type": {"text": {
		"default": "Filter Health Facilities by Type",
		"es": "Filtrar"
	}},
	"Administrative Actions": {"text": {
		"default": True,
		"es": "Acciones Administrativos"
	}},
	"Select Region": {"text": {
		"default": True,
		"es": "Selecciona Región"
	}},
	"Loading...": {"text": {
		"default": True,
		"es": "Cargando..."
	}},
	"This year": {"text": {
		"default": True,
		"es": "Este año"
	}},
	"In the future!": {"text": {
		"default": True,
		"es": "¡En el futuro!"
	}},
	"Select Facility Type": {"text": {
		"default": True,
		"es": "Selecciona Tipo"
	}},
	"Select Power Source": {"text": {
		"default": True,
		"es": "Selecciona Fuente de Poder"
	}},
	"Facility Inventory By Grid Power": {"text": {
		"default": True,
		"es": "Inventario de Facilidades usando Poder de Red Electríca"
	}},
	"Only facilities that use grid power": {"text": {
		"default": True,
		"es": "Solo facilidades que usan poder del red electríca"
	}},
	"Any": {"text": {
		"default": True,
		"es": "Cualquier"
	}},
}
