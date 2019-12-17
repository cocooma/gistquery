init:
	pip install --upgrade pipenv
	pipenv install --dev

clean:
	rm -rf build
	rm -rf dist
	rm -rf gistquery.egg-info

pytest:
	pipenv run python -m unittest  tests/test_guistquery.py

build: init clean pytest
	pipenv run  -d pyinstaller --onefile  gistquery/gistquery.py

