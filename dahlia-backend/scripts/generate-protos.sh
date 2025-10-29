#!/bin/bash
set -e

PROTO_DIR="protos"
KOTLIN_OUT="shared/proto-gen/kotlin"
PYTHON_OUT="shared/proto-gen/python"

mkdir -p $KOTLIN_OUT $PYTHON_OUT

protoc --kotlin_out=$KOTLIN_OUT \
       --grpc-kotlin_out=$KOTLIN_OUT \
       --proto_path=$PROTO_DIR \
       $PROTO_DIR/*.proto

protoc --python_out=$PYTHON_OUT \
       --grpc_python_out=$PYTHON_OUT \
       --proto_path=$PROTO_DIR \
       $PROTO_DIR/*.proto

echo "✅ Protobuf generation complete"
