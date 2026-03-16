# check if ruff is installed
lint:
	poetry run ruff check --fix --select I ./ && poetry run ruff format ./


test:
	poetry run pytest