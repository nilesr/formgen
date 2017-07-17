push := False
appname := fail
adbranch := fail
coldchain: appname = coldchain
coldchain: adbranch = cold-chain-demo
coldchain: all clean
deploy-coldchain: push = True
deploy-coldchain: coldchain
development: appname = default
development: adbranch = development
development: all clean
deploy-development: push = True
deploy-development: development
deploy-multiapp: deploy-coldchain deploy-development
all:
	python3 -c "import sys; sys.path.append('.'); import utils; utils.make('$(appname)', '$(adbranch)', $(push))"
clean:
	rm -rf __pycache__ ||:
.PHONY: coldchain deploy-coldchain development deploy-development deploy-multiapp all clean