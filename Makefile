# Mekaneck Makefile
# Comprehensive build and development automation

.PHONY: help install install-dev clean test validate build-rust build-docker run-docker \
        run-validation lint format docs check pre-commit all

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================

help: ## Show this help message
	@echo "Mekaneck - Pharmaceutical Maxwell Demon Framework"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Installation
# ============================================================================

install: ## Install Python dependencies
	@echo "Installing Python dependencies..."
	pip install -r blindhorse/requirements.txt
	@echo "✓ Python dependencies installed"

install-dev: install ## Install development dependencies
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt
	@echo "✓ Development dependencies installed"

# ============================================================================
# Cleaning
# ============================================================================

clean: ## Clean build artifacts and caches
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/
	rm -rf target/
	rm -rf results/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	@echo "✓ Cleaned"

clean-results: ## Clean validation results only
	@echo "Cleaning validation results..."
	rm -rf results/
	@echo "✓ Results cleaned"

# ============================================================================
# Testing and Validation
# ============================================================================

test: ## Run Python tests
	@echo "Running tests..."
	pytest tests/ -v --cov=blindhorse --cov-report=html --cov-report=term
	@echo "✓ Tests completed"

validate: ## Run complete validation suite
	@echo "Running Pharmaceutical Maxwell Demon validation suite..."
	python blindhorse/run_validation.py
	@echo "✓ Validation completed"

validate-fast: ## Run fast validation (skip slow validators)
	@echo "Running fast validation..."
	python blindhorse/run_validation.py --fast
	@echo "✓ Fast validation completed"

validate-no-viz: ## Run validation without visualizations
	@echo "Running validation without visualizations..."
	python blindhorse/run_validation.py --no-viz
	@echo "✓ Validation completed (no visualizations)"

# ============================================================================
# Rust Build
# ============================================================================

build-rust: ## Build Rust project (release)
	@echo "Building Rust project..."
	cargo build --release
	@echo "✓ Rust build completed"

build-rust-dev: ## Build Rust project (debug)
	@echo "Building Rust project (debug)..."
	cargo build
	@echo "✓ Rust debug build completed"

test-rust: ## Run Rust tests
	@echo "Running Rust tests..."
	cargo test
	@echo "✓ Rust tests completed"

# ============================================================================
# Docker
# ============================================================================

build-docker: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t mekaneck:latest .
	@echo "✓ Docker image built"

run-docker: build-docker ## Run validation in Docker
	@echo "Running validation in Docker..."
	docker run --rm -v $(PWD)/results:/app/results mekaneck:latest
	@echo "✓ Docker validation completed"

docker-compose-up: ## Start all services with docker-compose
	@echo "Starting services..."
	docker-compose up -d
	@echo "✓ Services started"

docker-compose-down: ## Stop all services
	@echo "Stopping services..."
	docker-compose down
	@echo "✓ Services stopped"

docker-shell: ## Open shell in Docker container
	@echo "Opening Docker shell..."
	docker run -it --rm -v $(PWD)/results:/app/results mekaneck:latest bash

# ============================================================================
# Code Quality
# ============================================================================

lint: ## Run linters (flake8, mypy)
	@echo "Running linters..."
	flake8 blindhorse/ --max-line-length=120 --ignore=E203,W503
	mypy blindhorse/ --ignore-missing-imports
	@echo "✓ Linting completed"

format: ## Format code (black, isort)
	@echo "Formatting code..."
	black blindhorse/ --line-length=120
	isort blindhorse/ --profile black
	@echo "✓ Code formatted"

format-check: ## Check code formatting without modifying
	@echo "Checking code formatting..."
	black blindhorse/ --check --line-length=120
	isort blindhorse/ --check-only --profile black
	@echo "✓ Format check completed"

# ============================================================================
# Documentation
# ============================================================================

docs: ## Build documentation
	@echo "Building documentation..."
	cd docs && pdflatex mekaneck/docs/pharmaceutical-maxwell-demon/pharmaceutical-maxwell-demon.tex
	@echo "✓ Documentation built"

docs-open: docs ## Build and open documentation
	@echo "Opening documentation..."
	open docs/pharmaceutical-maxwell-demon.pdf || xdg-open docs/pharmaceutical-maxwell-demon.pdf

# ============================================================================
# Pre-commit and CI
# ============================================================================

check: lint format-check test ## Run all checks (lint, format, test)
	@echo "✓ All checks passed"

pre-commit: format lint test ## Run pre-commit checks
	@echo "✓ Pre-commit checks passed"

ci: clean install check validate ## Run full CI pipeline
	@echo "✓ CI pipeline completed"

# ============================================================================
# Development Workflow
# ============================================================================

dev-setup: install-dev ## Setup development environment
	@echo "Setting up development environment..."
	pre-commit install
	@echo "✓ Development environment ready"

run-validator: ## Run specific validator (use VAL=<name>)
	@echo "Running validator: $(VAL)"
	python -c "from blindhorse.validators import $(VAL)Validator; $(VAL)Validator().run_validation()"

# Examples:
# make run-validator VAL=HardwareOscillation
# make run-validator VAL=HarmonicNetwork

# ============================================================================
# Comprehensive Targets
# ============================================================================

all: clean install build-rust validate ## Clean, install, build, and validate everything
	@echo "✓ All tasks completed"

release: clean install build-rust validate build-docker ## Prepare release (build everything)
	@echo "✓ Release ready"

# ============================================================================
# Info
# ============================================================================

info: ## Show project information
	@echo "Mekaneck - Pharmaceutical Maxwell Demon Framework"
	@echo "================================================="
	@echo "Version: 0.1.0"
	@echo "Python: $(shell python --version)"
	@echo "Rust: $(shell rustc --version)"
	@echo "Docker: $(shell docker --version)"
	@echo ""
	@echo "Project structure:"
	@echo "  - blindhorse/: Python validation package"
	@echo "  - mekaneck/: Rust implementation (coming)"
	@echo "  - docs/: Theoretical documentation"
	@echo ""
	@echo "Quick start:"
	@echo "  make install      # Install dependencies"
	@echo "  make validate     # Run validation suite"
	@echo "  make help         # Show all commands"

