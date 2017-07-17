push := False
appname := fail
coldchain: appname = coldchain
coldchain: all coldchain-cleanup
deploy-coldchain: appname = coldchain
deploy-coldchain: deploy coldchain-cleanup

default: appname = default
default: all
deploy-default: appname = default
deploy-default: deploy

coldchain-cleanup:
	rm /home/niles/Documents/odk/app-designer/app/config/assets/tables.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/table.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/detail.html
	rm -rf /home/niles/Documents/odk/app-designer/app/config/assets/formgen
deploy: push = True
deploy: all
all:
	python3 -c "import sys; sys.path.append('.'); import utils; utils.make('$(appname)', $(push))"
	make clean
clean:
	rm -rf __pycache__ ||:
.PHONY: coldchain deploy-coldchain default deploy-default deploy-multiapp deploy all clean