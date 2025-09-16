# Makefile for Java Notebook development

.PHONY: help install install-dev dev test test-unit test-integration coverage lint format typecheck check clean build upload

# Default target
help:
	@echo "Java Notebook Development Commands"
	@echo "=================================="
	@echo "install          Install production dependencies"
	@echo "install-dev      Install development dependencies + pre-commit hooks"
	@echo "dev              Start development server"
	@echo "test             Run all tests"
	@echo "test-unit        Run unit tests only"
	@echo "test-integration Run integration tests only"
	@echo "coverage         Run tests with coverage report"
	@echo "lint             Run linting (flake8)"
	@echo "format           Format code (black + isort)"
	@echo "typecheck        Run type checking (mypy)"
	@echo "check            Run all quality checks (lint + typecheck + test)"
	@echo "pre-commit       Run pre-commit hooks manually"
	@echo "clean            Clean build artifacts"
	@echo "build            Build package"
	@echo "upload           Upload to PyPI (requires credentials)"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Development server
dev:
	python -m javanotebook examples/basic_java.md --debug

dev-port:
	python -m javanotebook examples/basic_java.md --port 8080 --debug

# Testing
test:
	pytest

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

coverage:
	pytest --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/

format:
	black src/
	isort src/

typecheck:
	mypy src/

check: lint typecheck test

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

# Development utilities
example-basic:
	python -m javanotebook examples/basic_java.md

example-algorithms:
	python -m javanotebook examples/algorithms.md

example-data-structures:
	python -m javanotebook examples/data_structures.md

# Quick development setup
setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"

# Verify Java installation
check-java:
	@echo "Checking Java installation..."
	@java -version
	@javac -version
	@echo "Java is properly installed!"

# Run with different examples
demo: check-java
	@echo "Starting Java Notebook demo..."
	python -m javanotebook examples/basic_java.md --no-browser