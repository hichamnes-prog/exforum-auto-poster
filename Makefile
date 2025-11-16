.PHONY: help setup dev build up down logs test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	@echo "Setting up ClipKit..."
	@chmod +x scripts/dev-setup.sh
	@./scripts/dev-setup.sh

dev: ## Start all services in development mode
	docker-compose up --build

up: ## Start all services in background
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-worker: ## Show worker logs
	docker-compose logs -f worker

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

test: ## Run tests
	@echo "Testing backend..."
	cd backend && python -m pytest
	@echo "Testing API..."
	@chmod +x scripts/test-api.sh
	@./scripts/test-api.sh

clean: ## Clean up containers and volumes
	docker-compose down -v
	rm -rf backend/storage/*
	rm -rf backend/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

build: ## Build Docker images
	docker-compose build

restart: ## Restart all services
	docker-compose restart

backend-shell: ## Open backend container shell
	docker-compose exec backend /bin/bash

worker-shell: ## Open worker container shell
	docker-compose exec worker /bin/bash

frontend-shell: ## Open frontend container shell
	docker-compose exec frontend /bin/sh

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli
