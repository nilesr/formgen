import sys, os, subprocess
import generate_table
import generate_detail
import demo
queue = []
_shells = []
def make_table(filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric):
    queue.append(["table", filename, customHtml, customCss, customJsOl, customJsSearch, customJsGeneric])
def make_detail(filename, customHtml, customCss, customJsOl, customJsGeneric):
    queue.append(["detail", filename, customHtml, customCss, customJsOl, customJsGeneric])
def make_demo(filename, config):
    queue.append(["demo", filename, config])
def shell(command): _shells.append(command);
def _make(utils, filenames):
    for q in queue:
        if q[0] == "detail":
            generate_detail.make(utils, *(q[1:]))
        elif q[0] == "table":
            generate_table.make(utils, *(q[1:]))
        elif q[0] == "demo":
            demo.make_demo(utils, *(q[1:]))
        else:
            print("Bad type in queue " + q[0]);
            sys.exit(0);
        filenames.append(q[1])
    return filenames

# Cold chain demo
make_table("aa_refrigerator_types_list.html", "", "", """
    allowed_tables = [];
    display_subcol = [["Manufacturer: ", "manufacturer", true]];
    allowed_group_bys = ["manufacturer", "climate_zone", "equipment_type"]
    display_col = "catalog_id"
    table_id = "refrigerator_types";
""", "", "")

make_table("aa_refrigerators_list.html", "", "", """
    allowed_tables = [];
    global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
    display_subcol = [["", "model_id", true], ["Healthcare Facility: ", "facility_name", true]];
    display_col = "refrigerator_id"
    table_id = "refrigerators";
    allowed_group_bys = [["facility_row_id", "Facility"], ["model_row_id", "Model"], ["reason_not_working", true], ["utilization", "Use"], ["working_status", true], ["year", true]]
""", "", "")

make_table("aa_health_facility_list.html", "", "", """
    allowed_tables = [];
    display_col = "facility_name"
    display_subcol = [["Facility ID: ", "facility_id", true]];
    table_id = "health_facility";
    allowed_group_bys = ["admin_region", "climate_zone", "delivery_type", "electricity_source", ["facility_ownership", "Ownership"], "facility_type", "storage_type", "solar_suitable_climate", "solar_suitable_site", "vaccine_supply_mode", "vaccine_reserve_stock_requirement"];

    global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE facility_row_id = health_facility._id) AS refrigerator_count"
    display_subcol = [["Facility ID: ", "facility_id", true], ["Refrigerators: ", "refrigerator_count", true]]
""", "", "")

make_detail("aa_refrigerators_detail.html", """
    <div class="main-col-wrapper">
        <div id="inject-refrigerator_id">Loading...</div>
    </div>
    <div class='h4-wrapper'><h4>Basic Refrigerator Information<h4></div>
    <ul>
        <li id='inject-facility_name'></li>
        <li id='inject-year'></li>
        <li id='inject-working_status'></li>
        <li id='inject-reason_not_working'></li>
        <li id='inject-model_id'></li>
        <li id='inject-tracking_id'></li>
        <li id='inject-voltage_regulator'></li>
    </ul>
    <button disabled id='open_model'>Model Information</button>
    <br />
    <button disabled id='open_hf'>Health Facility Information</button>
        """, open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + """

    var model_callback = function model_callback(e, c, d) {
        var btn = document.getElementById("open_model");
        var model = d.getData(0, "catalog_id"); // from join, not actually the model id
        var model_row_id = d.getData(0, "model_row_id");
        btn.disabled = false;
        btn.addEventListener("click", function() {
            odkTables.openDetailView(null, "refrigerator_types", model_row_id);
        });
        build_generic_callback("model_id", true)(e, c, d)
        return "";
    }
    var hf_callback = function hf_callback(e, c, d) {
        console.log(d.getData(0, "facility_name"));
        var btn = document.getElementById("open_hf");
        var hf = d.getData(0, "facility_name"); // from join, not actually the hf id
        var hf_row_id = d.getData(0, "facility_row_id");
        btn.disabled = false;
        btn.addEventListener("click", function() {
            odkTables.openDetailView(null, "health_facility", hf_row_id, "config/assets/aa_health_facility_detail.html#health_facility/" + hf_row_id);
        });
        build_generic_callback("facility_name", true, "Facility")(e, c, d)
        return "";
    }

    allowed_tables = [];
    main_col = "";
    global_join = "refrigerator_types ON refrigerators.model_row_id = refrigerator_types._id JOIN health_facility ON refrigerators.facility_row_id = health_facility._id"
    colmap = [
        ["facility_name", hf_callback],
        ["year", build_generic_callback("year", true, "Year Installed")],
        ["working_status", build_generic_callback("working_status", true, "Status")],
        ["reason_not_working", build_generic_callback("reason_not_working", true)],
        ["model_row_id", model_callback],
        ["tracking_id", build_generic_callback("tracking_id", false, "Tracking Number")],
        ["voltage_regulator", build_generic_callback("voltage_regulator", true)],
        ["refrigerator_id", build_generic_callback("refrigerator_id", true)]
    ];
""", "")

make_detail("aa_refrigerator_types_detail.html", """
    <div class="main-col-wrapper">
        <div id="inject-model_id" style='line-height: 3em;'>Loading...</div>
        <div id="inject-catalog_id" style='line-height: 3em;'>Loading...</div>
    </div>
    <div class="h4-wrapper"><h4>Model Information</h4></div>
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

    allowed_tables = [];
    main_col = "";
    global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE model_row_id = refrigerator_types._id) as refrig_with_this_model_count"
    var mid_callback = function mid_callback(e, c, d) {
        generic_callback(e, c, d, "model_id", true);
        document.getElementById("open_model").innerHTML = "View All " + c + " Refrigerators (<span id='refrig_with_this_model_count'>Loading...</span>)"
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




make_detail("aa_health_facility_detail.html", """
    <div class="main-col-wrapper">
        <div id="inject-facility_name">Loading...</div>
    </div>
    <div class="h4-wrapper"><h4>Basic Facility Information</h4></div>
    <ul>
        <li id='inject-facility_id'></li>
        <li id='inject-facility_type'></li>
        <li id='inject-facility_ownership'></li>
        <li id='inject-facility_population'></li>
        <li id='inject-facility_coverage'></li>
        <li id='inject-admin_region'></li>
    </ul>
    <div class="h4-wrapper"><h4>Power Information</h4></div>
    <ul>
        <li id='inject-electricity_source'></li>
        <li id='inject-grid_power_availability'></li>
        <li id='inject-gas_availability'></li>
        <li id='inject-kerosene_availability'></li>
        <li id='inject-solar_suitable_climate'></li>
        <li id='inject-solar_suitable_site'></li>
    </ul>
    <div class="h4-wrapper"><h4>Location Information</h4></div>
    <ul>
        <li id='inject-Location_latitude'></li>
        <li id='inject-Location_longitude'></li>
        <li id='inject-climate_zone'></li>
    </ul>
    <div class="h4-wrapper"><h4>Stock Information</h4></div>
    <ul>
        <li id='inject-distance_to_supply'></li>
        <li id='inject-vaccine_supply_interval'></li>
        <li id='inject-vaccine_reserve_stock_requirement'></li>
        <li id='inject-vaccine_supply_mode'></li>
    </ul>
    <div style="text-align: center;">
        <button disabled id='refrigerator_inventory'>Loading...</button>
        <br />
        <button onClick="odkTables.launchHTML(null, "/config/assets/formgen/refrigerators#" + newGuid())">Add refrigerator</button>
    </div>
        """, open("refrigerator_detail.css").read(), open("refrigerator_detail.js", "r").read() + """

    allowed_tables = [];
    main_col = "";
    global_which_cols_to_select = "*, (SELECT COUNT(*) FROM refrigerators WHERE facility_row_id = health_facility._id) as refrig_with_this_hfid_count"
    var fname_callback = function fname_callback(e, c, d) {
        generic_callback(e, c, d, "facility_name", true, "Health Facility ID");
        document.getElementById("refrigerator_inventory").innerHTML = "Refrigerator Inventory (<span id='refrig_with_this_hfid_count'>Loading...</span>)"
        document.getElementById("refrigerator_inventory").disabled = false;
        document.getElementById("refrigerator_inventory").addEventListener("click", function click() {
            odkTables.launchHTML(null, "config/assets/aa_refrigerators_list.html#refrigerators/facility_row_id = ?/" + row_id);
        });
        document.getElementById("refrig_with_this_hfid_count").innerText = d.getData(0, "refrig_with_this_hfid_count");
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
""", "")

make_demo("index.html.coldchaindemo2", """
var metadata = {};
var list_views = {
    "health_facility": "config/assets/aa_health_facility_list.html",
    "refrigerators": "config/assets/aa_refrigerators_list.html",
    "refrigerator_types": "config/assets/aa_refrigerator_types.html",
}
var menu = [
        "PATH Cold Chain Demo", null, [
        ["View Health Facilities", "health_facility", [
            ["View All", "health_facility", ""],
            [true, "health_facility", "admin_region"],
            [true, "health_facility", "facility_type"],
            [true, "health_facility", "ownership"],
            ["More", "health_facility", [
                [true, "health_facility", "delivery_type"],
                [true, "health_facility", "electricity_source"],
                [true, "health_facility", "storage_type"],
                [true, "health_facility", "solar_suitable_climate"],
                [true, "health_facility", "solar_suitable_site"],
                [true, "health_facility", "vaccine_supply_mode"],
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
    ]];
        """)
# convention is to just squash it
shell(["cp", "/sdcard/opendatakit/coldchain/config/assets/index.html.coldchaindemo2", "/sdcard/opendatakit/coldchain/config/assets/index.html"]);



make_table("plot.html", "", "", """
    display_subcol = [["", "planting", false], [", ","plot_size", false], [" hectares", null, true]];
    table_id = "plot";
""", "", "")


make_table("Tea_houses_list.html", "", "", """
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
make_table("selects_list.html", "", "", """
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
