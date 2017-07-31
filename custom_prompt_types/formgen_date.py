import sys
sys.path.append(".")
import formgen_datetime as datetime
def make_date(tokens, raw_attrs):
	attrs = " ".join(raw_attrs)
	text = "<span class='date prompt user-defined-prompt' "+attrs+">"
	text += "<select></select>"
	text += "/"
	text += "<select></select>"
	text += "/"
	text += "<select></select>"
	text += "</span>"
	return tokens, text
date_js = datetime.fill + """
screen_data: function(elem) {
	var get_at_idx = function get_at_idx(elem, idx) {
		var select = elem.getElementsByTagName("select")[idx];
		if (select.selectedOptions[0] != undefined) {
			if (select.selectedIndex == 0) return null;
			return Number(select.selectedOptions[0].value);
		}
	}
	var year = get_at_idx(elem, 0);
	var month = get_at_idx(elem, 1);
	var day = get_at_idx(elem, 2) + 1;
	var hour = Number(elem.getAttribute("data-hour"));
	var minute = Number(elem.getAttribute("data-minute"));
	var seconds = Number(elem.getAttribute("data-sec"));
	var millis = Number(elem.getAttribute("data-millis"));
	if (year == null || month == null || day == null) return null;
	var date = new Date(year, month- 1, day - 1, hour, minute, seconds, millis);
	if (elem.hasAttribute("data-time_format")) {
		var pad = this.pad
		return elem.getAttribute("data-time_format").replace("YYYY", date.getFullYear()).replace("YY", pad(date.getYear() % 100)).replace("DD", pad(d.getDate())).replace("hh", pad(d.getHours())).replace("MM", pad(d.getMinutes()));
	} else {
		return odkCommon.toOdkTimeStampFromDate(date);
	}

},
changeElement: function(elem, newdata) {
	var year = elem.getElementsByTagName("select")[0];
	if (year.children.length == 0) this.fill(year, 1970, 2020, 0);
	var month = elem.getElementsByTagName("select")[1];
	if (month.children.length == 0) this.fill(month, 1, 12, 0);
	var day = elem.getElementsByTagName("select")[2];
	if (day.children.length == 0) this.fill(day, 1, 31, 0);


	var date = odkCommon.toDateFromOdkTimeStamp(newdata);
	var year = -1;
	var month = -1;
	var day = -1;
	if (newdata != null) {
		year = Number(newdata.split("-")[0])
		month = Number(newdata.split("-")[1])
		day = Number(newdata.split("-")[2].split("T")[0])
		elem.setAttribute("data-hour", date.getHours());
		elem.setAttribute("data-minute", date.getMinutes());
		elem.setAttribute("data-sec", date.getSeconds());
		elem.setAttribute("data-millis", date.getMilliseconds());
	}
	elem.getElementsByTagName("select")[0].selectedIndex = year - 1970 + 1;
	elem.getElementsByTagName("select")[1].selectedIndex = month;
	elem.getElementsByTagName("select")[2].selectedIndex = day;
	return true;
},
validate: function(elem) {
	return true;
}
"""
