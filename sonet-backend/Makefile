.PHONY: help proto build test docker-build dev

help:
	@echo "Sonet Backend Commands:"
	@echo "  make proto         - Generate protobuf code"
	@echo "  make build         - Build all services"
	@echo "  make test          - Run all tests"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make dev           - Start local environment"

proto:
	./scripts/generate-protos.sh

build:
	cd services/swift && ./build-all.sh
	cd services/rust && cargo build --release --workspace

test:
	cd services/swift && swift test --parallel
	cd services/rust && cargo test --workspace

docker-build:
	./scripts/build-all.sh

dev:
	docker-compose -f infra/docker-compose/docker-compose.yml up
