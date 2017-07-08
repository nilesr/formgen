all:
	python3 form_generator.py
deploy: all
	adb shell rm -rf /sdcard/opendatakit/default/config/assets/formgen||:
	adb shell mkdir -p /sdcard/opendatakit/default/config/assets/formgen||:
	find . -maxdepth 1 -mindepth 1 -type d -exec adb push \{\} /sdcard/opendatakit/default/config/assets/formgen/\{\} \;
	make clean
clean:
	find . -maxdepth 1 -mindepth 1 -type d -exec rm -rf \{\} \;
