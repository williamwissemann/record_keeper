
test: venv lint
	. venv/bin/activate; python3 -m pip install -r requirements.txt
	. venv/bin/activate; py.test --cov=source tests --capture=sys -r w --disable-pytest-warnings --cov-fail-under 9 -vv

lint: venv
	. venv/bin/activate; pip install flake8==3.3.0
	. venv/bin/activate; python3.7 -m flake8 \
		--ignore=F401,E266,E501,E731 \
		--exclude .git,__pycache__,venv,old,build,dist \
	    --max-complexity 10

coverage: venv test
	. venv/bin/activate; coverage html
	. venv/bin/activate; open htmlcov/index.html

setup:
	python3 -m pip install virtualenv

venv: setup
	rm -rf venv
	virtualenv -p python3 venv

docker-build:
	docker-compose build 

docker-entry-bash:
	docker run -it record_keeper:discord
