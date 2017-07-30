import sys
sys.path.append(".")
import formgen_datetime as datetime
def make_time_html(tokens, raw_attrs):
	attrs = " ".join(raw_attrs)
	text = "<span class='time prompt user-defined-prompt' "+attrs+">"
	text += datetime.make_numeric_select(24);
	text += ":"
	text += datetime.make_numeric_select(60, pad = 2);
	text += "</span>"
	return tokens, text
time_js = """
screen_data: function(elem) {
	var hour = elem.getElementsByTagName("select")[0];
	if (hour.selectedOptions[0] !== undefined) {
		if (hour.selectedIndex == 0) return null;
		hour = Number(hour.selectedOptions[0].value);
	} else {
		hour = 0;
	}
	var minute = elem.getElementsByTagName("select")[1];
	if (minute.selectedOptions[0] !== undefined) {
		if (minute.selectedIndex == 0) return null;
		minute = Number(minute.selectedOptions[0].value)
	} else {
		minute = 0;
	}
	var date = new Date();
	date.setHours(hour);
	date.setMinutes(minute);
	date.setSeconds(Number(elem.getAttribute("data-sec")));
	date.setMilliseconds(Number(elem.getAttribute("data-millis")));
	return odkCommon.toOdkTimeFromDate(date);
},
changeElement: function(elem, newdata) {
	var date = odkCommon.toDateFromOdkTime(new Date(), newdata);
	if (date == null) date = new Date();
	var hours = date.getHours();
	var minutes = date.getMinutes();
	elem.setAttribute("data-sec", date.getSeconds());
	elem.setAttribute("data-millis", date.getMilliseconds());
	if (newdata == null) {
		hours = -1;
		minutes = -1;
	}
	elem.getElementsByTagName("select")[0].selectedIndex = hours + 1;
	elem.getElementsByTagName("select")[1].selectedIndex = minutes + 1;
	return true;
},
validate: function(elem) {
	return true;
}
"""
