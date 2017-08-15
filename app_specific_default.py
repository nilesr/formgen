import sys;
sys.path.append('.');
import custom_helper;
helper = custom_helper.helper();
helper.make_table("Tea_houses_list.html","","","\tclicked = function clicked(table_id, row_id) {\n\t\todkTables.openDetailWithListView(null, table_id, row_id, \"config/assets/Tea_houses_detail.html\");\n\t}\n\tglobal_join = \"Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id\"\n\tglobal_which_cols_to_select = \"*, Tea_types.Name AS ttName, Tea_houses.Name AS thName\"\n\tdisplay_subcol = [[\"Specialty: \", \"ttName\", true], [\"\", \"District\", false], [\", \", \"Neighborhood\", true]];\n\n\tdisplay_subcol = [\n\t\t{\"column\": \"ttName\", \"display_name\": \"Specialty: \", \"newline\": true},\n\t\t{\"column\": \"District\", \"newline\": false},\n\t\t{\"column\": \"Neighborhood\", \"display_name\": \", \", \"newline\": true}\n\t]\n\tdisplay_col = \"thName\";\n\ttable_id = \"Tea_houses\";\n\tallowed_group_bys = [\n\t\t{\"column\": \"District\"},\n\t\t{\"column\": \"Neighborhood\"},\n\t\t{\"column\": \"State\"},\n\t\t{\"column\": \"WiFi\"},\n\t\t{\"column\": \"Hot\"},\n\t\t{\"column\": \"Iced\"},\n\t\t{\"column\": \"State\"},\n\t\t{\"column\": \"ttName\", \"display_name\": \"Specialty\"},\n\t]\n","","");

helper.make_table("Tea_inventory_list.html","","","\tglobal_join = \"Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id\"\n\tglobal_which_cols_to_select = \"*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName\"\n\tdisplay_subcol = [[\"Tea House: \", \"thName\", true], [\"Type: \", \"ttName\", true]];\n\n\tdisplay_subcol = [\n\t\t{\"column\": \"thName\", \"display_name\": \"Tea House: \", \"newline\": true},\n\t\t{\"column\": \"ttName\", \"display_name\": \"Type: \", \"newline\": true}\n\t]\n\tdisplay_col = \"tiName\";\n\ttable_id = \"Tea_inventory\";\n\tallowed_group_bys = [\n\t\t{\"column\": \"thName\", \"display_name\": \"House\"},\n\t\t{\"column\": \"ttName\", \"display_name\": \"Type\"},\n\t\t{\"column\": \"Iced\"},\n\t\t{\"column\": \"Hot\"},\n\t\t{\"column\": \"Bags\"},\n\t\t{\"column\": \"Loose_Leaf\"}\n\t]\n","","");

helper.make_table("Tea_types_list.html","","","\tvar extras_cb = function extras_cb(e, c, d, i) {\n\t\tvar caffeinated = d.getData(i, \"Caffeinated\").toUpperCase() == \"YES\"\n\t\tvar fermented = d.getData(i, \"Fermented\").toUpperCase() == \"YES\"\n\t\tvar extras = []\n\t\tif (caffeinated) extras = extras.concat(\"Caffeinated\");\n\t\tif (fermented) extras = extras.concat(\"Fermented\");\n\t\treturn extras.join(\", \");\n\t}\n\tdisplay_subcol = [[\"Origin: \", \"Origin\", true], [extras_cb, \"_id\", true]];\n\n\tdisplay_subcol = [\n\t\t{\"column\": \"Origin\", \"display_name\": \"Origin: \", \"newline\": true},\n\t\t{\"column\": \"_id\", \"callback\": extras_cb, \"newline\": true}\n\t]\n\tdisplay_col = \"Name\";\n\ttable_id = \"Tea_types\";\n\tallowed_group_bys = [\n\t\t{\"column\": \"Origin\"},\n\t\t{\"column\": \"Caffeinated\"},\n\t\t{\"column\": \"Fermented\"}\n\t]\n","","");

helper.make_detail("Tea_houses_detail.html","","","\tvar br = function(col, extra) {\n\t\treturn function(e, c, d) { return \"<b>\" + col + \"</b>: \" + c + (extra ? extra : \"<br />\"); };\n\t}\n\tvar check = function(col, accepting, type) {\n\t\tif (accepting === undefined) {\n\t\t\taccepting = function(e, c, d) {\n\t\t\t\treturn c.toUpperCase() == \"YES\";\n\t\t\t}\n\t\t}\n\t\tif (type === undefined) type = \"checkbox\"\n\t\treturn function(e, c, d) {\n\t\t\treturn \"<input disabled type='\"+type+\"' \" + (accepting(e, c, d) ? \"checked=checked\" : \"\") + \" /><b>\" + col + \"</b>\";\n\t\t};\n\t}\n\tvar selected = function(a, b) {\n\t\tif (a == null) return false;\n\t\tif (a[0] == \"[\") {\n\t\t\treturn jsonParse(a).indexOf(b) >= 0;\n\t\t}\n\t\treturn a.toUpperCase() == b.toUpperCase();\n\t}\n\n\tmain_col = \"thName\";\n\ttable_id = \"Tea_houses\";\n\tglobal_join = \"Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id\"\n\tglobal_which_cols_to_select = \"*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, (SELECT COUNT(*) FROM Tea_inventory WHERE Tea_inventory.House_id = Tea_houses._id) AS num_teas\"\n\tvar opened = function(e, c, d) { return \"<b>Opened</b>: \" + (c == null ? \"\" : c).split(\"T\")[0]; };\n\tcolmap = [\n\t\t[\"thName\", function(e, c, d) { return c }],\n\t\t[\"State\", true],\n\t\t[\"Region\", true],\n\t\t[\"District\", true],\n\t\t[\"Neighborhood\", br(\"Neighborhood\")],\n\t\t[\"ttName\", br(\"Specialty\")],\n\t\t[\"Date_Opened\", opened],\n\t\t[\"Customers\", \"Number of Customers: \"],\n\t\t[\"Visits\", br(\"Total Number of Visits\")],\n\t\t[\"Location_latitude\", \"Latitude (GPS): \"],\n\t\t[\"Location_longitude\", br(\"Longitude (GPS)\", \"<br /><br /><b>Services</b>:\")],\n\t\t[\"Iced\", check(\"Iced\")],\n\t\t[\"Hot\", check(\"Hot\")],\n\t\t[\"WiFi\", function(e, c, d) { return check(\"WiFi\")(e, c, d) + \"<br /><h3>Contact Information</h3>\"; }],\n\t\t[\"Store_Owner\", true],\n\t\t[\"Phone_Number\", \"Mobile number: \"],\n\t\t[\"num_teas\", function (e, c, d) {\n\t\t\todkTables.setSubListView(\"Tea_inventory\", \"House_id = ?\", [row_id], \"config/assets/Tea_inventory_list.html#Tea_inventory/thName = ?/\" + d.getData(0, \"thName\"));\n\t\t\treturn \"<span onClick='openTeas();' style='color: blue; text-decoration: underline;'>\" + c + \" tea\" + (c.toString() == 1 ? \"\" : \"s\") + \"</span>\";\n\t\t}],\n\t]\n\tcolmap = [\n\t\t{\"column\": \"thName\", \"callback\": function(e, c, d) { return c; }},\n\t\t{\"column\": \"State\"},\n\t\t{\"column\": \"Region\"},\n\t\t{\"column\": \"District\"},\n\t\t{\"column\": \"Neighborhood\", \"callback\": br(\"Neighborhood\")},\n\t\t{\"column\": \"ttName\", \"callback\": br(\"Specialty\")},\n\t\t{\"column\": \"Date_Opened\", \"callback\": opened},\n\t\t{\"column\": \"Customers\", \"display_name\": \"Number of Customers: \"},\n\t\t{\"column\": \"Visits\", \"callback\": br(\"Total Number of Visits\")},\n\t\t{\"column\": \"Location_latitude\", \"display_name\": \"Latitude (GPS): \"},\n\t\t{\"column\": \"Location_longitude\", \"callback\": br(\"Longitude (GPS)\", \"<br /><br /><b>Services</b>:\")},\n\t\t{\"column\": \"Iced\", \"callback\": check(\"Iced\")},\n\t\t{\"column\": \"Hot\", \"callback\": check(\"Hot\")},\n\t\t{\"column\": \"WiFi\", \"callback\": function(e, c, d) { return check(\"WiFi\")(e, c, d) + \"<br /><h3>Contact Information</h3>\"; }},\n\t\t{\"column\": \"Store_Owner\"},\n\t\t{\"column\": \"Phone_Number\", \"display_name\": \"Mobile number: \"},\n\t\t{\"column\": \"num_teas\", \"callback\": function(e, c, d) {\n\t\t\todkTables.setSubListView(\"Tea_inventory\", \"House_id = ?\", [row_id], \"config/assets/Tea_inventory_list.html#Tea_inventory/thName = ?/\" + d.getData(0, \"thName\"));\n\t\t\treturn \"<span onClick='openTeas();' style='color: blue; text-decoration: underline;'>\" + c + \" tea\" + (c.toString() == 1 ? \"\" : \"s\") + \"</span>\";\n\t\t}}\n\t]\n\twindow.openTeas = function openTeas() {\n\t\todkTables.openTableToListView({}, \"Tea_inventory\", \"House_id = ?\", [row_id], \"config/assets/Tea_inventory_list.html#Tea_inventory/thName = ?/\" + cached_d.getData(0, \"thName\"));\n\t}\n","");

helper.make_detail("Tea_inventory_detail.html","","","\tvar br = function(col, extra) {\n\t\treturn function(e, c, d) { return \"<b>\" + col + \"</b>: \" + c + (extra ? extra : \"<br />\"); };\n\t}\n\tvar check = function(col, accepting, type) {\n\t\tif (accepting === undefined) {\n\t\t\taccepting = function(e, c, d) {\n\t\t\t\treturn c.toUpperCase() == \"YES\";\n\t\t\t}\n\t\t}\n\t\tif (type === undefined) type = \"checkbox\"\n\t\treturn function(e, c, d) {\n\t\t\treturn \"<input disabled type='\"+type+\"' \" + (accepting(e, c, d) ? \"checked=checked\" : \"\") + \" /><b>\" + col + \"</b>\";\n\t\t};\n\t}\n\tvar selected = function(a, b) {\n\t\tif (a == null) return false;\n\t\tif (a[0] == \"[\") {\n\t\t\treturn jsonParse(a).indexOf(b) >= 0;\n\t\t}\n\t\treturn a.toUpperCase() == b.toUpperCase();\n\t}\n\n\tmain_col = \"tiName\";\n\ttable_id = \"Tea_inventory\";\n\tglobal_join = \"Tea_houses ON Tea_houses._id = Tea_inventory.House_id JOIN Tea_types ON Tea_types._id = Tea_inventory.Type_id\"\n\tglobal_which_cols_to_select = \"*, Tea_types.Name AS ttName, Tea_houses.Name AS thName, Tea_inventory.Name AS tiName\"\n\tcolmap = [\n\t\t[\"tiName\", function(e, c, d) { return c }],\n\t\t[\"ttName\", \"Type: \"],\n\t\t[\"Price_8oz\", \"8oz: \"],\n\t\t[\"Price_12oz\", \"12oz: \"],\n\t\t[\"Price_16oz\", function(e, c, d) { return \"<b>16oz</b>: \" + c + \"<br /><br /><b>Offered</b>:\" }],\n\t\t[\"Iced\", check(\"Iced\")],\n\t\t[\"Hot\", check(\"Hot\")],\n\t\t[\"Loose_Leaf\", check(\"Loose Leaf\")],\n\t\t[\"Bags\", check(\"Bags\")],\n\t]\n\tcolmap = [\n\t\t{\"column\": \"tiName\", \"callback\": function(e, c, d) { return c; }},\n\t\t{\"column\": \"ttName\", \"display_name\": \"Type: \"},\n\t\t{\"column\": \"Price_8oz\", \"display_name\": \"8oz: \"},\n\t\t{\"column\": \"Price_12oz\", \"display_name\": \"12oz: \"},\n\t\t{\"column\": \"Price_16oz\", \"callback\": function(e, c, d) { return \"<b>16oz</b>: \" + c + \"<br /><br /><b>Offered</b>:\"; }},\n\t\t{\"column\": \"Iced\", \"callback\": check(\"Iced\")},\n\t\t{\"column\": \"Hot\", \"callback\": check(\"Hot\")},\n\t\t{\"column\": \"Loose_Leaf\", \"callback\": check(\"Loose Leaf\")},\n\t\t{\"column\": \"Bags\", \"callback\": check(\"Bags\")}\n\t]\n","");

helper.make_detail("Tea_types_detail.html","","","\tvar br = function(col, extra) {\n\t\treturn function(e, c, d) { return \"<b>\" + col + \"</b>: \" + c + (extra ? extra : \"<br />\"); };\n\t}\n\tvar check = function(col, accepting, type) {\n\t\tif (accepting === undefined) {\n\t\t\taccepting = function(e, c, d) {\n\t\t\t\treturn c.toUpperCase() == \"YES\";\n\t\t\t}\n\t\t}\n\t\tif (type === undefined) type = \"checkbox\"\n\t\treturn function(e, c, d) {\n\t\t\treturn \"<input disabled type='\"+type+\"' \" + (accepting(e, c, d) ? \"checked=checked\" : \"\") + \" /><b>\" + col + \"</b>\";\n\t\t};\n\t}\n\tvar selected = function(a, b) {\n\t\tif (a == null) return false;\n\t\tif (a[0] == \"[\") {\n\t\t\treturn jsonParse(a).indexOf(b) >= 0;\n\t\t}\n\t\treturn a.toUpperCase() == b.toUpperCase();\n\t}\n\n\tmain_col = \"Name\";\n\ttable_id = \"Tea_types\";\n\tcolmap = [\n\t\t[\"Name\", function(e, c, d) { return c }],\n\t\t[\"Origin\", br(\"Origin\", \"<br /><br />Details:\")],\n\t\t[\"Caffeinated\", check(\"Caffeinated\")],\n\t\t[\"Fermented\", check(\"Fermented\")],\n\t]\n\tcolmap = [\n\t\t{\"column\": \"Name\", \"callback\": function(e, c, d) { return c; }},\n\t\t{\"column\": \"Origin\", \"callback\": br(\"Origin\", \"<br /><br />Details:\")},\n\t\t{\"column\": \"Caffeinated\", \"callback\": check(\"Caffeinated\")},\n\t\t{\"column\": \"Fermented\", \"callback\": check(\"Fermented\")}\n\t]\n","");

helper.make_index("teatime.html","\tlist_views = {\n\t\t\"Tea_houses\": \"config/assets/Tea_houses_list.html\",\n\t\t\"Tea_types\": \"config/assets/Tea_types_list.html\",\n\t\t\"Tea_inventory\": \"config/assets/Tea_inventory_list.html\",\n\t}\n\tmenu = {\"label\": \"Tea Demo\", \"type\": \"menu\", \"contents\": [\n\t\t{\"label\": \"View Tea Houses (try searching for \\\"Hill\\\")\", \"type\": \"list_view\", \"table\": \"Tea_houses\"},\n\t\t{\"label\": \"View Tea Houses on a Map\", \"type\": \"js\", \"function\": function() { odkTables.openTableToMapView(null, \"Tea_Houses\", null, null, \"config/assets/Tea_houses_list.html\"); }},\n\t\t{\"label\": \"View Teas\", \"type\": \"list_view\", \"table\": \"Tea_inventory\"},\n\t\t{\"label\": \"View Teas by Tea House\", \"type\": \"group_by\", \"table\": \"Tea_inventory\", \"grouping\": \"thName\"},\n\t\t{\"label\": \"View Tea Types\", \"type\": \"list_view\", \"table\": \"Tea_types\"},\n\t]}\n","body {\n\tbackground: url('img/teaBackground.jpg') no-repeat center/cover fixed;\n}\n#title {\n\tcolor: white;\n\twidth: 100%;\n\tdisplay: block;\n\tbox-shadow: none;\n\tfont-family: arial;\n\tborder-bottom: 2px solid #38c0f4;\n\tbackground: none;\n\tmargin-left: 0px;\n\tmargin-right: 0px;\n\tfont-size: 35px;\n\tpadding-top: 5px;\n\tpadding-bottom: 5px;\n\tmargin-bottom: 25px;\n\tfont-weight: bold;\n}\n");

