import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();

helper.static_files.append("tests/bad2.html")
