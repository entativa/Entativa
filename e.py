#!/usr/bin/env python3

import os
import sys

PROJECT_NAME = "sonet-backend"

MAKEFILE = """
.PHONY: help proto build test docker-build dev

help:
\t@echo "Sonet Backend Commands:"
\t@echo "  make proto         - Generate protobuf code"
\t@echo "  make build         - Build all services"
\t@echo "  make test          - Run all tests"
\t@echo "  make docker-build  - Build Docker images"
\t@echo "  make dev           - Start local environment"

proto:
\t./scripts/generate-protos.sh

build:
\tcd services/swift && ./build-all.sh
\tcd services/rust && cargo build --release --workspace

test:
\tcd services/swift && swift test --parallel
\tcd services/rust && cargo test --workspace

docker-build:
\t./scripts/build-all.sh

dev:
\tdocker-compose -f infra/docker-compose/docker-compose.yml up
"""

DOCKER_COMPOSE = """version: '3.8'

services:
  scylla:
    image: scylladb/scylla:5.2
    ports:
      - "9042:9042"
    volumes:
      - scylla-data:/var/lib/scylla

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sonet
      POSTGRES_USER: sonet
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  nats:
    image: nats:2.10
    ports:
      - "4222:4222"
      - "8222:8222"

  meilisearch:
    image: getmeili/meilisearch:v1.5
    ports:
      - "7700:7700"
    environment:
      MEILI_MASTER_KEY: dev_master_key
    volumes:
      - meilisearch-data:/meili_data

volumes:
  scylla-data:
  postgres-data:
  redis-data:
  meilisearch-data:
"""

GENERATE_PROTOS = """#!/bin/bash
set -e

echo "📦 Generating protobuf code..."

PROTO_DIR="protos"
SWIFT_OUT="shared/proto-gen/swift"
RUST_OUT="shared/proto-gen/rust"

mkdir -p $SWIFT_OUT $RUST_OUT

protoc --swift_out=$SWIFT_OUT \\
       --grpc-swift_out=$SWIFT_OUT \\
       --proto_path=$PROTO_DIR \\
       $PROTO_DIR/*.proto

protoc --rust_out=$RUST_OUT \\
       --tonic_out=$RUST_OUT \\
       --proto_path=$PROTO_DIR \\
       $PROTO_DIR/*.proto

echo "✅ Protobuf generation complete"
"""

BUILD_ALL = """#!/bin/bash
set -e

echo "🐳 Building all Docker images..."

services=(
    "api-gateway"
    "user-service"
    "boo-service"
    "dm-service"
    "export-service"
    "feed-service"
    "media-service"
    "metrics-service"
    "ghost-reaper"
)

for service in "${services[@]}"; do
    echo "Building $service..."
    if [[ -d "services/swift/$service" ]]; then
        docker build -t sonet/$service:latest services/swift/$service
    elif [[ -d "services/rust/$service" ]]; then
        docker build -t sonet/$service:latest services/rust/$service
    fi
done

echo "✅ All images built"
"""

USER_PROTO = """syntax = "proto3";

package user;

service UserService {
  rpc GetUser(GetUserRequest) returns (UserResponse);
  rpc UpdateProfile(UpdateProfileRequest) returns (UserResponse);
  rpc FollowUser(FollowRequest) returns (FollowResponse);
  rpc UnfollowUser(FollowRequest) returns (FollowResponse);
}

message GetUserRequest {
  string user_id = 1;
}

message UserResponse {
  string id = 1;
  string username = 2;
  string avatar_url = 3;
  string todays_mood = 4;
  int32 follower_count = 5;
  int32 following_count = 6;
}

message UpdateProfileRequest {
  string user_id = 1;
  optional string username = 2;
  optional string avatar_url = 3;
  optional string todays_mood = 4;
}

message FollowRequest {
  string user_id = 1;
  string target_user_id = 2;
}

message FollowResponse {
  bool success = 1;
}
"""

BOO_PROTO = """syntax = "proto3";

package boo;

service BooService {
  rpc CreateBoo(CreateBooRequest) returns (BooResponse);
  rpc GetBoo(GetBooRequest) returns (BooResponse);
  rpc DeleteBoo(DeleteBooRequest) returns (DeleteBooResponse);
  rpc ArchiveBoo(ArchiveRequest) returns (ArchiveResponse);
}

message CreateBooRequest {
  string user_id = 1;
  string content = 2;
  repeated string media_urls = 3;
}

message BooResponse {
  string id = 1;
  string user_id = 2;
  string content = 3;
  repeated string media_urls = 4;
  int64 created_at = 5;
  int64 expires_at = 6;
  string lifecycle = 7;
  int32 fire_count = 8;
  int32 reply_count = 9;
}

message GetBooRequest {
  string boo_id = 1;
}

message DeleteBooRequest {
  string boo_id = 1;
}

message DeleteBooResponse {
  bool success = 1;
}

message ArchiveRequest {
  string boo_id = 1;
}

message ArchiveResponse {
  bool success = 1;
}
"""

FEED_PROTO = """syntax = "proto3";

package feed;

service FeedService {
  rpc GetFeed(GetFeedRequest) returns (FeedResponse);
  rpc RefreshFeed(RefreshFeedRequest) returns (FeedResponse);
}

message GetFeedRequest {
  string user_id = 1;
  int32 limit = 2;
  optional string cursor = 3;
}

message FeedResponse {
  repeated FeedItem items = 1;
  optional string next_cursor = 2;
}

message FeedItem {
  string boo_id = 1;
  string user_id = 2;
  string username = 3;
  string content = 4;
  int64 created_at = 5;
  int64 expires_at = 6;
}

message RefreshFeedRequest {
  string user_id = 1;
}
"""

SWIFT_PACKAGE = """// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "{}",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "{}", targets: ["{}"])
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),
        .package(url: "https://github.com/grpc/grpc-swift.git", from: "1.19.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
    ],
    targets: [
        .executableTarget(
            name: "{}",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "GRPC", package: "grpc-swift"),
                .product(name: "Logging", package: "swift-log"),
            ]
        ),
        .testTarget(
            name: "{}Tests",
            dependencies: [.target(name: "{}")]
        )
    ]
)
"""

SWIFT_MAIN = """import Vapor
import Logging

@main
struct Application {{
    static func main() async throws {{
        let app = Vapor.Application()
        defer {{ app.shutdown() }}
        
        try configure(app)
        try app.run()
    }}
}}

func configure(_ app: Vapor.Application) throws {{
    app.http.server.configuration.hostname = "0.0.0.0"
    app.http.server.configuration.port = 8080
    
    try routes(app)
}}

func routes(_ app: Vapor.Application) throws {{
    app.get("health") {{ req in
        return ["status": "ok"]
    }}
}}
"""

SWIFT_DOCKERFILE = """FROM swift:5.9 as builder
WORKDIR /build
COPY Package.* ./
RUN swift package resolve
COPY . .
RUN swift build -c release

FROM swift:5.9-slim
WORKDIR /app
COPY --from=builder /build/.build/release/{} ./
EXPOSE 8080
ENTRYPOINT ["./{}"]
"""

RUST_CARGO = """[package]
name = "{}"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = {{ version = "1.35", features = ["full"] }}
tonic = "0.11"
prost = "0.12"
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
tracing = "0.1"
tracing-subscriber = {{ version = "0.3", features = ["env-filter"] }}

[build-dependencies]
tonic-build = "0.11"
"""

RUST_MAIN = """use tonic::transport::Server;
use tracing_subscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();
    
    let addr = "0.0.0.0:50051".parse()?;
    
    tracing::info!("Server listening on {}", addr);
    
    Server::builder()
        .add_service(service_impl())
        .serve(addr)
        .await?;
    
    Ok(())
}

fn service_impl() -> impl tonic::codegen::Service<
    http::Request<tonic::body::BoxBody>,
    Response = http::Response<tonic::body::BoxBody>,
> {
    // Placeholder
    todo!()
}
"""

RUST_BUILD = """fn main() {
    tonic_build::configure()
        .build_server(true)
        .compile(&["../../protos/feed.proto"], &["../../protos"])
        .unwrap();
}
"""

RUST_DOCKERFILE = """FROM rust:1.75 as builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /build/target/release/{} ./
EXPOSE 50051
ENTRYPOINT ["./{}"]
"""

K8S_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {}
  namespace: sonet
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {}
  template:
    metadata:
      labels:
        app: {}
    spec:
      containers:
      - name: {}
        image: sonet/{}:latest
        ports:
        - containerPort: {}
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: {}
  namespace: sonet
spec:
  selector:
    app: {}
  ports:
  - port: {}
    targetPort: {}
"""

def create_file(path, content):
  dirpath = os.path.dirname(path)
  if dirpath:
    os.makedirs(dirpath, exist_ok=True)
  with open(path, 'w') as f:
    f.write(content.strip() + '\n')

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def create_swift_service(name, port=8080):
    base = f"services/swift/{name}"
    dirs = [
        f"{base}/Sources/{name}/Routes",
        f"{base}/Sources/{name}/Controllers",
        f"{base}/Sources/{name}/Services",
        f"{base}/Sources/{name}/Models",
        f"{base}/Sources/{name}/Database",
        f"{base}/Sources/{name}/gRPC",
        f"{base}/Sources/{name}/Config",
        f"{base}/Tests"
    ]
    for d in dirs:
        create_dir(d)
    
    create_file(f"{base}/Package.swift", SWIFT_PACKAGE.format(name, name, name, name, name, name))
    create_file(f"{base}/Sources/{name}/main.swift", SWIFT_MAIN)
    create_file(f"{base}/Dockerfile", SWIFT_DOCKERFILE.format(name, name))
    create_file(f"{base}/README.md", f"# {name}\n\n{name} microservice")

def create_rust_service(name, port=50051):
    base = f"services/rust/{name}"
    dirs = [
        f"{base}/src/service",
        f"{base}/src/models",
        f"{base}/src/db",
        f"{base}/src/grpc"
    ]
    for d in dirs:
        create_dir(d)
    
    create_file(f"{base}/Cargo.toml", RUST_CARGO.format(name))
    create_file(f"{base}/src/main.rs", RUST_MAIN)
    create_file(f"{base}/build.rs", RUST_BUILD)
    create_file(f"{base}/Dockerfile", RUST_DOCKERFILE.format(name, name))
    create_file(f"{base}/README.md", f"# {name}\n\n{name} microservice")

def create_k8s_manifest(name, port):
    base = f"infra/k8s/services/{name}"
    create_dir(base)
    create_file(f"{base}/deployment.yaml", K8S_DEPLOYMENT.format(name, name, name, name, name, port, name, name, port, port))

def main():
    print("🚀 Scaffolding Sonet Backend Monorepo...")
    
    create_dir(PROJECT_NAME)
    os.chdir(PROJECT_NAME)
    
    base_dirs = [
        "services/swift",
        "services/rust",
        "protos",
        "shared/proto-gen/swift",
        "shared/proto-gen/rust",
        "shared/scripts",
        "infra/k8s/base",
        "infra/k8s/services",
        "infra/k8s/databases/scylla",
        "infra/k8s/databases/postgres",
        "infra/k8s/databases/redis",
        "infra/k8s/monitoring/prometheus",
        "infra/k8s/monitoring/grafana",
        "infra/terraform/modules",
        "infra/docker-compose",
        "scripts",
        "docs/architecture",
        "docs/api",
        "docs/deployment"
    ]
    
    for d in base_dirs:
        create_dir(d)
    
    create_file("Makefile", MAKEFILE)
    create_file("README.md", "# Sonet Backend\n\nMicroservices backend for Sonet")
    create_file(".gitignore", "target/\n.build/\n*.swp\n.DS_Store\nshared/proto-gen/")
    
    create_file("scripts/generate-protos.sh", GENERATE_PROTOS)
    create_file("scripts/build-all.sh", BUILD_ALL)
    os.chmod("scripts/generate-protos.sh", 0o755)
    os.chmod("scripts/build-all.sh", 0o755)
    
    create_file("infra/docker-compose/docker-compose.yml", DOCKER_COMPOSE)
    
    create_file("protos/user.proto", USER_PROTO)
    create_file("protos/boo.proto", BOO_PROTO)
    create_file("protos/feed.proto", FEED_PROTO)
    create_file("protos/common.proto", 'syntax = "proto3";\n\npackage common;\n\nmessage Empty {}')
    
    swift_services = [
        ("api-gateway", 8080),
        ("user-service", 8081),
        ("boo-service", 8082),
        ("dm-service", 8083),
        ("export-service", 8084)
    ]
    
    for name, port in swift_services:
        create_swift_service(name, port)
        create_k8s_manifest(name, port)
    
    rust_services = [
        ("feed-service", 50051),
        ("media-service", 50052),
        ("metrics-service", 50053),
        ("ghost-reaper", 50054)
    ]
    
    for name, port in rust_services:
        create_rust_service(name, port)
        create_k8s_manifest(name, port)
    
    create_file("services/swift/build-all.sh", """#!/bin/bash
set -e
for service in */; do
    echo "Building ${service%/}..."
    cd "$service"
    swift build
    cd ..
done
echo "✅ All Swift services built"
""")
    os.chmod("services/swift/build-all.sh", 0o755)
    
    create_file("services/rust/Cargo.toml", """[workspace]
members = [
    "feed-service",
    "media-service",
    "metrics-service",
    "ghost-reaper"
]
resolver = "2"
""")
    
    create_file("infra/k8s/base/namespace.yaml", """apiVersion: v1
kind: Namespace
metadata:
  name: sonet
""")
    
    create_file("docs/architecture/overview.md", "# Sonet Architecture\n\nOverview of the microservices architecture")
    create_file("docs/deployment/local-setup.md", "# Local Development Setup\n\n1. Start dependencies: `make dev`\n2. Build services: `make build`")
    
    print("✅ Backend monorepo scaffolded successfully!")
    print(f"📂 Navigate to {PROJECT_NAME}")
    print("🏗️  Run: make dev (start local environment)")
    print("📦 Run: make proto (generate protobuf code)")
    print("🔨 Run: make build (build all services)")

if __name__ == "__main__":
    main()
