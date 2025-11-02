.PHONY: help build up down logs restart clean migrate shell

help:
	@echo "CrossIt - E-commerce Cross-Listing Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make build    - Build all containers"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make restart  - Restart all services"
	@echo "  make clean    - Remove all containers and volumes"
	@echo "  make migrate  - Run database migrations"
	@echo "  make shell    - Open backend shell"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

migrate:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend /bin/bash

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && pip install -r requirements.txt

