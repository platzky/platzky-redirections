lint:
	poetry run black .
	poetry run ruff check --fix .

dev: lint
	poetry run pyright .

lint-check:
	poetry run black --check .
	poetry run ruff check .
	poetry run pyright .
	poetry run interrogate platzky_redirections/ --verbose

unit-tests:
	poetry run python -m pytest -v

coverage:
	poetry run coverage run --branch --source=platzky_redirections -m pytest -m "not skip_coverage"
	poetry run coverage report --fail-under=90
	poetry run coverage lcov

html-cov: coverage
	poetry run coverage html

audit:
	poetry run pip-audit

build:
	poetry build
