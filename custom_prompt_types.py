import sys
sys.path.append("custom_prompt_types")
import formgen_time as time, formgen_datetime as datetime
sys.path.insert(0, ".")
def make(utils):
	utils.register_custom_prompt_type("time", "time", time.make_time_html, time.time_js)
	utils.register_custom_prompt_type("datetime", "datetime", datetime.make_datetime, datetime.datetime_js)