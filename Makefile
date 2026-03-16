.PHONY: help install install-dev lint lint-fix type-check format format-check test test-coverage clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install all dependencies including dev tools"
	@echo "  make lint          - Run linter (ruff) to check code quality"
	@echo "  make lint-fix      - Run linter and automatically fix issues"
	@echo "  make type-check    - Run type checker (mypy)"
	@echo "  make format        - Format code and organize imports (ruff)"
	@echo "  make format-check  - Check if code is formatted (CI-friendly)"
	@echo "  make test          - Run tests with pytest"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make check         - Run lint, type-check, format-check, and test"
	@echo "  make clean         - Remove cache files and build artifacts"

# Installation
install:
	uv sync --no-dev

install-dev:
	uv sync

# Linting
lint:
	uv run ruff check roolz tests

lint-fix:
	uv run ruff check --fix roolz tests

# Type checking
type-check:
	uv run mypy roolz

# Formatting
format:
	uv run ruff format roolz tests
	uv run ruff check --fix --select I roolz tests

format-check:
	uv run ruff format --check roolz tests
	uv run ruff check --select I roolz tests

# Testing
test:
	uv run pytest

test-coverage:
	uv run pytest --cov=roolz --cov-report=term-missing --cov-report=html

# Combined checks (useful for CI)
check: lint type-check format-check test
	@echo "All checks passed!"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf htmlcov .coverage coverage.xml 2>/dev/null || true

# run benchmark tests
benchmark:
	uv run pytest tests/benchmark_test_*.py --benchmark-only --benchmark-sort=mean
