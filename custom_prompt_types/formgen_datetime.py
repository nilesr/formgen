fill = """
fill: function(elem, min, max, pad) {
	elem.appendChild(document.createElement("option"))
	for (var i = min; i <= max; i++) {
		var str = i.toString()
		while (str.length < pad) {
			str = "0" + str;
		}
		var child = document.createElement("option");
		child.value = i;
		child.innerText = str;
		elem.appendChild(child);
	}
},
pad:  function pad(thing) {
	while (thing.length < 2) {
		thing = "0" + thing;
	}
	return thing;
},
"""
def make_datetime(tokens, raw_attrs):
	attrs = " ".join(raw_attrs)
	text = "<span class='datetime prompt user-defined-prompt' "+attrs+">"
	text += "<select></select>"
	text += "/"
	text += "<select></select>"
	text += "/"
	text += "<select></select>"
	text += "@"
	text += "<select></select>"
	text += ":"
	text += "<select></select>"
	text += "</span>"
	return tokens, text
datetime_js = fill + """
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
	var year = elem.getElementsByTagName("select")[0];
	if (year.children.length == 0) this.fill(year, 1970, 2020, 0);
	var month = elem.getElementsByTagName("select")[1];
	if (month.children.length == 0) this.fill(month, 1, 12, 0);
	var day = elem.getElementsByTagName("select")[2];
	if (day.children.length == 0) this.fill(day, 1, 31, 0);
	var hour = elem.getElementsByTagName("select")[3];
	if (hour.children.length == 0) this.fill(hour, 0, 23, 0);
	var minute = elem.getElementsByTagName("select")[4];
	if (minute.children.length == 0) this.fill(minute, 0, 59, 2);


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

