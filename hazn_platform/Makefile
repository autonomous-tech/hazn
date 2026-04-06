.PHONY: up down seed reset-db vault-init vault-policies test logs migrate build ps manage

COMPOSE_FILE := docker-compose.local.yml

## Start all services and initialize Vault
up:
	docker compose -f $(COMPOSE_FILE) up -d --remove-orphans
	@echo "Waiting for services to be healthy..."
	@sleep 10
	$(MAKE) vault-init

## Stop all services
down:
	docker compose -f $(COMPOSE_FILE) down

## Build all Docker images
build:
	docker compose -f $(COMPOSE_FILE) build

## Run seed data command (creates test agency, end-clients, etc.)
seed:
	docker compose -f $(COMPOSE_FILE) run --rm django python manage.py seed_dev_data

## Destroy volumes and rebuild from scratch
reset-db:
	docker compose -f $(COMPOSE_FILE) down -v
	docker compose -f $(COMPOSE_FILE) up -d --remove-orphans
	@echo "Waiting for services to be healthy..."
	@sleep 10
	$(MAKE) vault-init
	$(MAKE) migrate
	$(MAKE) seed

## Initialize and unseal Vault
vault-init:
	@bash scripts/vault-init.sh

## Apply Vault policies from HCL files (requires .vault-keys with ROOT_TOKEN)
vault-policies:
	@bash -c 'source .vault-keys && \
	for policy in django orchestrator mcp; do \
		CONTENT=$$(cat vault/policies/$$policy.hcl); \
		curl -sf -X PUT "$${VAULT_ADDR:-http://127.0.0.1:8200}/v1/sys/policy/hazn-$$policy" \
			-H "X-Vault-Token: $${ROOT_TOKEN}" \
			-H "Content-Type: application/json" \
			-d "{\"policy\": $$(echo "$$CONTENT" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")}"; \
		echo "Applied policy: hazn-$$policy"; \
	done'

## Run pytest inside Django container
test:
	docker compose -f $(COMPOSE_FILE) run --rm django pytest

## Follow logs for all services
logs:
	docker compose -f $(COMPOSE_FILE) logs -f

## Run Django migrations
migrate:
	docker compose -f $(COMPOSE_FILE) run --rm django python manage.py migrate

## Run any Django management command: make manage cmd="createsuperuser"
manage:
	docker compose -f $(COMPOSE_FILE) run --rm django python manage.py $(cmd)

## Show running services
ps:
	docker compose -f $(COMPOSE_FILE) ps
