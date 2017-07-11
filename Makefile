appname := $(shell python3 -c "import sys; sys.path.append('.'); import utils; print(utils.appname)")
all:
	adb shell rm -rf /sdcard/opendatakit/$(appname)/config/assets/formgen||:
	python3 form_generator.py # copies things into assets/formgen so we delete assets/formgen up here, not in push_forms
	adb shell mkdir -p /sdcard/opendatakit/$(appname)/config/assets/formgen||:
	find . -maxdepth 1 -mindepth 1 -type d -exec adb push \{\}/index.html /sdcard/opendatakit/$(appname)/config/assets/formgen/\{\}/index.html \;
	python3 generate_table.py # reads the list of folders in config/assets/formgen/ OFF THE DEVICE, so we push forms first
	python3 generate_tables.py
	python3 generate_detail.py
	python3 generate_common.py
	#python3 update_props_csv.py
	python3 custom.py
	find . -maxdepth 1 -mindepth 1 -type f -exec adb push \{\} /sdcard/opendatakit/$(appname)/config/assets/\{\} \;
deploy:
	make all
	make clean
deploy-multiapp:
	echo 'default|development' > .appname-hack
	make deploy
	echo 'coldchain|cold-chain-demo' > .appname-hack
	make deploy
clean:
	find . -maxdepth 1 -mindepth 1 -type d -exec rm -rf \{\} \;
	rm table.html tables.html detail.html formgen_common.js .appname-hack ||:
gitpush:
	./gitpush.sh
