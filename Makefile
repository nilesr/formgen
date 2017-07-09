all:
	adb shell rm -rf /sdcard/opendatakit/default/config/assets/formgen||:
	python3 form_generator.py # copies things into assets/formgen so we delete assets/formgen up here, not in push_forms
	make push_forms
	python3 generate_table.py # reads the list of folders in config/assets/formgen/ OFF THE DEVICE, so we push forms first
	python3 generate_tables.py
	python3 update_props_csv.py
	make push_files
push_forms:
	adb shell mkdir -p /sdcard/opendatakit/default/config/assets/formgen||:
	find . -maxdepth 1 -mindepth 1 -type d -exec adb push \{\}/index.html /sdcard/opendatakit/default/config/assets/formgen/\{\}/index.html \;
push_files:
	find . -maxdepth 1 -mindepth 1 -type f -exec adb push \{\} /sdcard/opendatakit/default/config/assets/\{\} \;
deploy: all
	bash -c 'echo odkTables.launchHTML\(null, \"config/assets/tables.html\"\)|xsel -b'
	make clean
clean:
	find . -maxdepth 1 -mindepth 1 -type d -exec rm -rf \{\} \;
	rm table.html tables.html ||:
gitpush:
	./gitpush.sh
