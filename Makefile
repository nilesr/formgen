push := False
appname := fail
all:
	python3 -c "import sys; sys.path.append('.'); import utils; utils.make('$(appname)', $(push))"
	make clean
deploy: push = True
deploy: all
clean:
	rm -rf __pycache__ ||:
.PHONY: coldchain deploy-coldchain default deploy-default deploy-multiapp deploy all clean

coldchain: appname = coldchain
coldchain: all
deploy-coldchain: appname = coldchain
deploy-coldchain: deploy

default: appname = default
default: all
deploy-default: appname = default
deploy-default: deploy

