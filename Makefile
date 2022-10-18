# GNU Makefile

ifneq (,)
This makefile requires GNU Make.
endif

# COLORS
TERM_TEXT := tput -Txterm
GREEN  := $(shell $(TERM_TEXT) setaf 2)
WHITE  := $(shell $(TERM_TEXT) setaf 7)
YELLOW := $(shell $(TERM_TEXT) setaf 3)
RED := $(shell $(TERM_TEXT) setaf 1)
RESET  := $(shell $(TERM_TEXT) sgr0)
TARGET_MAX_CHAR_NUM := 20
ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

## Docker: List running containers
containers:
	docker-compose ps

## Dashboard: Open in browser
dashboard:
	python3 -m webbrowser -t "http://launchbox.run:8080"

## Docker: Open database shell
database:
	docker-compose exec app /bin/bash -c "python3 -m bin.db"

## Docker: Build container
devbuild:
	docker-compose build

## Docker: Build container (no cache)
devbuild-nocache:
	docker-compose build --no-cache

## Docker: Cleanup containers
docker-cleanup:
	docker-compose down

## Minio: Open dashboard in browser
minio:
	python3 -m webbrowser -t "http://localhost:9001"

## Mkdocs: Setup and run
mkdocs:
	@echo "Initializing Mkdocs..."
	cd docs && test -d venv || echo "⚙️ - Creating virtual environment" && python3 -m venv venv
	@echo "Installing latest version of pip..."
	cd docs && . venv/bin/activate && python3 -m pip install --upgrade pip
	@echo "Installing Mkdocs dependencies..."
	cd docs && . venv/bin/activate && python3 -m pip install -r requirements.txt
	@echo "Serving Mkdocs..."
	cd docs && . venv/bin/activate && mkdocs serve

## Docker: Start containers
start:
	docker-compose up --remove-orphans

## Docker: Open bash shell
shell:
	docker-compose exec app /bin/bash

## Docker: Open bash shell (as root)
shell-root:
	docker-compose exec --user root app /bin/bash

## Makefile: Usage and help text
help:
	@echo ''
	@echo 'Makefile Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}[command]${RESET}'
	@echo ''
	@echo 'Available Commands:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			split(helpMessage, helpParts, ": "); \
			printf "  ${GREEN}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${YELLOW}%s${RESET}: ${WHITE}%s${RESET}\n", helpCommand, helpParts[1], helpParts[2]; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''
.PHONY: help
.DEFAULT_GOAL := help
