var generic_callback = function generic_callback(element, columnValue, data, which, pretty, optional_col_name) {
	if (optional_col_name == null || optional_col_name == undefined || typeof(optional_col_name) != "string") {
		optional_col_name = displayCol(which, data.getMetadata(), data.getTableId());
	} else {
		optional_col_name = translate_user(optional_col_name);
	}
	wrapper = function(i) { return translate_choice(data, which, i); };
	if (pretty) wrapper = function(i) { return window.pretty(translate_choice(data, which, i.toString())); };
	if (columnValue == null) columnValue = "null"; // because null.toString() will throw an exception
	document.getElementById("inject-" + which).innerHTML = "<b>" + optional_col_name + "</b>: " + wrapper(columnValue);
	document.getElementById("inject-" + which).classList.add("li-inner");
}
var build_generic_callback = function build_generic_callback(which, pretty, optional_col_name) {
	return function _generic_callback_wrapper(element, columnValue, data) {
		if (typeof(pretty) == "string") {
			columnValue += pretty;
			pretty = false;
		}
		if (typeof(pretty) == "function") {
			columnValue = pretty(columnValue)
			pretty = false;
		}
		return generic_callback(element, columnValue, data, which, pretty, optional_col_name);
	}
}
