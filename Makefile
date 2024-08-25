# check if ruff is installed
lint:
	@which ruff || (pip install ruff && echo "ruff installed")
	ruff check --fix ./ && ruff format ./