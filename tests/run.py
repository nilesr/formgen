import sys
sys.path.append(".")
import utils, os, subprocess, shutil
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

setup("good.py")
utils.make("default", False, True)
cleanup()

cleanup_all()