.PHONY: help install train api docker-build docker-up docker-down test clean format lint check

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies with Poetry"
	@echo "  train        Train the model"
	@echo "  api          Start the API server"
	@echo "  docker-build Build Docker images"
	@echo "  docker-up    Start all services with Docker"
	@echo "  docker-down  Stop all services with Docker"
	@echo "  test         Run tests"
	@echo "  format       Format code with black"
	@echo "  lint         Run linting"
	@echo "  clean        Clean up generated files"

install:
	poetry install

train:
	poetry run python scripts/run_training.py

api:
	poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-down:
	docker-compose down

test:
	poetry run pytest tests/

format:
	poetry run black src/ scripts/ tests/

lint:
	poetry run flake8 src/ scripts/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf dist/
	rm -rf *.egg-info