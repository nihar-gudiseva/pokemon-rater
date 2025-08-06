# Pokemon Rater Makefile
# Use 'make help' to see available commands

.PHONY: help setup build init start stop restart logs clean dev test

# Default target
help: ## Show this help message
	@echo "Pokemon Rater - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup    # First time setup"
	@echo "  make start    # Start the application"

setup: ## Setup environment and initialize database
	@echo "🎮 Setting up Pokemon Rater..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp env.template .env; \
		echo "✅ .env file created! Edit it to customize settings."; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@mkdir -p data
	@echo "🚀 Setup complete! Run 'make start' to begin."

build: ## Build the Docker image
	@echo "🔨 Building Docker image..."
	docker-compose build

init: ## Initialize database with Pokemon data
	@echo "📊 Initializing database..."
	docker-compose --profile init up db-init

start: ## Start the application (initializes database if needed)
	@echo "🚀 Starting Pokemon Rater..."
	@if [ ! -f data/pokemon_rater.db ]; then \
		echo "Database not found, initializing..."; \
		$(MAKE) init; \
	fi
	@echo "Starting application..."
	docker-compose up app

dev: ## Start in development mode with live reload
	@echo "🔧 Starting in development mode..."
	docker-compose up app

stop: ## Stop all containers
	@echo "🛑 Stopping containers..."
	docker-compose down

restart: stop start ## Restart the application

logs: ## Show application logs
	docker-compose logs -f app

clean: ## Clean up containers, volumes, and images
	@echo "🧹 Cleaning up..."
	docker-compose down -v --remove-orphans
	docker-compose down --rmi local
	@if [ -d data ]; then \
		echo "🗑️  Removing data directory..."; \
		rm -rf data; \
	fi

clean-db: ## Clean only the database
	@echo "🗑️  Cleaning database..."
	@if [ -d data ]; then \
		rm -rf data; \
		echo "✅ Database cleaned"; \
	fi

reset: clean-db init ## Reset database with fresh data

test: ## Run a quick test to check if the app is running
	@echo "🧪 Testing application..."
	@curl -s http://localhost:8000 > /dev/null && echo "✅ App is running!" || echo "❌ App is not responding"

status: ## Show container status
	docker-compose ps

shell: ## Open a shell in the running container
	docker-compose exec app /bin/bash

# Manual/non-Docker commands
manual-setup: ## Setup for manual (non-Docker) development
	@echo "🔧 Manual setup..."
	pip install -r requirements.txt
	python scripts/import_csv.py

manual-start: ## Start manually without Docker
	@echo "🚀 Starting manually..."
	python run.py

# Utility commands
check-env: ## Check if .env file exists and show variables
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
		echo "Environment variables:"; \
		grep -v '^#' .env | grep -v '^$$'; \
	else \
		echo "❌ .env file not found. Run 'make setup' first."; \
	fi

ports: ## Show what's running on port 8000
	@echo "Checking port 8000..."
	@netstat -tulpn 2>/dev/null | grep :8000 || echo "Port 8000 is free"

# Development helpers
backup-db: ## Backup the database
	@if [ -f data/pokemon_rater.db ]; then \
		cp data/pokemon_rater.db data/pokemon_rater_backup_$(shell date +%Y%m%d_%H%M%S).db; \
		echo "✅ Database backed up"; \
	else \
		echo "❌ No database found to backup"; \
	fi