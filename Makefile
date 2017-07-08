all:
	python3 form_generator.py
	python3 generate_table.py
	python3 generate_tables.py
deploy:
	adb shell rm -rf /sdcard/opendatakit/default/config/assets/formgen||:
	adb shell mkdir -p /sdcard/opendatakit/default/config/assets/formgen||:
	make all
	find . -maxdepth 1 -mindepth 1 -type d -exec adb push \{\}/index.html /sdcard/opendatakit/default/config/assets/formgen/\{\}/index.html \;
	find . -maxdepth 1 -mindepth 1 -type f -exec adb push \{\} /sdcard/opendatakit/default/config/assets/\{\} \;
	bash -c 'echo window.location.href = \"/default/config/assets/tables.html\"|xsel -b'
	make clean
clean:
	find . -maxdepth 1 -mindepth 1 -type d -exec rm -rf \{\} \;
	rm table.html tables.html ||:
