window.odkCommonDefinitions = {_tokens: {}};
var possible_wrapped = ["prompt", "title"]; // used in both display and fake_translate
window.fake_translate = function(thing) {
    //console.log("Fake translating " + thing);
    if (thing === undefined) return "Error translating " + thing;
    if (typeof(thing) == "string") return thing;
    var possible_wrapped_full = possible_wrapped.concat("default").concat("_");
    for (var i = 0; i < possible_wrapped_full.length; i++) {
        if (thing[possible_wrapped_full[i]] !== undefined) {
            return fake_translate(thing[possible_wrapped_full[i]]);
        }
    }
    var raw_field_names = odkCommon.i18nFieldNames;
    var result = "";
    for (var j = 0; j < raw_field_names.length; j++) {
        if (thing[raw_field_names[j]] !== undefined) {
            result = display_update_result(result, thing[raw_field_names[j]], raw_field_names[j]);
        }
    }
    if (result.length > 0) return result;
    return "Error fake translating " + JSON.stringify(thing);
};
window.display_update_result = function display_update_result(result, this_result, field) {
    if (!result) result = "";
    if (this_result !== null && this_result !== undefined && this_result.trim().length > 0) {
        if (field == "text") {
            result += this_result;
        }
        if (field == "audio") {
            result += "<audio controls='controls'><source src='" + this_result + "' /></audio>";
        }
        if (field == "video") {
            result += "<video controls='controls'><source src='" + this_result + "' /></video>";
        }
        if (field == "image") {
            result += "<img src='" + this_result + "' />";
        }
    }
    return result;
};
window.display = function display(thing) {
    if (typeof(thing) == "string") return thing;
	if (typeof(thing) == "undefined") return "Can't translate undefined!";
    // REMOVE THIS LINE BEFORE SHIPPING TO ANOTHER COUNTRY
    // Also breaks image choices
    //return fake_translate(thing);
    for (var i = 0; i < possible_wrapped.length; i++) {
        if (thing[possible_wrapped[i]] !== undefined) {
            return display(thing[possible_wrapped[i]]);
        }
    }
    // if we get {text: "something"}, don't bother asking odkCommon to do it
	// however if we get {text: {english: "a", hindi: "b"}} we should not call fake_translate and continue
    var raw_field_names = odkCommon.i18nFieldNames;
    for (var j = 0; j < raw_field_names.length; j++) {
        if (typeof(thing[raw_field_names[j]]) == "string") {
            return fake_translate(thing);
        }
    }

    var id = newGuid();
    window.odkCommonDefinitions._tokens[id] = thing;
    console.log("Translating " + JSON.stringify(window.odkCommonDefinitions._tokens[id]));
    var result = "";
    var found = false;
    for (i = 0; i < odkCommon.i18nFieldNames.length; i++) {
        var field = odkCommon.i18nFieldNames[i];
        this_result = odkCommon.localizeTokenField(odkCommon.getPreferredLocale(), id, field);
        //console.log(result);
        result = display_update_result(result, this_result, field);
    }
    if (result.length === 0) {
        return "Couldn't translate " + JSON.stringify(thing);
    }
    odkCommonDefinitions[id] = null; // let it be garbage collected
    return result;
};
var S4 = function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
};
window.newGuid = function newGuid() {
    return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
};
window.page_go = function page_go(location) {
    //document.location.href = location;
    odkTables.launchHTML({}, location);
};
window.page_back = function page_back() {
    //window.history.back();
    odkCommon.closeWindow(-1, null);
};
