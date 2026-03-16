# check if ruff is installed
lint:
	poetry run ruff check --fix ./ && poetry run ruff format ./


test:
	poetry run pytest