## formgen 2

## Getting started

First, clone [the app designer repo](https://github.com/opendatakit/app-designer), and set the path of where you cloned it to in the `appdesigner` variable in `utils.py`

Then run `./build your_app_name` to generate forms and automatically copy them to your app designer repo. Add `--push` to have them sent to a connected device as well.

You can add --quiet for some prettier output, and If you're feeling lucky, you can also add --no-syntax to skip syntax checking, which will vastly improve speeds.

## Configuring list/detail views

By default, running `make` will generate a `list.html` and `detail.html`. These are generic files that you can set your list view or detail view filenames to and they will work ok, however they probably won't do what you need them to do. To add table specific configuration, create a file called `app_specific_yourappnamehere.py`. Copy the first four lines from one of the existing templates, or just copy and paste this in

	import sys
	sys.path.append(".")
	import custom_helper
	helper = custom_helper.helper();

That will let you access these helpful functions
	
	helper.make_table(filename, customHtml, customCss, customJsOnload, customJsSearch, customJsGeneric)
	helper.make_detail(filename, customHtml, customCss, customJsOnload, customJsGeneric)
	helper.make_index(filename, customJs, customCss)
	helper.make_graph(filename, customCss)
	helper.make_tabs(filename, customJs, customCss)

Since it's python, you can use docstrings (triple quotes) to enter multiple lines in the fields. If you have a lot of CSS or something, you might want to extract it to another file and pass in something like `open("form_style.css").read()` instead

Tip - if you set `allowed_tables = []` in onload, it will open/edit in survey instead of formgen no matter what.

### List views

customHtml will be appended at the end of the body, customCss in a style tag, customJsGeneric in a script tag, and customJsOnload at the end of the onload function. Most of those can be empty strings **BUT NOT customJsOnload**

in customJsOnload you MUST SET `table_id` to something, like

	table_id = "Tea_houses"

Also, the column to be displayed for each row in the list will be automatically detected from the instance column in the formDef.json settings. This is unpredictable and usually missing or wrong. It is strongly recommended that you set `display_col`, like

	display_col = "Name"

You can set `display_subcol` if you want more things displayed, like this

	display_subcol = [
		{"column": "ttName", "display_name": "Specialty: ", "newline": true},
		{"column": "District", "newline": false},
		{"column": "Neighborhood", "display_name": ", ", "newline": true}
	]

That display "Specialty: Herbal" on one line then "Seattle, Belltown" on the next

![](ss.png)

The `display_name` is displayed immediately before the value of that column, unless `callback` is provided instead.

If `column` is not provided, then `display_name` is displayed by itself.

If `callback` is provided, it's called with the second argument set to the column value, and whatever the function returns is displayed. For example:

	var sc_callback = function(element, columnValue, data, i) {
		  if (columnValue == "Black") {
			  return "This tea house specializes in Black Tea - Yuck!"
		  } else {
			  return "Specialty: " +  columnValue;
		  }
	};
	display_subcol = [{"column": "ttName", "callback": sc_callback, "newline": true}]

would display a snide remark about the tea houses specialty if it specializes in Black Tea, otherwise display it normally

Another example from selects:

	var cb = function(element, columnValue, data, i) {
		if (columnValue == null || columnValue == undefined || columnValue.trim().length == 0) return "Didn't see anything";
		var n = ""
		if ("aeiou".indexOf(columnValue[0].toLowerCase()) >= 0) n = "n"
		return "Saw a" + n + " " + columnValue;
	}
	display_subcol = [{"column": "bird", "callback": cb, "newline": true}]

which can display lines like "Didn't see anything", "Saw a robin", or "Saw an egret" on each row

The four arguments are `element`, the dom element that the text will be displayed inside of, `columnValue`, the database value of the requested column, `data`, the odkData object and `i`, the index of the row. So if you had a callback that needed data from another column, you can get it using `d.getData(i, "some_other_column")`

The callback functions can return html too.

You can also set `display_col_wrapper` to a function that returns what should be displayed, like this

	display_col_wrapper = function display_col_wrapper(d, i, c) {
		return c.split("T")[0];
	}
	display_col = "date_serviced"

This would display "2017-03-05" instead of "2017-03-05T00:00:00.0000000" in the `display_col` field

You can change the behavior of clicking on a row by changing the global `clicked` function. The default implementation is this

	var clicked = function clicked(table_id, row_id, data, i) {
		odkTables.openDetailView({}, table_id, row_id);
	}

If you wanted to open a detail with sub list view or something, just set clicked to something different in your customJsOl (without the leading `var`)

When you enter something into the search box, first it tries to find results `WHERE :display_col LIKE %:search%`

If no results are returned, it adds an OR clause for each column in `display_subcol`. So if you're in tea houses and you search for "Tea", it will show all the columns that have "Tea" in their name. But if you search for "Hill", it will first try and show all the columns that have Hill in their name, realize that there are no results, then (if you used the `display_subcol` above) show all the columns where `Name LIKE %Hill% OR District LIKE %Hill% OR Neighborhood LIKE %Hill%`, and there are several neighborhoods with Hill in their name so it will come back with some results.

If you want to search for a column but not display it, you could just write a callback function that returns "" and set the third value in the triplet to false. Bit of a hack but it works

To do a cross table query, set a JOIN, example from tea houses

	global_join = "Tea_types ON Tea_types._id = Tea_houses.Specialty_Type_id"

In this case, `Tea_houses` and `Tea_types` both have a column called Name, so you need to tell sqlite how to differentiate them. Do that by setting

	global_which_cols_to_select = "*, Tea_types.Name as ttName"

Unless your column names actually conflict this is usually unnecessary. If you need to do this, you'll know, it will display a big error when you try and load the list view

By default it will allow you to group on any column, and display the translated/prettified name in the listing. To configure which ones are allowed, set something like this

	allowed_group_bys = [
		{"column": "Specialty"},
		{"column": "District", "display_name": "District of the tea house"}
	]

Then your users won't be able to group by silly things like the location latitude

If you provide `display_name`, that is what is show in the list. It is also shown in the explanation for the relevant group by and collection views ("Displaying x-y of z unique values of `display_name goes here`" and "Displaying x-y of z rows where `display_name goes here` is `whatever the user selected`")

If you provide `pretty` and set it to false, and don't provide a display name, the raw column name is used.

If there's only one element in the list of `allowed_group_bys`, it's launched automatically if the user clicks the group by button.

If you set `allowed_group_bys` to an empty list, the group by button won't be displayed

If you set `forMapView` to true, your list view will be way slower but it will open the selected marker as soon as the user selects it. Map view support is abysmal, mostly due to getViewData. I don't recommend map views in formgen to my worst enemies.

### Detail views

For `make_detail`, you almost certainly need to set `main_col` to something, so for tea houses

	main_col = "Name"

For joins, set `global_join` the same as lists. You can also set `global_which_cols_to_select` if needed.

By default, it will display every single column in the list. To configure how it gets shown, set `colmap`.

`colmap` is a list of objects describing which columns to show. If a colmap is set, a column is not displayed in the detail view unless it is found in `colmap`. Each pair is in the form of `[column_id, text_to_display]`, and the ul on the screen will appear as `text_to_display: value_of_that_column`.

Your `main_col` should be in your `colmap`

So for an imaginary cold chain deployment in the US, you might write this

	colmap = [
		{"column": "refrig_count", "display_name": "Number of refrigerators"},
		{"column": "facility_type"},
		{"column": "city", "callback": function(element, columnValue, data) {
			return "Located in <b>" + columnValue + "</b>, <b>" + data.getData(0, "state") + "</b>;
		}];
	]

And the result might look like this:

**Number of refrigerators**: 12<br />
**Facility Type**: Dispensary<br />
Located in **Atlanta**, **Georgia**

If you have an image, audio or video column, with \_contentType and \_uriFragment columns, you can specify the name without the extra \_uriFragment and you'll get a dom element that can be appended to e, or for an image you can get c.src to put it in your own html.

### Menus

In customJs you need to set `menu`. The different types of menus that you can have are listed here
	
	menu = {"label": "Menu Title Here", "type": "menu", "contents": [
			{"label": "Button Text 1", "type": "list_view", "table": "some_table"},
			{"label": "Button Text 2", "type": "group_by", "table": "some_table", "grouping": "some_group_by_column"},
			{"label": "Button Text 3", "type": "collection", "table": "some_table", "column": "some_column", "value": "some_value"},
			{"label": "Button Text 4", "type": "static", "table": "some_table", "query": "SELECT * FROM health_facility WHERE regionLevel2 = ? AND facility_type = ?", "args": ["North", "community_hospital"], "explanation": "Health facilities in the region level 2 ? of the type ?"},
			{"label": "Button Text 5", "type": "js", "function": function() { alert('Some javascript'); }},
			{"label": "Button Text 6", "type": "html", "page": "config/assets/some_page.html" },
			{"type": "group_by", "table": "some_table", "grouping": "some_column"}
		]}
	
 
For example, to make a buttom that opens a list of `health_facilities` where admin_region is Dowa, you would set

	menu = {"label": "Menu Title", type": "menu", "contents": [
		{"label": "Button text", "type": "collection", "table": "health_facility", "column": "admin_region", "value": "Dowa"}
	]}
	
A menu can also have embedded menus using the `menu` type

	menu = {"label": "Main Title", "type": "menu", "contents": [
			// Will display all health facilities
			{"label": "View All Health Facilities", "type": "list_view", "table: "health_facility"],
			// Will group by admin region and display "By Admin Region" for the button's text	
			{"type": "group_by", "table": health_facility", "grouping": "admin_region"},
			{"label": "Launch another page", "type": "html", "page": "assets/config/some_other_page.html"},
			{"label": "This is an embedded menu", "type": "menu", "contents": [
				{"type": "group_by", "table": "health_facility", "grouping": "delivery_type"},
				{"label": "By Reserve Stock Requirement", "type": "group_by", "table": "health_facility", "grouping": "vaccine_reserve_stock_requirement"},
				{"label": "All refrigerators in health facilities in the admin region of Dowa that were installed before 1995", "type": "static", "table": "refrigerators", "query": "SELET * FROM refrigerators JOIN health_facility ON health_facility._id = refrigerators.facility_row_id WHERE health_facility.admin_region = ? AND year < ?", "args": ["Dowa", 1995], "explanation": "refrigerators in health facilities in the admin region ? that were installed before ?"},
			]}
		]}

You also need to set the `list_views` variable to a dictionary. So for the above example,

	list_views = {
		"health_facility": "config/assets/aa_health_facility_list.html",
		"refrigerators": "config/assets/aa_refrigerators_list.html"
	}

If you didn't create a custom list view file, you can leave it blank and it will default to `config/assets/table.html`, just make sure you specified an instance column in your xlsx.

### Tabs

You can make a page that has tabs like this

	helper.make_tabs("index.html", """
		var tabs = [
			{"title": "Some tab name", "file": "first_page.html"},
			{"title": "Tab two", "file": "second_page.html"},
			{"title": "Tab three", "file": "third_page.html"}
		]
	""", "")

An iframe with `src` set to the second element in the pair will take up the rest of the page below the header

Remember that odkData despises iframes with a loathing passion, and your odkData callbacks on these pages will not work. To get data callbacks, you can have your iframe's html set a `window.success` (or a similar name), and add a function to your triplet, like this

	var tabs = [
		{"title": "Some tab name", "file": "first_page.html"},
		{"title": "Tab Two", "page": "second_page.html", "callback": function(iframe) {
			odkData.arbitraryQuery(table, raw_query, args, 10000, 0, iframe.contentWindow.success, function(e) { alert("Error: " + e); });
		}},
	]

### Translations

Most of the above configuration involves setting strings that will be displayed to the user. To have those strings automatically translated to another language, set `helper.translations`. For example

	helper.make_table("aa_health_facility_list.html", "", "", """
		table_id = "health_facility";
		display_col = "facility_name"
		display_subcol = [
			{"column": "facility_id", "display_name": "Facility ID: ", "newline": true},
			{"column": "refrig_count", "display_name": "Refrigerators: ", "newline": true},
		]
	""", "", "")
	
	helper.translations = {
		"Facility ID: ": {"text": {
			"default": True,
			"spanish": "ID de Facilidad: "
		}},
		"Refrigerators: ": {"text": {
			"default": True,
			"spanish": "Frigoríficos: "
		}}
	}

would do exactly what you expect. You can pass in the boolean literal true to avoid duplicating the input string if they are the same

Total list of things translated using these translations:
- The second string in a pair in colmap in a detail view
- Button text in indexes
- The first string in a triplet in display_subcol in a list view
- Strings to be displayed in allowed_group_bys in a list view
- Human readable "what is being selected" explanations in list views opened with the `STATIC` selector, ?s replaced with bindargs of the query.
- Tab titles
- Graph titles
- Graph keys

You can also call the `_tu` function in your custom javascript to retrieve something from helper.translations in the user's currently selected locale


## Using detail, list, index and graph views from your own code

When launching a table view, you should pass your arguments through the hash. At the minimum, it expects to be passed

	#table_id
	
You can technically omit it if you're opening a list view you generated with `helper.make_table`, but you'll still need it for anything more complicated.

To launch a group by, add the column to group on

	#table_id/column_id
	
That will display all the unique values of column_id as if column_id were the `display_col` and `display_subcol` was not set. Clicking a value will open a collection.

To open a collection view, pass in the where clause and argument like one of these

	#table_id/column_id = ?/some_value
	#table_id/column_id IS NULL/null

For anything more complicated, use the `STATIC` method, which looks like this

	#table_id/STATIC/Selection statement/Json encoded bindargs/Translateable text
	#table_id/STATIC/SELECT * FROM refrigerators JOIN health_facility ON health_facility._id = refrigerators.facility_row_id WHERE admin_region = ? AND model_row_id = ?/["Dowa", "M25"]/refrigerators at health facilities in the admin region ? with the model number ?

Everything after that last `/` will be looked up in your user specific translations and displayed to the user as an explanation of what they're viewing

### Graphs

Open a pie chart view like this

	#pie/table_id/[graph_key, graph_val]/select statement/json encoded bindargs/translateable title
	
So for example

	#pie/refrigerators/["normalized_year", "count"]/SELECT (CASE WHEN year < 2007 THEN 'More than 10 years ago' ELSE 'Within the last 10 years' END) AS normalized_year, COUNT(*) AS count FROM refrigerators JOIN health_facility ON health_facility._id = refrigerators.facility_row_id WHERE health_facility.regionLevel2 = ? GROUP BY normalized_year/["North"]/Refrigerator Age
	
<img src="http://i.imgur.com/6LkMYNg.png" height="400px" />

The strings 'More than 10 years ago', 'Within the last 10 years' and 'Refrigerator Age' will all be translated.

In this example

	#pie/refrigerators/["power_source", "count"]/SELECT power_source, COUNT(power_source) AS count FROM refrigerators JOIN health_facility ON health_facility._id = refrigerators.facility_row_id WHERE health_facility.regionLevel2 = ? GROUP BY power_source/["North"]/Refrigerator Power
	
<img src="http://i.imgur.com/QWrn4QV.png" height="400px" />
	
The strings ('electricity', 'solar', 'unknown', etc...) coming out of the database would be translated without the need to add them to user translations. Since we know the table id and column id, they can be pulled from the choices list in the xlsx. However if that fails, user translations will be checked.

Bar graphs, line graphs and scatter plots are the same, just change pie to bar, line or scatter in the url

<img src="http://i.imgur.com/nSgeJmT.png" height="400px" />

Graphs provide a `window.success` for use in iframes

TODO document `show_value`, `sort` and `reverse` and `all_colors`

### Detail views

Expect

	#table_id/row_id

and nothing else.


## Todo list

### Big stuff

- port hope study
- list view generator in app designer
	- global which cols to select
	- callback functions
- detail view generator
- Detail views used to automatically display pictures, now they don't because we loop over the colmap instead of d.getColumns().

### Small stuff

- test special \_finalize label
- test scatterplots
- test inputAttributes.timeFormat
- more testing of user_branch
- more testing of goto to another section
- If the last thing in your initial section (if you provide one) is a 'do section', it will show "next" instead of "finalize" on the last screen in the subsection but it will finalize anyways
	- Temporary workaround is to set default_initial, but I'd like to not do that.
	- There's no way to know if this is the last prompt the user is going to see without evaling all the do_sections that come after the current screen (e.g. soi and smg), potentially going back up the chain as well. May not be a real solution
	- \^ that basically means `WONTFIX`
- Document custom prompt types
- signature (just need to know the name of the activity to start, can scrape it by setting breakpoint in doAction in survey)
- NaN showing for total count in STATIC list views (sometimes)
- read_only_image
	- might be a scan specific thing
- Display sync state and savepoint type in detail views
- Canceling a barcode results in a "Location Providers Are Disabled" message
- for the household survey, deleting the household owner then changing it to someone else will ignore your changes and store the old value in the database because it can't update the screen_data to a now-deleted row id
- css and handling for twoColumn
- make fork that attempts to support custom screen types
	- set showHeader, showFooter false before render
	- fill in all divs with `field-name=":dbcol"`
	- the corresponding element in sections\[section\] for a custom screen will need to be a list of prompts instead of one string
		- may just do that for the entire thing? Will have to make serious changes on the python side, not-so-serious changes on the javascript side
- inputAttributes.timeFormat works for times but not dates
- back button works as implemented, but that's almost never the way you'd expect it to work

Forms I don't support yet and why I don't support them

8 (and a half) forms total

- send_sms
	- send_sms
	- sms_example
- breathcounter
	- breathcounter
	- imgci
	- imgci/imgci\_test
- pulseox
	- imnci
- signature
	- sign
- async assign garbage
	- agriculture
	- visit
