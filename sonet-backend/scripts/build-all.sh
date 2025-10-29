#!/bin/bash
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
