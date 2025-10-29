.PHONY: help proto build test docker-build dev

help:
	@echo "Dahlia Backend Commands:"
	@echo "  make proto         - Generate protobuf code"
	@echo "  make build         - Build all services"
	@echo "  make test          - Run all tests"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make dev           - Start local environment"

proto:
	./scripts/generate-protos.sh

build:
	cd services/kotlin && ./gradlew build
	cd services/python && pip install -r requirements.txt

test:
	cd services/kotlin && ./gradlew test
	cd services/python && pytest

docker-build:
	./scripts/build-all.sh

dev:
	docker-compose -f infra/docker-compose/docker-compose.yml up
