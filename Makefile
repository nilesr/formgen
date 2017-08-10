push := False
appname := fail
all:
	python3 -c "import sys; sys.path.append('.'); import utils; utils.make('$(appname)', $(push))"
	make clean
deploy: push = True
deploy: all
clean:
	rm -rf __pycache__ custom_prompt_types/__pycache__ ||:
.PHONY: coldchain deploy-coldchain default deploy-default deploy-multiapp deploy all clean

coldchain: appname = coldchain
coldchain: all coldchain-cleanup
deploy-coldchain: appname = coldchain
deploy-coldchain: deploy coldchain-cleanup
coldchain-cleanup:
	rm -rf /home/niles/Documents/odk/app-designer/app/config/assets/formgen
	rm /home/niles/Documents/odk/app-designer/app/config/assets/form_generator.js
	rm /home/niles/Documents/odk/app-designer/app/config/assets/form_generator.css
	rm /home/niles/Documents/odk/app-designer/app/config/assets/graph.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/detail.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/table.html
	rm /home/niles/Documents/odk/app-designer/app/config/assets/tables.html

default: appname = default
default: all
deploy-default: appname = default
deploy-default: deploy

example: appname = example
example: all
deploy-example: appname = example
deploy-example: deploy

test:
	python3 tests/run.py