#!/usr/bin/env python3

import os

PROJECT_NAME = "dahlia-backend"

MAKEFILE = """
.PHONY: help proto build test docker-build dev

help:
\t@echo "Dahlia Backend Commands:"
\t@echo "  make proto         - Generate protobuf code"
\t@echo "  make build         - Build all services"
\t@echo "  make test          - Run all tests"
\t@echo "  make docker-build  - Build Docker images"
\t@echo "  make dev           - Start local environment"

proto:
\t./scripts/generate-protos.sh

build:
\tcd services/kotlin && ./gradlew build
\tcd services/python && pip install -r requirements.txt

test:
\tcd services/kotlin && ./gradlew test
\tcd services/python && pytest

docker-build:
\t./scripts/build-all.sh

dev:
\tdocker-compose -f infra/docker-compose/docker-compose.yml up
"""

DOCKER_COMPOSE = """version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dahlia
      POSTGRES_USER: dahlia
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

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: dahlia
      MINIO_ROOT_PASSWORD: dahlia123
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: dahlia
      RABBITMQ_DEFAULT_PASS: dahlia123

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es-data:/usr/share/elasticsearch/data

volumes:
  postgres-data:
  redis-data:
  minio-data:
  es-data:
"""

GENERATE_PROTOS = """#!/bin/bash
set -e

PROTO_DIR="protos"
KOTLIN_OUT="shared/proto-gen/kotlin"
PYTHON_OUT="shared/proto-gen/python"

mkdir -p $KOTLIN_OUT $PYTHON_OUT

protoc --kotlin_out=$KOTLIN_OUT \\
       --grpc-kotlin_out=$KOTLIN_OUT \\
       --proto_path=$PROTO_DIR \\
       $PROTO_DIR/*.proto

protoc --python_out=$PYTHON_OUT \\
       --grpc_python_out=$PYTHON_OUT \\
       --proto_path=$PROTO_DIR \\
       $PROTO_DIR/*.proto

echo "✅ Protobuf generation complete"
"""

BUILD_ALL = """#!/bin/bash
set -e

services=(
    "api-gateway"
    "auth-service"
    "user-service"
    "post-service"
    "feed-service"
    "media-service"
    "notification-service"
    "search-service"
)

for service in "${services[@]}"; do
    if [[ -d "services/kotlin/$service" ]]; then
        docker build -t dahlia/$service:latest services/kotlin/$service
    elif [[ -d "services/python/$service" ]]; then
        docker build -t dahlia/$service:latest services/python/$service
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
  rpc GetFollowers(GetFollowersRequest) returns (FollowerListResponse);
}

message GetUserRequest {
  string user_id = 1;
}

message UserResponse {
  string id = 1;
  string username = 2;
  string display_name = 3;
  string bio = 4;
  string avatar_url = 5;
  int32 follower_count = 6;
  int32 following_count = 7;
  int32 post_count = 8;
}

message UpdateProfileRequest {
  string user_id = 1;
  optional string display_name = 2;
  optional string bio = 3;
  optional string avatar_url = 4;
}

message FollowRequest {
  string user_id = 1;
  string target_user_id = 2;
}

message FollowResponse {
  bool success = 1;
}

message GetFollowersRequest {
  string user_id = 1;
  int32 limit = 2;
  optional string cursor = 3;
}

message FollowerListResponse {
  repeated UserResponse users = 1;
  optional string next_cursor = 2;
}
"""

POST_PROTO = """syntax = "proto3";

package post;

service PostService {
  rpc CreatePost(CreatePostRequest) returns (PostResponse);
  rpc GetPost(GetPostRequest) returns (PostResponse);
  rpc DeletePost(DeletePostRequest) returns (DeletePostResponse);
  rpc LikePost(LikeRequest) returns (LikeResponse);
  rpc UnlikePost(LikeRequest) returns (LikeResponse);
}

message CreatePostRequest {
  string user_id = 1;
  string image_url = 2;
  string caption = 3;
  optional string location = 4;
}

message PostResponse {
  string id = 1;
  string user_id = 2;
  string image_url = 3;
  string caption = 4;
  optional string location = 5;
  int64 created_at = 6;
  int32 like_count = 7;
  int32 comment_count = 8;
}

message GetPostRequest {
  string post_id = 1;
}

message DeletePostRequest {
  string post_id = 1;
}

message DeletePostResponse {
  bool success = 1;
}

message LikeRequest {
  string post_id = 1;
  string user_id = 2;
}

message LikeResponse {
  bool success = 1;
}
"""

AUTH_PROTO = """syntax = "proto3";

package auth;

service AuthService {
  rpc Login(LoginRequest) returns (AuthResponse);
  rpc Signup(SignupRequest) returns (AuthResponse);
  rpc RefreshToken(RefreshRequest) returns (AuthResponse);
  rpc Logout(LogoutRequest) returns (LogoutResponse);
}

message LoginRequest {
  string email = 1;
  string password = 2;
}

message SignupRequest {
  string email = 1;
  string username = 2;
  string password = 3;
}

message AuthResponse {
  string access_token = 1;
  string refresh_token = 2;
  string user_id = 3;
  int64 expires_in = 4;
}

message RefreshRequest {
  string refresh_token = 1;
}

message LogoutRequest {
  string user_id = 1;
}

message LogoutResponse {
  bool success = 1;
}
"""

KOTLIN_SETTINGS = """rootProject.name = "dahlia-services"

include(":api-gateway")
include(":auth-service")
include(":user-service")
include(":post-service")
include(":feed-service")
include(":notification-service")
"""

KOTLIN_BUILD = """plugins {
    kotlin("jvm") version "1.9.22" apply false
    kotlin("plugin.serialization") version "1.9.22" apply false
}

allprojects {
    group = "com.dahlia"
    version = "1.0.0"
    
    repositories {
        mavenCentral()
    }
}
"""

KOTLIN_SERVICE_BUILD = """plugins {{
    kotlin("jvm")
    kotlin("plugin.serialization")
    application
}}

dependencies {{
    implementation("io.ktor:ktor-server-core:2.3.7")
    implementation("io.ktor:ktor-server-netty:2.3.7")
    implementation("io.ktor:ktor-server-content-negotiation:2.3.7")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
    implementation("io.grpc:grpc-kotlin-stub:1.4.1")
    implementation("io.grpc:grpc-netty:1.60.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.exposed:exposed-core:0.46.0")
    implementation("org.jetbrains.exposed:exposed-dao:0.46.0")
    implementation("org.jetbrains.exposed:exposed-jdbc:0.46.0")
    implementation("org.postgresql:postgresql:42.7.1")
    implementation("redis.clients:jedis:5.1.0")
    implementation("ch.qos.logback:logback-classic:1.4.14")
    
    testImplementation(kotlin("test"))
}}

application {{
    mainClass.set("com.dahlia.{}.ApplicationKt")
}}

tasks.test {{
    useJUnitPlatform()
}}
"""

KOTLIN_MAIN = """package com.dahlia.{}

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun main() {{
    embeddedServer(Netty, port = {}) {{
        routing {{
            get("/health") {{
                call.respondText("OK")
            }}
        }}
    }}.start(wait = true)
}}
"""

KOTLIN_DOCKERFILE = """FROM gradle:8.5-jdk17 AS builder
WORKDIR /app
COPY . .
RUN gradle {} --no-daemon

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/build/libs/{}-1.0.0.jar app.jar
EXPOSE {}
ENTRYPOINT ["java", "-jar", "app.jar"]
"""

PYTHON_REQUIREMENTS = """fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
pillow==10.2.0
opencv-python==4.9.0.80
numpy==1.26.3
tensorflow==2.15.0
torch==2.1.2
torchvision==0.16.2
boto3==1.34.34
celery==5.3.6
grpcio==1.60.0
grpcio-tools==1.60.0
pyjwt==2.8.0
python-multipart==0.0.6
httpx==0.26.0
"""

PYTHON_MAIN = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {{"status": "ok"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={})
"""

PYTHON_DOCKERFILE = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {}
CMD ["python", "main.py"]
"""

K8S_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {}
  namespace: dahlia
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
        image: dahlia/{}:latest
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
  namespace: dahlia
spec:
  selector:
    app: {}
  ports:
  - port: {}
    targetPort: {}
"""

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def create_kotlin_service(name, port):
    base = f"services/kotlin/{name}"
    service_name = name.replace("-", "")
    
    dirs = [
        f"{base}/src/main/kotlin/com/dahlia/{service_name}",
        f"{base}/src/main/kotlin/com/dahlia/{service_name}/config",
        f"{base}/src/main/kotlin/com/dahlia/{service_name}/service",
        f"{base}/src/main/kotlin/com/dahlia/{service_name}/repository",
        f"{base}/src/main/kotlin/com/dahlia/{service_name}/model",
        f"{base}/src/main/kotlin/com/dahlia/{service_name}/grpc",
        f"{base}/src/test/kotlin/com/dahlia/{service_name}"
    ]
    
    for d in dirs:
        create_dir(d)
    
    create_file(f"{base}/build.gradle.kts", KOTLIN_SERVICE_BUILD.format(service_name))
    create_file(f"{base}/src/main/kotlin/com/dahlia/{service_name}/Application.kt", 
                KOTLIN_MAIN.format(service_name, port))
    create_file(f"{base}/Dockerfile", KOTLIN_DOCKERFILE.format(f":{name}:build", name, port))
    create_file(f"{base}/README.md", f"# {name}\n\n{name} microservice")

def create_python_service(name, port):
    base = f"services/python/{name}"
    
    dirs = [
        f"{base}/app",
        f"{base}/app/api",
        f"{base}/app/core",
        f"{base}/app/models",
        f"{base}/app/services",
        f"{base}/app/ml",
        f"{base}/tests"
    ]
    
    for d in dirs:
        create_dir(d)
    
    create_file(f"{base}/requirements.txt", PYTHON_REQUIREMENTS)
    create_file(f"{base}/main.py", PYTHON_MAIN.format(name, port))
    create_file(f"{base}/Dockerfile", PYTHON_DOCKERFILE.format(port))
    create_file(f"{base}/README.md", f"# {name}\n\n{name} microservice")
    create_file(f"{base}/app/__init__.py", "")
    create_file(f"{base}/app/api/__init__.py", "")
    create_file(f"{base}/app/core/__init__.py", "")
    create_file(f"{base}/app/models/__init__.py", "")
    create_file(f"{base}/app/services/__init__.py", "")
    create_file(f"{base}/tests/__init__.py", "")

def create_k8s_manifest(name, port):
    base = f"infra/k8s/services/{name}"
    create_dir(base)
    create_file(f"{base}/deployment.yaml", 
                K8S_DEPLOYMENT.format(name, name, name, name, name, port, name, name, port, port))

def main():
    print("🌸 Scaffolding Dahlia Backend Monorepo...")
    
    create_dir(PROJECT_NAME)
    os.chdir(PROJECT_NAME)
    
    base_dirs = [
        "services/kotlin",
        "services/python",
        "protos",
        "shared/proto-gen/kotlin",
        "shared/proto-gen/python",
        "shared/scripts",
        "infra/k8s/base",
        "infra/k8s/services",
        "infra/terraform/modules",
        "infra/docker-compose",
        "scripts",
        "docs"
    ]
    
    for d in base_dirs:
        create_dir(d)
    
    create_file("Makefile", MAKEFILE)
    create_file("README.md", "# Dahlia Backend\n\nMicroservices backend for Dahlia")
    create_file(".gitignore", "*.pyc\n__pycache__/\n.gradle/\nbuild/\ntarget/\n.idea/\n*.iml\nshared/proto-gen/")
    
    create_file("scripts/generate-protos.sh", GENERATE_PROTOS)
    create_file("scripts/build-all.sh", BUILD_ALL)
    os.chmod("scripts/generate-protos.sh", 0o755)
    os.chmod("scripts/build-all.sh", 0o755)
    
    create_file("infra/docker-compose/docker-compose.yml", DOCKER_COMPOSE)
    
    create_file("protos/user.proto", USER_PROTO)
    create_file("protos/post.proto", POST_PROTO)
    create_file("protos/auth.proto", AUTH_PROTO)
    create_file("protos/common.proto", 'syntax = "proto3";\n\npackage common;\n\nmessage Empty {}')
    
    kotlin_services = [
        ("api-gateway", 8080),
        ("auth-service", 8081),
        ("user-service", 8082),
        ("post-service", 8083),
        ("feed-service", 8084),
        ("notification-service", 8085)
    ]
    
    create_file("services/kotlin/settings.gradle.kts", KOTLIN_SETTINGS)
    create_file("services/kotlin/build.gradle.kts", KOTLIN_BUILD)
    
    for name, port in kotlin_services:
        create_kotlin_service(name, port)
        create_k8s_manifest(name, port)
    
    python_services = [
        ("media-service", 9000),
        ("search-service", 9001),
        ("recommendation-service", 9002)
    ]
    
    for name, port in python_services:
        create_python_service(name, port)
        create_k8s_manifest(name, port)
    
    create_file("services/python/shared_requirements.txt", PYTHON_REQUIREMENTS)
    
    create_file("infra/k8s/base/namespace.yaml", """apiVersion: v1
kind: Namespace
metadata:
  name: dahlia
""")
    
    create_file("docs/architecture.md", """# Dahlia Architecture

## Services

### Kotlin Services
- **api-gateway** (8080): REST API gateway
- **auth-service** (8081): Dahlia ID authentication
- **user-service** (8082): User profiles and relationships
- **post-service** (8083): Post CRUD operations
- **feed-service** (8084): Timeline generation
- **notification-service** (8085): Push notifications

### Python Services
- **media-service** (9000): Image processing, compression
- **search-service** (9001): Elasticsearch integration
- **recommendation-service** (9002): ML-based recommendations

## Tech Stack
- **Kotlin**: Ktor + Exposed + gRPC
- **Python**: FastAPI + TensorFlow/PyTorch
- **Databases**: PostgreSQL, Redis, Elasticsearch
- **Storage**: MinIO (S3-compatible)
- **Message Queue**: RabbitMQ
""")
    
    create_file("docs/api.md", """# Dahlia API Documentation

## Authentication
All endpoints require Bearer token except /auth/* endpoints.

```
Authorization: Bearer <access_token>
```

## Endpoints

### Auth
- POST /auth/login
- POST /auth/signup
- POST /auth/refresh
- POST /auth/logout

### Users
- GET /users/{id}
- PUT /users/{id}
- POST /users/{id}/follow
- DELETE /users/{id}/follow

### Posts
- POST /posts
- GET /posts/{id}
- DELETE /posts/{id}
- POST /posts/{id}/like
- DELETE /posts/{id}/like

### Feed
- GET /feed
- GET /feed/foryou
""")
    
    print("✅ Dahlia backend scaffolded successfully!")
    print(f"📂 Navigate to {PROJECT_NAME}")
    print("🏗️  Kotlin services: api-gateway, auth, user, post, feed, notification")
    print("🐍 Python services: media, search, recommendation")
    print("💾 Databases: PostgreSQL, Redis, Elasticsearch, MinIO")
    print("🔨 Run: make dev (start local environment)")
    print("📦 Run: make proto (generate protobuf code)")

if __name__ == "__main__":
    main()
