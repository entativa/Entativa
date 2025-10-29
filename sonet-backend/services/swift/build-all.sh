#!/bin/bash
set -e
for service in */; do
    echo "Building ${service%/}..."
    cd "$service"
    swift build
    cd ..
done
echo "✅ All Swift services built"
