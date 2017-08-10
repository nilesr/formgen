import sys
sys.path.append(".")
import utils, os, subprocess, shutil, traceback
try:
	shutil.rmtree(utils.appdesigner + "/app/config/tables/temperatureSensor");
except:
	pass
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
	print("Testing that Tea_houses_list.html contains the given config")
	get("Tea_houses_list.html").index("*, Tea_types.Name as ttName")
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