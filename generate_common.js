window.odkCommonDefinitions = {_tokens: {}};
// used in both display and fake_translate, just stuff that the translatable object might be wrapped in
var possible_wrapped = ["prompt", "title"];

// Mocks translation, much faster than actual translation
window.fake_translate = function fake_translate(thing) {
    // Can't translate undefined
    if (thing === undefined) return _t("Error translating ") + thing;

    // This will be hit eventually in a recursive call
    if (typeof(thing) == "string") {
        return thing; 
    }

    // A list of all the things the text might be wrapped in.
    // For real translation, we wouldn't do this, but for fake translation, attempt to automatically unwrap things like normal but also unwrap from the device default locale (sometimes "default", sometimes "_")
    var possible_wrapped_full = possible_wrapped.concat(["default", "_"]);
    for (var i = 0; i < possible_wrapped_full.length; i++) {
        // if thing is like {"default": inner} then return fake_translate(inner)
        // but also do that for everything in possible_wrapped_full not just "default"
        if (thing[possible_wrapped_full[i]] !== undefined) {
            return fake_translate(thing[possible_wrapped_full[i]]);
        }
    }

    // i18nFieldNames is usually ["text", "audio", "video", "image"]
    // Since an object might have multiple of these, like {"text": "Egret selected", "image": "media/egret.jpeg"}
    // and we want to extract all of them, let display_update_result concatenate them together into
    // "Egret selected<img src='media/egret.jpeg' />" for us, and run display_update_result once for each field type
    var result = "";
    for (var j = 0; j < odkCommon.i18nFieldNames.length; j++) {
        if (thing[odkCommon.i18nFieldNames[j]] !== undefined) {
            result = display_update_result(result, thing[odkCommon.i18nFieldNames[j]], odkCommon.i18nFieldNames[j]);
        }
    }

    // If we were able to find at least one of the four field types, we're good
    if (result.length > 0) {
        return result;
    }

    // Otherwise, we have no idea what kind of object this is. Sorry!
    return _t("Error fake translating ") + JSON.stringify(thing);
};

// Helper function for display and fake_translate
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

// This is an unfortunately named function, it should really be called translate, not display
window.display = function display(thing) {
  if (typeof(thing) == "string") return thing;
	if (typeof(thing) == "undefined") return _t("Can't translate undefined!");
    for (var i = 0; i < possible_wrapped.length; i++) {
        if (thing[possible_wrapped[i]] !== undefined) {
            return display(thing[possible_wrapped[i]]);
        }
    }
    // if we get {text: "something"}, don't bother asking odkCommon to do it, just call fake_translate
	// however if we get {text: {en_US: "a", hindi: "b"}} we should continue with the real translation instead
    for (var j = 0; j < odkCommon.i18nFieldNames.length; j++) {
        if (typeof(thing[odkCommon.i18nFieldNames[j]]) == "string") {
            return fake_translate(thing);
        }
    }

    // Insert it into odkCommonDefinitions so that we can pass it to localizeTokenField, which
    // only takes a key into odkCommonDefinitions because the whole translation system was designed poorly
    var id = newGuid();
    window.odkCommonDefinitions._tokens[id] = thing;

    // i18nFieldNames is usually ["text", "audio", "video", "image"]
    // Since an object might have multiple of these, like {"text": "Egret selected", "image": "media/egret.jpeg"}
    // and we want to extract all of them, let display_update_result concatenate them together into
    // "Egret selected<img src='media/egret.jpeg' />" for us, and run display_update_result once for each field type
    var result = "";
    for (i = 0; i < odkCommon.i18nFieldNames.length; i++) {
        var field = odkCommon.i18nFieldNames[i];
        this_result = odkCommon.localizeTokenField(odkCommon.getPreferredLocale(), id, field);
        if (this_result === true) return true; // used in __tr for passthrough translations
        result = display_update_result(result, this_result, field);
    }
    if (result.length === 0) {
        return _t("Couldn't translate ") + JSON.stringify(thing);
    }
    odkCommonDefinitions[id] = null; // let it be garbage collected
    return result;
};

// Helper function for newGuid
var S4 = function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1); 
};
// does what it says on the box
window.newGuid = function newGuid() {
    return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3) + "-" + S4() + "-" + S4() + S4() + S4()).toLowerCase();
};

// At one time, all pages called these two functions to open a link. Then it was easy to quickly swap out browser-based
// navigation for activity/doAction based navigation. However, they aren't really used anymore
window.page_go = function page_go(location) {
    //document.location.href = location;
    odkTables.launchHTML({}, location);
};
window.page_back = function page_back() {
    //window.history.back();
    odkCommon.closeWindow(-1, null);
};

// Javascript will refuse to parse json that uses single quotes instead of double quotes, 
window.jsonParse = function jsonParse(text) {
    try {
        return JSON.parse(text);
    } catch (e) {
        new_text = text.replace(/\'/g, '"');
        try {
            return JSON.parse(new_text);
        } catch (e) {
            // this is six backslashes in python, becomes three in the javascript,
            // becomes a string literal of a backslash followed by a single quote
            new_text = text.replace(/\"/g, "\\\"")
            new_text = new_text.replace(/\'/g, '"');
            // This is a last-ditch effort to save the situation, and it might still fail. The basic idea is
            // {'text': 'He said "Ow"'} -> {'text': 'He said \"Ow\"'} -> {"text": "He said \"Ow\""}
            // THIS MAY STILL THROW AN EXCEPTION
            return JSON.parse(new_text)
        }
    }
};
// Tries to translate the given column name, and if there's no translation, at least it will make it look pretty
// Even in the default app, no columns have translations, so whatever
window.displayCol = function constructSimpleDisplayName(name, metadata) {
    // Otherwise remove anything after the dot, if it's a group by column in a list view it may be in the form of table_id.column_id
    if (name.indexOf(".") > 0) {
        name = name.split(".", 2)[1]
    }
    // first check the translations we pulled from the db's kvs
    if (metadata) {
        var kvs = metadata.keyValueStoreList;
        var kvslen = kvs.length;
        for (var i = 0; i < kvslen; i++) {
            var entry = kvs[i];
            if (entry.partition == "Column" && entry.aspect == name && (entry.key == "displayName" || entry.key == "display_name")) {
                return display(jsonParse(entry.value));
            }
        }
    }
    // if it's a special column, like _sync_state or _savepoint_type, just return it unchanged
    if (name[0] == "_") return name;
    // Pretty print it
    return pretty(name);
};
// Pretty prints stuff with underscores in them. First it replaces underscores with spaces, then capitalizes each word.
window.pretty = function pretty(name) {
    name = name.replace(/_/g, " "); // can't just replace("_", " ") or it will only hit the first instance
    var sections = name.split(" ");
    var new_name = ""
    for (var i = 0; i < sections.length; i++) {
        if (sections[i].length > 0) {
            if (new_name.length > 0) new_name += " "
            new_name += sections[i][0].toUpperCase() + sections[i].substr(1);
        }
    }
    return new_name;
}
// Retrieves what should be displayed on screen for the given column name. First tries to pull it from
// optional_pair, which is supposedly an entry in allowed_group_bys, but if that's not set it tries to
// pull it from allowed_group_bys, and if that doesn't contain it it just returns the translated column name
window.get_from_allowed_group_bys = function get_from_allowed_group_bys(allowed_group_bys, colname, optional_pair, metadata) {
    // If we have no allowed_group_bys, always just translate the column name and leave it at that
    if (!allowed_group_bys) {
        optional_pair = [colname, true];
    }
    // If we weren't given an entry in allowed_group_bys, try and find the right entry
    if (!optional_pair) {
        for (var i = 0; i < allowed_group_bys.length; i++) {
            if (allowed_group_bys[i][0] == colname) {
                optional_pair = allowed_group_bys[i];
                break;
            }
        }
    }
    // If we couldn't find it in allowed_group_bys, just translate it normally
    if (!optional_pair) optional_pair = [colname, true]
    // For a full spec see README.md
    // if the user specified true, translate the column, if they specified false, return the exact column id
    // otherwise show the string the user specified
    if (optional_pair[1] === true) {
        return displayCol(optional_pair[0], metadata);
    } else if (optional_pair[1] === false) {
        return optional_pair[0];
    } else {
        return optional_pair[1];
    }
}
// helper function to get the relative path to where we are now. So if window.location.href
// is /coldchain/config/assets/refrigerators.html#refrigerator_type then it will
// return config/assets/refrigerators.html , which we can then add a hash to and pass to odkTables.launchHTML
var clean_href = function clean_href() {
    var href = window.location.href.split("#")[0]
    href = href.split("_formgen_replace_appname", 2)[1]
    return href;
}

var __tr = function __tr(s) {
    console.log("Was going to translate " + s);
    //return ["ok", "TEMP!!!!"]
    var found = formgen_specific_translations[s];
    if (found != undefined) {
      result = display(found);
      if (result === true) return ["ok", s];
      return ["ok", result];
    }
    found = user_translations[s];
    if (found != undefined) {
      result = display(found);
      if (result === true) return ["ok", s];
      return ["ok", result];
    }
    return ["error", s];
}

window._t = function(s) {
    var result = __tr(s);
    if (result[0] == "ok") return result[1];
    alert("Could not translate " + s);
    console.log("_t could not translate " + s)
    return s;
}
window._tu = function(s) {
    var result = __tr(s);
    if (result[0] == "ok") return result[1];
    console.log("_tu could not translate " + s)
    odkData.addRow("m_logs", {"notes": "_tu failed to translate '''" + s + "''' on the page " + window.location.href}, newGuid());
    return s;
}
var user_translations = _formgen_replace_user_translations

var formgen_specific_translations = {
    "Prompt for database column ": {"text": {
        "en_US": true,
        "es_ES": "Prompt por la columna "
    }},
    " not found on the screen! Will be stored in the database as null!": {"text": {
        "en_US": true,
        "es_ES": " no encontrado en el viento! Estará en el baso de datos como null!"
    }},
    "Unknown query type ": {"text": {
        "en_US": true,
        "es_ES": "No conozco la forma de popular opciones: "
    }},
    "Failed to start cross-table query: ": {"text": {
        "en_US": true,
        "es_ES": "No se pudo empezar el poblar de opciones de una tabla: "
    }},
    "Unexpected failure": {"text": {
        "en_US": true,
        "es_ES": ""
    }},
    "This shouldn't be possible, don't know how to update screen column ": {"text": {
        "en_US": true,
        "es_ES": "Este no debe ser posible, no hay forma de cambiar el texto en el viento para la celuda "
    }},
    "Unexpected failure to save row": {"text": {
        "en_US": true,
        "es_ES": "Inesperadamente no se puede salvar la fila"
    }},
    "Error saving row: ": {"text": {
        "en_US": true,
        "es_ES": "Inesperadamente no se puede salvar la fila"
    }},
    "An error occurred while loading the page. ": {"text": {
        "en_US": true,
        "es_ES": "Se ha occurido un error mientras cargando este viento. "
    }},
    "Error, location providers are disabled.": {"text": {
        "en_US": true,
        "es_ES": "Error, provisor de ubicacion no está eneblado"
    }},
    "Unknown type in dispatch struct!": {"text": {
        "en_US": true,
        "es_ES": "Tipo de pregunta en la estructura de envío no conocido"
    }},
    "Error translating ": {"text": {
        "en_US": true,
        "es_ES": "Error al traducir "
    }},
    "Are you sure? All entered data will be deleted.": {"text": {
        "en_US": true,
        "es_ES": "¿Está usted seguro? Todos los datos en este fila será perdido."
    }},
    "Unexpected error deleting row: ": {"text": {
        "en_US": true,
        "es_ES": "Inesperadamente no se puede eliminar la fila"
    }},
    "Error launching ": {"text": {
        "en_US": true,
        "es_ES": "Inesperadamente no se puede lanzar "
    }},
    "yes": {"text": {
        "en_US": true,
        "es_ES": "sí"
    }},
    "no": {"text": {
        "en_US": true,
        "es_ES": "no"
    }},
    "No row id in uri, beginning new instance with id ": {"text": {
        "en_US": true,
        "es_ES": "No se puede hallar el id de la fila en el URL, empezando una fila nueva"
    }},
    "Save incomplete": {"text": {
        "en_US": true,
        "es_ES": "Salvar como no completado"
    }},
    "Cancel and delete row": {"text": {
        "en_US": true,
        "es_ES": "Cancelar e eliminar fila"
    }},
    "Next": {"text": {
        "en_US": true,
        "es_ES": "Adelante!"
    }},
    "Back": {"text": {
        "en_US": true,
        "es_ES": "Retirarse"
    }},
    "Finalize": {"text": {
        "en_US": true,
        "es_ES": "Finalizar"
    }},
    "Can't translate undefined!": {"text": {
        "en_US": true,
        "es_ES": "¡No se puede traducir texto lo que no existe!"
    }},
    "Error fake translating ": {"text": {
        "en_US": true,
        "es_ES": "Error al pretender a traducir "
    }},
    "Couldn't translate ": {"text": {
        "en_US": true,
        "es_ES": "No se puede traducir "
    }},
    "Please confirm deletion of row ": {"text": {
        "en_US": true,
        "es_ES": "Por favor confirme que quiere usted eliminar la fila "
    }},
    "Failed to _delete row - ": {"text": {
        "en_US": true,
        "es_ES": "Inesperadamente no se puede _eliminar la fila "
    }},
    "Row not found!": {"text": {
        "en_US": true,
        "es_ES": "¡Fila no encontrada!"
    }},
    "Error querying data: ": {"text": {
        "en_US": true,
        "es_ES": "Error al pedir data: "
    }},
    "Delete Row": {"text": {
        "en_US": true,
        "es_ES": "Eliminar fila"
    }},
    "Edit Row": {"text": {
        "en_US": true,
        "es_ES": "Editar fila"
    }},
    "Edit": {"text": {
        "en_US": true,
        "es_ES": "Editar"
    }},
    "Delete": {"text": {
        "en_US": true,
        "es_ES": "Eliminar"
    }},
    "By ": {"text": {
        "en_US": true,
        "es_ES": "En grupos de "
    }},
    "Unknown selector in query hash": {"text": {
        "en_US": true,
        "es_ES": "El seleccionador encontrado en el URL es desconocido"
    }},
    "Couldn't guess instance col. Bailing out, you're on your own.": {"text": {
        "en_US": true,
        "es_ES": "No se puede automáticamente detectar cual celda por demostrar, demostrando el id"
    }},
    "No table id! Please set it in customJsOl or pass it in the url hash": {"text": {
        "en_US": true,
        "es_ES": "¡No hay ID de tabla! Por favor ponerlo en customJsOl o darla en el URL"
    }},
    "Unexpected error ": {"text": {
        "en_US": true,
        "es_ES": "Error inesperado"
    }},
    "Could not get columns: ": {"text": {
        "en_US": true,
        "es_ES": "No se puede obtener las columnas"
    }},
    "Still searching...": {"text": {
        "en_US": true,
        "es_ES": "Todavia buscando..."
    }},
    "No results": {"text": {
        "en_US": true,
        "es_ES": "Sin resultos"
    }},
    "rows ": {"text": {
        "en_US": true,
        "es_ES": "filas "
    }},
    "Showing ": {"text": {
        "en_US": true,
        "es_ES": "Demostrando "
    }},
    " of ": {"text": {
        "en_US": true,
        "es_ES": " de "
    }},
    " distinct values of ": {"text": {
        "en_US": true,
        "es_ES": " valores unicos de "
    }},
    " rows where ": {"text": {
        "en_US": true,
        "es_ES": " filas donde "
    }},
    " is ": {"text": {
        "en_US": true,
        "es_ES": " está "
    }},
    "Add Row": {"text": {
        "en_US": true,
        "es_ES": "Aggregar fila"
    }},
    "Group by": {"text": {
        "en_US": true,
        "es_ES": "Ver in grupos de..."
    }},
    "Go": {"text": {
        "en_US": true,
        "es_ES": "¡Ir!"
    }},
    "Previous Page": {"text": {
        "en_US": true,
        "es_ES": "Previo"
    }},
    "Next Page": {"text": {
        "en_US": true,
        "es_ES": "Siguiente"
    }},
    "Search": {"text": {
        "en_US": true,
        "es_ES": "Buscar"
    }},
    "List of tables": {"text": {
        "en_US": true,
        "es_ES": "Lista de tablas"
    }},
    "Failure! ": {"text": {
        "en_US": true,
        "es_ES": "¡Error!"
    }},
}
