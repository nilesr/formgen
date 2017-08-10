import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();

helper.make_table("Tea_houses_list.html", "", "", """
	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"
	global_which_cols_to_select = "*, Tea_types.Name as ttName"
	display_subcol = [I'm an idiot user and I don't know what I'm doing, ["", "District", false], [", ", "Neighborhood", true]];
	table_id = "Tea_houses";
""", "", "")
helper.make_detail("some_other_file.html", "", "", "", "")


