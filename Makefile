push := False
appname := fail
adbranch := fail
push: push = True
coldchain: appname = coldchain
coldchain: adbranch = cold-chain-demo
coldchain: all
deploy-coldchain: push coldchain clean
development: appname = default
development: adbranch = development
development: all
deploy-development: push development clean
deploy-multiapp: deploy-coldchain deploy-development
all:
	python3 -c "import sys; sys.path.append('.'); import utils; utils.make('$(appname)', '$(adbranch)', $(push))"
clean:
	rm -rf __pycache__ ||:
gitpush:
	./gitpush.sh
