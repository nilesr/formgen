# coding=utf-8
import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();


# Cold chain demo
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
""", """
	var makepicture = function makepicture(e, c, d, i) {
		return "<div class='img-wrapper'><img class='refrig-img' src='" + odkCommon.getRowFileAsUrl(table_id, d.getData(i, "_id"), c) + "' /></div>";
	}
	allowed_tables = [];
	display_subcol = [["Manufacturer: ", "manufacturer", true], ["Model ID: ", "model_id", true], [makepicture, "refrigerator_picture_uriFragment", true]];
	allowed_group_bys = ["manufacturer", "climate_zone", "equipment_type"]
	display_col = "catalog_id"
	table_id = "refrigerator_types";
	// Dirty hacks beyond this point
	if (global_group_by == null || global_group_by == undefined || global_group_by.trim().length == 0) {
		var option = document.createElement("option");
		option.value = 5;
		option.innerText = 5;
		var l = document.getElementById("limit");
		l.appendChild(option);
		l.selectedIndex = l.children.length - 1;
		limit = 5;
		newLimit();
	}
""", "", "")

helper.make_table("aa_refrigerators_list.html", "", "", """
	allowed_tables = [];
	global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
	display_subcol = [["", "model_id", true], ["Healthcare Facility: ", "facility_name", true]];
	display_col = "refrigerator_id"
	table_id = "refrigerators";
	allowed_group_bys = [["facility_row_id", "Facility"], ["model_row_id", "Model"], "reason_not_working", ["utilization", "Use"], "working_status", "year"]
""", "", "")

helper.make_table("aa_health_facility_list.html", "", "", """
	allowed_tables = [];
	display_col = "facility_name"
	table_id = "health_facility";
	allowed_group_bys = ["admin_region", "climate_zone", "delivery_type", "electricity_source", ["facility_ownership", "Ownership"], "facility_type", "storage_type", "solar_suitable_climate", "solar_suitable_site", "vaccine_supply_mode", "vaccine_reserve_stock_requirement"];

	global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE facility_row_id = health_facility._id) AS refrigerator_count"
	display_subcol = [["Facility ID: ", "facility_id", true], ["Refrigerators: ", "refrigerator_count", true]]
""", "", "")

helper.make_table("aa_m_logs_list.html", "", "", """
	allowed_tables = [];
	display_subcol = [["", "refrigerator_id", false]];
	allowed_group_bys = ["manufacturer", "climate_zone", "equipment_type"]
	display_col = "date_serviced"
	table_id = "m_logs";
""", "", "")


helper.make_detail("aa_refrigerators_detail.html", """
	<div class="main-col-wrapper">
		<div id="inject-refrigerator_id">Loading...</div>
	</div>
	<div class='h4-wrapper'><h4 id='bfi'><h4></div>
	<ul>
		<li id='inject-facility_name'></li>
		<li id='inject-year'></li>
		<li id='inject-working_status'></li>
		<li id='inject-reason_not_working'></li>
		<li id='inject-model_id'></li>
		<li id='inject-tracking_id'></li>
		<li id='inject-voltage_regulator'></li>
		<li id='inject-date_serviced'></li>
	</ul>
	<button disabled id='open_model'></button>
	<br />
	<button disabled id='open_hf'></button>
	<br />
	<button disabled id='add_m_log'></button>
	<br />
	<button disabled id='view_m_log'></button>
	<br />
		""", open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + """
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
		console.log(d.getData(0, "facility_name"));
		var btn = document.getElementById("open_hf");
		btn.innerText = _tu("Health Facility Information");
		var hf = d.getData(0, "facility_name"); // from join, not actually the hf id
		var hf_row_id = d.getData(0, "facility_row_id");
		btn.disabled = false;
		btn.addEventListener("click", function() {
			odkTables.openDetailView(null, "health_facility", hf_row_id, "config/assets/aa_health_facility_detail.html#health_facility/" + hf_row_id);
		});
		build_generic_callback("facility_name", true, "Facility")(e, c, d)
		document.getElementById("add_m_log").disabled = false;
		document.getElementById("add_m_log").innerText = _tu("Add Maintenance Record");
		var defaults = {"refrigerator_id": d.getData(0, "refrigerator_id"), "date_serviced": odkCommon.toOdkTimeStampFromDate(new Date())};
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
			odkTables.launchHTML(null, "config/assets/aa_m_logs_list.html#m_log/refrigerator_id = ?/" + d.getData(0, "refrigerator_id"));
		});

		return "";
	}

	allowed_tables = ["m_logs"];
	main_col = "";
	global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
	global_which_cols_to_select = "*"
	var subquery = "(SELECT date_serviced FROM m_logs WHERE m_logs.refrigerator_id = refrigerators.refrigerator_id AND m_logs._savepoint_type != 'INCOMPLETE' ORDER BY date_serviced DESC LIMIT 1)"
	global_which_cols_to_select = global_which_cols_to_select.concat(", (CASE WHEN "+subquery+" IS NOT NULL THEN "+subquery+" ELSE 'No Records' END) as date_serviced")
	colmap = [
		["facility_name", hf_callback],
		["year", build_generic_callback("year", true, "Year Installed")],
		["working_status", build_generic_callback("working_status", true, "Status")],
		["reason_not_working", build_generic_callback("reason_not_working", true)],
		["model_row_id", model_callback],
		["tracking_id", build_generic_callback("tracking_id", false, "Tracking Number")],
		["voltage_regulator", build_generic_callback("voltage_regulator", true)],
		["refrigerator_id", build_generic_callback("refrigerator_id", true)],
		["date_serviced", build_generic_callback("date_serviced", function(i) {
			if (i == "No Records") {
				return _tu(i);
			}
			return i.split("T")[0];
		}, _tu("Date Serviced"))]
	];
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
		""", open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + """

	document.getElementById("mi").innerText = _tu("Model Information")

	allowed_tables = [];
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
		["manufacturer", build_generic_callback("manufacturer", true)],
		["power_source", build_generic_callback("power_source", function(i) { return pretty(jsonParse(i).join(", ")); })],
		["refrigerator_gross_volume", build_generic_callback("refrigerator_gross_volume", " m<sup>3</sup>")],
		["freezer_gross_volume", build_generic_callback("freezer_gross_volume", " m<sup>3</sup>")],
		["equipment_type", build_generic_callback("equipment_type", true)],
		["climate_zone", build_generic_callback("climate_zone", true)],
		["refrigerator_net_volume", build_generic_callback("refrigerator_net_volume", " m<sup>3</sup>")],
		["freezer_net_volume", build_generic_callback("freezer_net_volume", " m<sup>3</sup>")],
		["model_id", mid_callback],
		["catalog_id", build_generic_callback("catalog_id", true)],
		["refrigerator_picture", function(e,c,d){document.getElementById("inject-refrigerator_picture").appendChild(c)}]
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
		""", open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + """

	allowed_tables = [];
	main_col = "";
	global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE facility_row_id = health_facility._id) as refrig_with_this_hfid_count"
	var fname_callback = function fname_callback(e, c, d) {
		generic_callback(e, c, d, "facility_name", true, "Health Facility ID");
		document.getElementById("refrigerator_inventory").innerHTML = _tu("Refrigerator Inventory (<span id='refrig_with_this_hfid_count'>Loading...</span>)")
		document.getElementById("refrigerator_inventory").disabled = false;
		document.getElementById("refrigerator_inventory").addEventListener("click", function click() {
			odkTables.launchHTML(null, "config/assets/aa_refrigerators_list.html#refrigerators/facility_row_id = ?/" + row_id);
		});
		document.getElementById("refrig_with_this_hfid_count").innerText = d.getData(0, "refrig_with_this_hfid_count");
		document.getElementById("addref").addEventListener("click", function() {
			var defaults = {"facility_row_id": d.getData(0, "_id")}
			if (allowed_tables.indexOf("refrigerators") >= 0) {
				var id = newGuid();
				odkData.addRow("m_logs", defaults, id, function() {
					// Escape the LIMIT 1
					odkData.arbitraryQuery("m_logs", "UPDATE m_logs SET _savepoint_type = ? WHERE _id = ?;--", ["INCOMPLETE", id], 100, 0, function success(d) {
						odkTables.launchHTML({}, "config/assets/formgen/refrigerators#" + id);
					}, null);
				});
			} else {
				odkTables.addRowWithSurvey({}, "m_logs", "m_logs", null, defaults);
			}
		});
	}
	colmap = [
		['facility_name', fname_callback],
		['facility_id', build_generic_callback("facility_id", true, "Health Facility ID")],
		['facility_type', build_generic_callback("facility_type", true)],
		['facility_ownership', build_generic_callback("facility_ownership", true, "Ownership")],
		['facility_population', build_generic_callback("facility_population", true, "Population")],
		['facility_coverage', build_generic_callback("facility_coverage", "%", "Coverage")],
		['admin_region', build_generic_callback("admin_region", true, "Admin Region")],
		['electricity_source', build_generic_callback("electricity_source", true)],
		['grid_power_availability', build_generic_callback("grid_power_availability", true, "Grid Availability")],
		['gas_availability', build_generic_callback("gas_availability", true)],
		['kerosene_availability', build_generic_callback("kerosene_availability", true)],
		['solar_suitable_climate', build_generic_callback("solar_suitable_climate", true, "Solar Suitable Climate?")],
		['solar_suitable_site', build_generic_callback("solar_suitable_site", true, "Solar Suitable Site?")],
		['Location_latitude', build_generic_callback("Location_latitude", true, "Latitude (GPS)")],
		['Location_longitude', build_generic_callback("Location_longitude", true, "Longitude (GPS)")],
		['climate_zone', build_generic_callback("climate_zone", true, "Climate")],
		['distance_to_supply', build_generic_callback("distance_to_supply", true, "Distance to Supply Point")],
		['vaccine_supply_interval', build_generic_callback("vaccine_supply_interval", true)],
		['vaccine_reserve_stock_requirement', build_generic_callback("vaccine_reserve_stock_requirement", true, "Vaccine Reserve Stock Req")],
		['vaccine_supply_mode', build_generic_callback("vaccine_supply_mode", true)],
	]
	document.getElementById("bfi").innerText = _tu("Basic Facility Information");
	document.getElementById("pi").innerText = _tu("Power Information");
	document.getElementById("locationi").innerText = _tu("Location Information");
	document.getElementById("stocki").innerText = _tu("Stock Information");
	document.getElementById("addref").innerText = _tu("Add Refrigerator");
""", "")
helper.make_detail("aa_m_logs_detail.html", "", "", """
	main_col = "refrigerator_id";
	colmap = [
		['refrigerator_id', false],
		['date_serviced', function(e, c, d) { return "<b>" + _tu("Date Serviced") + ":</b> " + c.split("T")[0]; }],
		['notes', false]
	]
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
levels = ["Region level 1", "Region level 2", "Admin Region"]
for i in range(len(levels) - 1):
	for row in c.execute("SELECT regionLevel1, t1.regionLevel2, regionLevel3 FROM t1 JOIN t2 ON t1.regionLevel2 = t2.regionLevel2;"):
		hierarchy["_start"].add(row[0])
		if row[i] != row[i + 1]:
			hierarchy[row[i]].add(row[i+1])
paths = {}
def make_admin_region(val, path):
	# path is like "/1/3/0"
	# needs to be like "#1/3/0" before it goes into `paths`
	paths[val.upper()] = "#" + path[1:];
	subquery = "(SELECT date_serviced FROM m_logs WHERE m_logs.refrigerator_id = refrigerators.refrigerator_id ORDER BY date_serviced DESC LIMIT 1)"
	return [val, None, [
		["View All Health Facilities", "health_facility", "admin_region = ?/" + val],
		["View All Refrigerators", "refrigerators", "STATIC/SELECT * FROM refrigerators JOIN health_facility ON refrigerators.facility_row_id = health_facility._id JOIN refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id WHERE health_facility.admin_region = ?/[\""+val+"\"]/"+"refrigerators in health facilities in the admin region ?"],
		["View All Refrigerators Not Serviced In The Last Six Months", "refrigerators", "STATIC/SELECT * FROM refrigerators JOIN health_facility ON refrigerators.facility_row_id = health_facility._id JOIN refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id WHERE health_facility.admin_region = ? AND ("+subquery+" IS NULL OR (julianday(datetime('now')) - julianday("+subquery+")) > (6 * 30))/[\""+val+"\"]/refrigerators in health facilities in the admin region ? that haven't been serviced in the last 180 days or have no service records"],
	]];
def make_map(val, path = ""):
	if len(hierarchy[val]) == 0: return make_admin_region(val, path)
	# These two lines aren't needed, but they make it so the order in the list doesn't change every time you regenerate
	hierarchy[val] = list(hierarchy[val])
	hierarchy[val].sort()
	return [val, None, [make_map(hierarchy[val][i], path + "/" + str(i)) for i in range(len(hierarchy[val]))]]
#print(hierarchy)
as_list = make_map("_start")
# as_list now like ["_start", null, [...]]
import json
as_list[0] = "PATH Cold Chain Demo"
# as_list now like ["PATH Cold Chain Demo", null, [...]]
# append to the [...] our own option

as_list[2].append(
	["All Regions", None, [[val[0], "_html", "config/assets/index.html" + paths[val[0].upper()]] for val in c.execute("SELECT regionlevel3 from t2;")]]
)
as_list[2].append(
	["View Data", None, [
		["View Health Facilities", "health_facility", [
			["View All", "health_facility", ""],
			[True, "health_facility", "admin_region"],
			[True, "health_facility", "facility_type"],
			["Ownership", "health_facility", "facility_ownership"],
			["More", "health_facility", [
				[True, "health_facility", "delivery_type"],
				[True, "health_facility", "electricity_source"],
				[True, "health_facility", "storage_type"],
				[True, "health_facility", "solar_suitable_climate"],
				[True, "health_facility", "solar_suitable_site"],
				[True, "health_facility", "vaccine_supply_mode"],
				["By Reserve Stock Requirement", "health_facility", "vaccine_reserve_stock_requirement"]
			]]
		]], ["View Refrigerators", "refrigerators", [
			["View All", "refrigerators", ""],
			["By Facility", "refrigerators", "facility_name"],
			["By Model", "refrigerators", "catalog_id"],
			["By Year", "refrigerators", "year"],
			["More", "refrigerators", [
				["By Use", "refrigerators", "utilization"],
				["By Working Status", "refrigerators", "working_status"],
				["By Reason Not Working", "refrigerators", "reason_not_working"]
			]]
		]], ["View Refrigerator Models", "refrigerator_types", [
			["View All", "refrigerator_types", ""],
			["By Manufacturer", "refrigerator_types", "manufacturer"],
			["By Equipment Type", "refrigerator_types", "equipment_type"],
			["More", "refrigerator_types", [
				["By Climate Zone", "refrigerator_types", "climate_zone"]
			]]
		]]
	]]
)

helper.make_index("index.html", """
list_views = {
	"health_facility": "config/assets/aa_health_facility_list.html",
	"refrigerators": "config/assets/aa_refrigerators_list.html",
	"refrigerator_types": "config/assets/aa_refrigerator_types_list.html",
}
menu = """+json.dumps(as_list)+""";
paths = """+json.dumps(paths)+""";
if (window.location.hash.substr(1).length == 0) {
	odkData.getRoles(function(r) {
		// TEMP DEBUG TEST
		//r = ["GROUP_ADMIN_REGION_MCHINJI"];
		//r = ["GROUP_ADMIN_REGION_MZIMBA_SOUTH"];
		for (var i = 0; i < r.length; i++) {
			if (r[i].indexOf("GROUP_ADMIN_REGION_") == 0) {
				// Doesn't work right on things with more than 3 underscores in them
				//var region = r[i].split("_", 4)[3];
				var region = r[i].replace("GROUP_ADMIN_REGION_", "");
				// replace all occurrences
				region = region.replace(/_/g, " ");
				window.location.hash = paths[region];
				alert(region);
				window.location.reload();
				break;
			}
		}
	});
}
		""", """
body {
	background: url('/coldchain/config/assets/img/hallway.jpg') no-repeat center/cover fixed;
}
		""")


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
		"es": "Este"
	}},
	"Central West": {"text": {
		"default": True,
		"es": "Oeste"
	}},
	"Refrigerators: ": {"text": {
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
}

