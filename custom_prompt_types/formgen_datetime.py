def make_numeric_select(*args, **kwargs):
	pad = kwargs["pad"] if "pad" in kwargs else 0
	text = "<select>"
	text += "<option value='null'></option>"
	for i in range(*args):
		i = str(i)
		text += "<option value='" + i + "'>" + i.rjust(pad, "0") + "</option>"
	text += "</select>"
	return text
def make_datetime(tokens, raw_attrs):
	attrs = " ".join(raw_attrs)
	text = "<span class='datetime prompt user-defined-prompt' "+attrs+">"
	text += make_numeric_select(1970, 2021, pad = 0);
	text += "/"
	text += make_numeric_select(1, 13, pad = 2);
	text += "/"
	text += make_numeric_select(1, 31, pad = 2);
	text += "@"
	text += make_numeric_select(24, pad = 2);
	text += ":"
	text += make_numeric_select(60, pad = 2);
	text += "</span>"
	return tokens, text
datetime_js = """
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
	var day = get_at_idx(elem, 2);
	var hour = get_at_idx(elem, 3);
	var minute = get_at_idx(elem, 4);
	var seconds = Number(elem.getAttribute("data-sec"));
	var millis = Number(elem.getAttribute("data-millis"));
	if (year == null || month == null || day == null || hour == null || minute == null) return null;
	var date = new Date(year, month - 1, day - 1, hour, minute, seconds, millis);
	return odkCommon.toOdkTimeStampFromDate(date);
},
changeElement: function(elem, newdata) {
	var date = odkCommon.toDateFromOdkTimeStamp(newdata);
	if (date == null) date = new Date();
	var year = date.getYear() + 1900;
	var month = date.getMonth();
	var day = date.getDate();
	var hours = date.getHours();
	var minutes = date.getMinutes();
	elem.setAttribute("data-sec", date.getSeconds());
	elem.setAttribute("data-millis", date.getMilliseconds());
	if (newdata == null) {
		year = -1;
		month = -1;
		day = -1;
		hours = -1;
		minutes = -1;
	}
	elem.getElementsByTagName("select")[0].selectedIndex = year - 1970 + 1;
	elem.getElementsByTagName("select")[1].selectedIndex = month + 1;
	elem.getElementsByTagName("select")[2].selectedIndex = day + 1;
	elem.getElementsByTagName("select")[3].selectedIndex = hours + 1;
	elem.getElementsByTagName("select")[4].selectedIndex = minutes + 1;
	return true;
},
validate: function(elem) {
	return true;
}
"""

