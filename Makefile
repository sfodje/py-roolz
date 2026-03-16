# check if ruff is installed
lint:
	poetry run ruff check --fix --select I ./ && poetry run ruff format ./

# run benchmark tests
benchmark:
	poetry run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-sort=mean

# run all tests including benchmarks
test:
	poetry run pytest tests/ --benchmark-skip