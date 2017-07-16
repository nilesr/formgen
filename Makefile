push := False
appname := fail
adbranch := fail
coldchain: appname = coldchain
coldchain: adbranch = cold-chain-demo
coldchain: all
deploy-coldchain: push = True
deploy-coldchain: coldchain clean
development: appname = default
development: adbranch = development
development: all
deploy-development: push = True
deploy-development: development clean
deploy-multiapp: deploy-coldchain deploy-development
all:
	python3 -c "import sys; sys.path.append('.'); import utils; utils.make('$(appname)', '$(adbranch)', $(push))"
clean:
	rm -rf __pycache__ ||:
.PHONY: coldchain deploy-coldchain development deploy-development deploy-multiapp all clean