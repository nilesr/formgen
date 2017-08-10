import sys
sys.path.append(".")
import custom_helper
helper = custom_helper.helper();

helper.static_files.append("file_that_does_not_exist.html")
