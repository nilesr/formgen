all:
	python3 form_generator.py
	python3 generate_table.py
deploy: all
	adb shell rm -rf /sdcard/opendatakit/default/config/assets/formgen||:
	adb shell mkdir -p /sdcard/opendatakit/default/config/assets/formgen||:
	find . -maxdepth 1 -mindepth 1 -type d -exec adb push \{\} /sdcard/opendatakit/default/config/assets/formgen/\{\} \;
	find . -maxdepth 1 -mindepth 1 -type f -exec adb push \{\} /sdcard/opendatakit/default/config/assets/\{\} \;
	bash -c 'echo window.location.href = \"/default/config/assets/table.html#Tea_houses\"|xsel -b'
	make clean
clean:
	find . -maxdepth 1 -mindepth 1 -type d -exec rm -rf \{\} \;
