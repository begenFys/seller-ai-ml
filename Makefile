# Build configuration
# -------------------

PROJECT_NAME := seller-ai-rag-agent
PROJECT_VERSION := 0.1.0
DOCKER_USERNAME := begenfys
GIT_REVISION = `git rev-parse HEAD`
PROD_SERVER_SSH := seller-ai
STU_SERVER_SSH := pushok-stu
BASE_DIR = seller-ai

# Introspection targets
# ---------------------

.PHONY: help
help: header targets

.PHONY: header
header:
	@echo "\033[34mEnvironment\033[0m"
	@echo "\033[34m---------------------------------------------------------------\033[0m"
	@printf "\033[33m%-23s\033[0m" "PROJECT_NAME"
	@printf "\033[35m%s\033[0m" $(PROJECT_NAME)
	@echo ""
	@printf "\033[33m%-23s\033[0m" "PROJECT_VERSION"
	@printf "\033[35m%s\033[0m" $(PROJECT_VERSION)
	@echo ""
	@printf "\033[33m%-23s\033[0m" "GIT_REVISION"
	@printf "\033[35m%s\033[0m" $(GIT_REVISION)
	@echo "\n"

.PHONY: targets
targets:
	@echo "\033[34mDevelopment Targets\033[0m"
	@echo "\033[34m---------------------------------------------------------------\033[0m"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# Deployment targets
# -------------
.PHONY: deploy-configs
deploy-configs:  ## Deploy configs
	scp ./Makefile ./.env ./docker-compose.yaml $(PROD_SERVER_SSH):/$(BASE_DIR)/$(PROJECT_NAME)

.PHONY: deploy-start
deploy-start:  ## Start production
	ssh -o StrictHostKeyChecking=no $(PROD_SERVER_SSH) "cd /$(BASE_DIR)/$(PROJECT_NAME) && make dc-start-prod"

.PHONY: deploy
deploy: deploy-configs deploy-start  ## Deploy and start on production

.PHONY: deploy-configs-stu
deploy-configs-stu:  ## Deploy configs on stu
	scp ./Makefile ./docker-compose.test.yaml $(STU_SERVER_SSH):/$(BASE_DIR)/$(PROJECT_NAME)
	scp ./.env.stu $(STU_SERVER_SSH):/$(BASE_DIR)/$(PROJECT_NAME)/.env.test

.PHONY: deploy-start-stu
deploy-start-stu:  ## Start stu
	ssh -o StrictHostKeyChecking=no $(STU_SERVER_SSH) "cd /$(BASE_DIR)/$(PROJECT_NAME) && make dc-start-stu"

.PHONY: deploy-stu
deploy-stu: deploy-configs-stu deploy-start-stu  ## Deploy and start on stu

# Development targets
# -------------

.PHONY: sync
sync: ## Install dependencies
	uv sync

.PHONY: start
start: ## Starts the server
	set -a && . ./.env.dev && set +a && uv run -m src

.PHONY: start-broker
start-broker: ## Starts the broker
	set -a && . ./.env.dev && set +a && faststream run src.core.faststream.base:APP_BROKER

.PHONY: migrate
migrate:  ## Run the migrations
	set -a && . ./.env.dev && set +a && alembic upgrade head

.PHONY: rollback
rollback: ## Rollback migrations one level
	set -a && . ./.env.dev && set +a && alembic downgrade -1

.PHONY: reset-database
reset-database: ## Rollback all migrations
	set -a && . ./.env.dev && set +a && alembic downgrade base

.PHONY: generate-migration
generate-migration: ## Generate a new migration
	@read -p "Enter migration message: " message; \
	set -a && . ./.env.dev && set +a && alembic revision --autogenerate -m "$$message"

# Check, lint and format targets
# ------------------------------
.PHONY: lint
lint: ## Run linter
	uv run ruff check

.PHONY: format
format: ## Run code formatter
	uv run ruff format
	uv run ruff check --fix

.PHONE: check-types
check-types: ## Check types
	uv run mypy src --install-types

.PHONE: setup-precommit
setup-precommit: ## Install all hooks
	uv run pre-commit install

.PHONE: check-precommit
check-precommit: ## Check
	uv run pre-commit run --all-files

# Docker and Docker-compose
# -------------
docker-setup-prod: ## Create all needs production docker stuff
	docker network ls | grep -q seller-net || docker network create seller-net
	docker volume ls | grep -q seller-ai-qdrant-storage || docker volume create seller-ai-qdrant-storage

docker-setup-test: ## Create all needs test docker stuff
	docker network ls | grep -q seller-test || docker network create seller-test
	docker volume ls | grep -q seller-ai-qdrant-storage || docker volume create seller-ai-qdrant-storage

docker-build-prod: ## Build prod image
	docker build -t $(DOCKER_USERNAME)/$(PROJECT_NAME):latest -t $(DOCKER_USERNAME)/$(PROJECT_NAME):$(PROJECT_VERSION) .

docker-build-test: ## Build test image
	docker build -t $(DOCKER_USERNAME)/$(PROJECT_NAME):test -t $(DOCKER_USERNAME)/$(PROJECT_NAME):$(PROJECT_VERSION)-test .

docker-buildx-prod: ## Build (buildx multi-platform) prod image
	docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_USERNAME)/$(PROJECT_NAME):latest -t $(DOCKER_USERNAME)/$(PROJECT_NAME):$(PROJECT_VERSION) --no-cache .

docker-buildx-test: ## Build (buildx multi-platform) test image
	docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_USERNAME)/$(PROJECT_NAME):test -t $(DOCKER_USERNAME)/$(PROJECT_NAME):$(PROJECT_VERSION)-test --no-cache .

docker-buildx-and-push-prod: ## Build (buildx) and push prod image
	docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_USERNAME)/$(PROJECT_NAME):latest -t $(DOCKER_USERNAME)/$(PROJECT_NAME):$(PROJECT_VERSION) --no-cache --push .

docker-buildx-and-push-test: ## Build (buildx) and push test image
	docker buildx build --platform linux/amd64,linux/arm64 -t $(DOCKER_USERNAME)/$(PROJECT_NAME):test -t $(DOCKER_USERNAME)/$(PROJECT_NAME):$(PROJECT_VERSION)-test --no-cache --push .

dc-pull-prod: ## Pull actual images
	set -a && . ./.env.prod && set +a && docker compose pull

dc-pull-test: ## Pull actual images
	set -a && . ./.env.test && set +a && docker compose -f ./docker-compose.test.yaml pull

dc-down-prod: ## Down prod docker-compose
	set -a && . ./.env.prod && set +a && docker compose down

dc-down-test: ## Down test docker-compose
	set -a && . ./.env.test && set +a && docker compose -f ./docker-compose.test.yaml down

dc-up-prod: ## Start prod docker-compose
	set -a && . ./.env.prod && set +a && docker compose up -d

dc-up-test: ## Start test docker-compose
	set -a && . ./.env.test && set +a && docker compose -f ./docker-compose.test.yaml up -d

dc-start-prod: ## Start prod docker-compose
	make docker-setup-prod && \
	make dc-pull-prod && \
	make dc-down-prod && \
	make dc-up-prod

dc-start-test: ## Start test docker-compose
	make docker-setup-test && \
	make docker-build-test && \
	make dc-down-test && \
	make dc-up-test

dc-start-stu: ## Start test docker-compose for stu
	make docker-setup-test && \
	make dc-pull-test && \
	make dc-down-test && \
	make dc-up-test

dc-rm-test:
	docker compose -f ./docker-compose.test.yaml rm -s -v -f
