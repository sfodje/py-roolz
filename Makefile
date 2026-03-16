# check if uv is installed, install if not
ensure-uv:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo 'uv not found, installing with pipx...'; \
		pipx install uv; \
	fi

# check if ruff is installed
lint: ensure-uv
	uv run ruff check --fix --select I ./ && uv run ruff format ./

# run benchmark tests
benchmark: ensure-uv
	uv run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-sort=mean

# run all tests including benchmarks
test: ensure-uv
	uv run pytest -n auto tests/ --benchmark-skip