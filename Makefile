# This makefile has been created to help developers perform common actions.
# Most actions assume it is operating in a virtual environment where the
# python command links to the appropriate virtual environment Python.

MAKEFLAGS += --no-print-directory

PYTHON=python3.8

# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.    
# help:                                                                                             
# help: record_keeper help
# help:

# help: help                           - display this makefile's help information
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: venv                           - create a virtual environment for development
venv:
	@$(PYTHON) -m venv venv
	@/bin/bash -c "source venv/bin/activate && pip install pip --upgrade && pip install -r requirements.dev.txt && pip install -e ."
	@echo "\nEnter virtual environment using: \n\t$ source venv/bin/activate\n"

# help: clean                          - clean up the venv and python cache files
.PHONY: clean
clean:
	@rm -rf venv
	@rm -rf .coverage
	@rm -rf src/*.egg-info
	@rm -rf htmlcov
	@rm -rf docs/_build/
	@rm -rf docs/build/
	@rm -rf docs/source/api/
	@rm -rf .pytest_cache
	@find . -type f -name '*.pyc' -delete
	@find . -empty -type d -delete
	@echo "\nClean up based on .gitignore rules:\n"
	@git clean -X -f -d -n
	@echo "\n[OPTIONAL] Use 'git clean -X -f -d' to remove them \n"

	
# help: test                           - run tests
.PHONY: test 
test: venv 
	@. venv/bin/activate; pytest \
		--cov=src \
		--cov-report html \
		--cov-report term \
		tests \
		-r w \
		--cov-fail-under 0
	@. venv/bin/activate; coverage-badge -f -o coverage.svg

# help: test-verbose                   - run tests [verbosely]
.PHONY: test-verbose
test-verbose:
	@. venv/bin/activate; pytest \
		--cov=src \
		--cov-report html \
		--cov-report term \
		tests \
		-r w \
		--cov-fail-under 0 \
		-vvs
	@. venv/bin/activate; coverage-badge -f -o coverage.svg

# help: coverage                       - perform test coverage checks
.PHONY: coverage
coverage:
	@. venv/bin/activate; coverage erase
	@. venv/bin/activate; PYTHONPATH=src coverage run -m unittest discover -s tests -v
	@. venv/bin/activate; coverage html
	@. venv/bin/activate; coverage report

# help: format                         - perform code style format
.PHONY: format
format:
	@. venv/bin/activate; black src/record_keeper tests examples


# help: check-format                   - check code format compliance
.PHONY: check-format
check-format:
	@. venv/bin/activate; black --check src/record_keeper tests examples


# help: sort-imports                   - apply import sort ordering
.PHONY: sort-imports
sort-imports:
	@. venv/bin/activate; isort . --profile black


# help: check-sort-imports             - check imports are sorted
.PHONY: check-sort-imports
check-sort-imports:
	@. venv/bin/activate; isort . --check-only --profile black


# help: style                          - perform code style format
.PHONY: style
style: sort-imports format


# help: check-style                    - check code style compliance
.PHONY: check-style
check-style: check-sort-imports check-format


# help: check-types                    - check type hint annotations
.PHONY: check-types
check-types:
	@. venv/bin/activate; cd src; mypy -p record_keeper --ignore-missing-imports


# help: check-lint                     - run static analysis checks
.PHONY: check-lint
check-lint:
	. venv/bin/activate; $(PYTHON) -m flake8 src/


# help: check-static-analysis          - check code style compliance
.PHONY: check-static-analysis
check-static-analysis: check-lint check-types


# help: docs                           - generate project documentation
.PHONY: docs
docs: coverage
	@. venv/bin/activate; cd docs; rm -rf source/api/record_keeper*.rst source/api/modules.rst build/*
	@. venv/bin/activate; cd docs; make html


# help: check-docs                     - quick check docs consistency
.PHONY: check-docs
check-docs:
	@. venv/bin/activate; cd docs; make dummy


# help: serve-docs                     - serve project html documentation
.PHONY: serve-docs
serve-docs:
	@. venv/bin/activate; cd docs/build; python -m http.server --bind 127.0.0.1


# help: dist                           - create a wheel distribution package
.PHONY: dist
dist:
	@python setup.py bdist_wheel

# help: dist-upload                    - upload a wheel distribution package
.PHONY: dist-upload
dist-upload:
	@twine upload dist/record_keeper-*-py3-none-any.whl


# Keep these lines at the end of the file to retain nice help
# output formatting.
# help:
