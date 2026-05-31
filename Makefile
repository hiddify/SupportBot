.ONESHELL:
UV ?= uv
ENV_PREFIX=$(shell $(UV) run python -c "print('')" 2>/dev/null && echo "$(UV) run ")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@$(UV) python list 2>/dev/null || true
	@$(UV) run python -V
	@$(UV) run python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	$(UV) sync

.PHONY: fmt
fmt:              ## Format code using black & isort.
	$(UV) run isort hiddify_support_bot/
	$(UV) run black -l 79 hiddify_support_bot/
	$(UV) run black -l 79 tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	$(UV) run flake8 hiddify_support_bot/
	$(UV) run black -l 79 --check hiddify_support_bot/
	$(UV) run black -l 79 --check tests/
	$(UV) run mypy --ignore-missing-imports hiddify_support_bot/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	$(UV) run pytest -v --cov-config .coveragerc --cov=hiddify_support_bot -l --tb=short --maxfail=1 tests/
	$(UV) run coverage xml
	$(UV) run coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr $(UV) run pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: virtualenv
virtualenv: install ## Create/sync the uv virtual environment.

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "$${TAG}" > hiddify_support_bot/VERSION
	@$(UV) run gitchangelog > HISTORY.md
	@git add hiddify_support_bot/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(UV) run mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL || open $$URL

.PHONY: init
init:             ## Initialize the project based on an application template.
	@./.github/init.sh
