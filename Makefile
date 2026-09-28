.PHONY: help install test lint run pipeline up down clean seed

help:
	@echo "Available commands:"
	@echo "  make install    - Install Python dependencies in virtualenv"
	@echo "  make run        - Run local FastAPI server with Uvicorn"
	@echo "  make pipeline   - Ingest all retail and banking sample datasets"
	@echo "  make test       - Execute pytest test suite with coverage report"
	@echo "  make seed       - Generate fresh sample CSV, JSON, and Excel files"
	@echo "  make up         - Start complete Docker Compose stack (FastAPI + Postgres + ETL)"
	@echo "  make down       - Stop Docker Compose stack"
	@echo "  make clean      - Clean temporary files, caches, and test artifacts"

install:
	pip install -r requirements.txt

run:
	python -m app.cli start-server --reload

pipeline:
	python -m app.cli run-all-samples

test:
	python -m pytest --cov=app --cov-report=term-missing

seed:
	python sample_data/generator.py

up:
	docker compose up --build -d

down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
