import subprocess, glob, os, sys
sys.path.append(".")
import utils
tables = utils.get_tables();
for table in tables:
	subprocess.call(["adb", "pull", "/sdcard/opendatakit/default/config/tables/" + table + "/properties.csv", "properties.csv"])
	props = open("properties.csv", "r").read().split("\n")
	found = []
	for i in range(len(props)):
		row = props[i].split(",")
		if len(row) < 5: continue
		if row[2] == "defaultViewType":
			row[4] = "LIST"
			found.append("viewtype")
		if row[2] == "listViewFileName":
			row[4] = "config/assets/table.html#" + table
			found.append("listfile")
		if row[2] == "detailViewFileName":
			row[4] = "config/assets/detail.html"
			found.append("detailfile")
		props[i] = ",".join(row);
	if not "viewtype" in found:
		props.append("Table,default,defaultViewType,string,LIST")
	if not "listfile" in found:
		props.append("Table,default,listViewFileName,string,config/assets/table.html#" + table)
	if not "detailfile" in found:
		props.append("Table,default,detailViewFileName,string,config/assets/detail.html")
	open("properties.csv", "w").write("\n".join(props))
	subprocess.call(["adb", "push", "properties.csv", "/sdcard/opendatakit/default/config/tables/" + table + "/properties.csv"])
os.remove("properties.csv")
