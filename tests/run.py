import sys
sys.path.append(".")
import utils, os, subprocess, shutil, traceback, form_generator, bs4, json
try:
	shutil.rmtree(utils.appdesigner + "/app/config/tables/temperatureSensor");
except:
	pass
if os.path.exists("app_specific_default.py.bac"):
	utils.message("Tests were previously aborted uncleanly - to avoid data loss, not overwriting app_specific_default.py.bac")
	sys.exit(1)
if os.path.exists("app_specific_default.py"):
	os.rename("app_specific_default.py", "app_specific_default.py.bac")

def setup(file):
	shutil.copyfile("tests/" + file, "app_specific_default.py")
def cleanup():
	os.remove("app_specific_default.py");
def fname(file):
	return utils.appdesigner + "/app/config/assets/" + file
def get(file):
	return open(fname(file), "r").read();
def scripts(file):
	soup = bs4.BeautifulSoup(get(file), "html.parser");
	s = soup.find_all("script")
	s = [x.text.strip().encode("utf-8") for x in s]
	s = [x for x in s if len(x) > 0]
	result = []
	for x in s:
		tempfile = utils.tmp + "/script_" + form_generator.gensym();
		open(tempfile, "wb").write(x)
		result.append(json.loads(subprocess.check_output(["acorn", tempfile])))
		os.remove(tempfile)
	return result
def cleanup_all():
	if os.path.exists("app_specific_default.py.bac"):
		os.rename("app_specific_default.py.bac", "app_specific_default.py")
	subprocess.call(["make", "clean"])
def make():
	# we MUST spawn a new process instead of using utils.make because python won't recognize that we swapped out app_specific_default.py because it thinks it's already imported it
	subprocess.check_call(["python3",  "-c",  "import sys; sys.path.append(\".\"); import utils; utils.make(\"default\", False, True, True);"])


all_passed = True;
try:
	# Should work even in the simplest case
	print("Building with an empty config")
	setup("empty.py")
	make();
	cleanup();

	print("Building with a default config")
	setup("good.py")
	make();
	# .index will throw an exception if the string isn't found
	print("Testing that Tea_houses_list.html contains the given configuration")
	get("Tea_houses_list.html").index("*, Tea_types.Name as ttName")

	print("Testing that plot.html contains the given configuration")
	get("plot.html").index("Not planting")
	s = scripts("plot.html")
	worked = False
	print("Testing that display_col_wrapper is null")
	for script in s:
		try:
			dcw_decl = script["body"][2]
		except:
			continue
		if dcw_decl["type"] == "VariableDeclaration" and dcw_decl["declarations"][0]["id"]["name"] == "display_col_wrapper" and dcw_decl["declarations"][0]["init"]["value"] is None:
			worked = True
	assert(worked)
	print("Testing customJsOl")
	worked = False
	for script in s:
		try:
			customJsOl = script["body"][4]["declarations"][0]
		except:
			continue
		print("Testing that planting_cb checks if the given argument is null")
		assert(customJsOl["id"]["name"] == "customJsOl")
		customJsOl = customJsOl["init"]["body"]["body"]
		planting_cb = customJsOl[0]["declarations"][0]
		assert(planting_cb["id"]["name"] == "planting_cb")
		planting_cb = planting_cb["init"]["body"]["body"]
		first_if = planting_cb[0]
		assert(first_if["type"] == "IfStatement")
		assert(first_if["test"]["type"] == "LogicalExpression")
		assert(first_if["test"]["left"]["left"]["name"] == "planting")
		assert(planting_cb[1]["type"] == "ReturnStatement")
		print("Testing that display_subcol was set correctly")
		display_subcol = customJsOl[1]["expression"]
		assert(display_subcol["type"] == "AssignmentExpression")
		assert(display_subcol["left"]["name"] == "display_subcol")
		display_subcol = display_subcol["right"]
		assert(display_subcol["type"] == "ArrayExpression")
		display_subcol = display_subcol["elements"]
		assert(len(display_subcol) == 3)
		assert(display_subcol[0]["elements"][0]["name"] == "planting_cb")
		assert(display_subcol[0]["elements"][1]["value"] == "planting")
		assert(display_subcol[0]["elements"][2]["value"] == False)
		assert(display_subcol[1]["elements"][0]["value"] == ", ")
		assert(display_subcol[1]["elements"][1]["value"] == "plot_size")
		assert(display_subcol[1]["elements"][2]["value"] == False)
		assert(display_subcol[2]["elements"][0]["value"] == " hectares")
		assert(display_subcol[2]["elements"][1]["value"] is None)
		assert(display_subcol[2]["elements"][2]["value"] == True)
		print("Testing that table_id was set correctly")
		table_id = customJsOl[2]["expression"]["right"]["value"]
		assert(table_id == "plot")
		worked = True
	assert(worked)

	print("Testing that plot.html contains the given CSS")
	get("plot.html").index("color: blue")
	get("plot.html").index("Custom CSS")

	print("Testing that plot.html contains the given Html")
	get("plot.html").index("<h1>Custom HTML")

	print("Testing that plot.html contains the given search config")
	get("plot.html").index("Custom JS run when you search")

	print("Testing that plot.html contains the given generic config")
	get("plot.html").index("Custom JS put in a random script tag")

	print("Testing that selects_list.html contains the given config")
	get("selects_list.html").index("Didn't see anything")
	cleanup()

	print("Building with syntax errors")
	worked = False;
	setup("bad.py")
	try:
		make();
	except:
		print()
		worked = True
	print("Testing that the build was aborted on the syntax error")
	assert(worked)
	print("Testing that the build was aborted on the syntax error using a different method")
	assert(not os.path.exists(fname("some_other_file.html")))
	cleanup()
except:
	print(traceback.format_exc())
	utils.message("TEST FAILED")
	all_passed = False;
cleanup_all()

if all_passed: utils.message("ALL TESTS PASSED")