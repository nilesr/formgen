var generic_callback = function generic_callback(e, c, d, which, pretty, optional_col_name) {
	if (optional_col_name == null || optional_col_name == undefined || typeof(optional_col_name) != "string") {
		optional_col_name = displayCol(which, d.getMetadata(), d.getTableId());
	} else {
		optional_col_name = _tu(optional_col_name);
	}
	wrapper = function(i) { return _tc(d, which, i); };
	if (pretty) wrapper = function(i) { return window.pretty(_tc(d, which, i.toString())); };
	if (c == null) c = "null"; // because null.toString() will throw an exception
	document.getElementById("inject-" + which).innerHTML = "<b>" + optional_col_name + "</b>: " + wrapper(c);
	document.getElementById("inject-" + which).classList.add("li-inner");
}
var build_generic_callback = function build_generic_callback(which, pretty, optional_col_name) {
	return function _generic_callback_wrapper(e, c, d) {
		if (typeof(pretty) == "string") {
			c = c + pretty;
			pretty = false;
		}
		if (typeof(pretty) == "function") {
			c = pretty(c)
			pretty = false;
		}
		return generic_callback(e, c, d, which, pretty, optional_col_name);
	}
}
