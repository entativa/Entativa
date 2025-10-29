#!/bin/bash
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
