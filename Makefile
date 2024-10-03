THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: help build up start down destroy stop restart import createsuperuser logs ps cli shell
.PHONY: db-shell db-dump restore-db organize-imports mypy lint lint-fix format pretty ok
.PHONY: build-tests tests-up tests-down tests coverage
.PHONY: build-prod prod-up prod-down
help:
	@echo
	@echo "Nginx Logs parser management help"
	@echo "================================="
	@echo "make build"
	@echo "    Build docker environment"
	@echo "make up"
	@echo "    (Re)create containers and run the service in Docker environment"
	@echo "make down"
	@echo "    Stop running service and remove its containers and created networks"
	@echo "make destroy"
	@echo "    Down the service and remove database volume"
	@echo "make stop"
	@echo "    Stop running service"
	@echo "make start"
	@echo "    Start service after stopping in existing containers"
	@echo "make restart"
	@echo "    Restart service"
	@echo "make createsuperuser"
	@echo "    Create Django superuser"
	@echo "make import json_log_file.log"
	@echo "    Import Nginx JSON log file into DB"
	@echo "make logs"
	@echo "    View containers logs"
	@echo "make ps"
	@echo "    View running Docker containers"
	@echo "make cli"
	@echo "    Open system terminal in Django container"
	@echo "make shell"
	@echo "    Open Django interactive shell"
	@echo "make db-shell"
	@echo "    Open psql terminal"
	@echo "make db-dump"
	@echo "    Forward DB dump into standard output"
	@echo "make restore-db <dump_file.sql>"
	@echo "    Restore saved SQL dump back into DB"
	@echo "make mypy"
	@echo "    Python type checking with mypy"
	@echo "make lint"
	@echo "    Check source code style"
	@echo "make lint-fix"
	@echo "    Autofix code style issues"
	@echo "make organize-imports"
	@echo "    Organize Python imports in source files"
	@echo "make format"
	@echo "    Makes autoformatting of source files"
	@echo "make pretty"
	@echo "    Autofix issues, organize imports and autoformat"
	@echo "make ok"
	@echo "    Run Mypy and make pretty"
	@echo
	@echo "==========================="
	@echo "    Testing environment"
	@echo "==========================="
	@echo "make build-tests"
	@echo "    Build Docker testing environment"
	@echo "make tests-up"
	@echo "    (Re)create containers and run testing environment"
	@echo "make tests-down"
	@echo "    Stop testing environment and remove its containers"
	@echo "make tests"
	@echo "    Run tests inside of testing environment"
	@echo "make coverage"
	@echo "    Build coverage report (based on tests)"
	@echo
	@echo "==========================="
	@echo "   Production environment"
	@echo "==========================="
	@echo "make build-prod"
	@echo "    Build production environment"
	@echo "make prod-up"
	@echo "    Run production environment"
	@echo "make prod-down"
	@echo "    Stop production environmetn and delete its containers"
build:
	@docker compose -f ./docker/docker-compose.dev.yml build $(c)
up:
	@docker compose -f docker/docker-compose.dev.yml up -d $(c)
start:
	@docker compose -f docker/docker-compose.dev.yml start $(c)
down:
	@docker compose -f docker/docker-compose.dev.yml down $(c)
destroy:
	@docker compose -f docker/docker-compose.dev.yml down -v $(c)
stop:
	@docker compose -f docker/docker-compose.dev.yml stop $(c)
restart:
	@docker compose -f docker/docker-compose.dev.yml stop $(c)
	@docker compose -f docker/docker-compose.dev.yml up -d $(c)
import:
	@cat $(filter-out $@,$(MAKECMDGOALS)) | docker compose -f docker/docker-compose.dev.yml exec -T web python manage.py import - $(c)
createsuperuser:
	@docker compose -f docker/docker-compose.dev.yml exec dev python manage.py createsuperuser
migrations:
	@docker compose -f docker/docker-compose.dev.yml exec dev python manage.py makemigrations
migrate:
	@docker compose -f docker/docker-compose.dev.yml exec dev python manage.py migrate
logs:
	@docker compose -f docker/docker-compose.dev.yml logs --tail=100 -f $(c)
ps:
	@docker compose -f docker/docker-compose.dev.yml ps
cli:
	@docker compose -f docker/docker-compose.dev.yml exec dev /bin/bash
shell:
	@docker compose -f docker/docker-compose.dev.yml exec dev python manage.py shell
db-shell:
	@docker compose -f docker/docker-compose.dev.yml exec dev-db psql -U nginx_logs_user nginx_logs
db-dump:
	@docker compose exec dev-db pg_dump -U nginx_logs_user nginx_logs
restore-db:
	@cat $(filter-out $@,$(MAKECMDGOALS)) | docker compose -f docker/docker-compose.dev.yml exec -T dev-db psql -U nginx_logs_user nginx_logs $(c)
organize-imports:
	@docker compose -f docker/docker-compose.dev.yml exec dev importanize .
mypy:
	@docker compose -f docker/docker-compose.dev.yml exec dev mypy ./app
lint:
	@docker compose -f docker/docker-compose.dev.yml exec dev ruff check
lint-fix:
	@docker compose -f docker/docker-compose.dev.yml exec dev ruff check --fix
format:
	@docker compose -f docker/docker-compose.dev.yml exec dev ruff format
pretty: lint-fix organize-imports format
ok:
	@make mypy && make pretty

build-tests:
	@docker compose -f docker/docker-compose.tests.yml build $(c)
tests-up:
	@docker compose -f docker/docker-compose.tests.yml up -d $(c)
tests-down:
	@docker compose -f docker/docker-compose.tests.yml down -v $(c)
tests:
	@docker compose -f docker/docker-compose.tests.yml exec tests pytest --capture=sys -vv ./tests
coverage:
	@docker compose -f docker/docker-compose.dev.yml exec tests pytest --no-cov-on-fail --cov-reset --cov-branch --cov-report=term:skip-covered --cov-config=./tests/.coveragerc --cov=./app ./tests

build-prod:
	@docker compose -f docker/prod/docker-compose.yml build
prod-up:
	@docker compose -f docker/prod/docker-compose.yml up -d
prod-down:
	@docker compose -f docker/prod/docker-compose.yml down
prod-ps:
	@docker compose -f docker/prod/docker-compose.yml ps
prod-logs:
	@docker compose -f docker/prod/docker-compose.yml logs -f