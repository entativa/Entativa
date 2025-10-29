#!/bin/bash
set -e

echo "📦 Generating protobuf code..."

PROTO_DIR="protos"
SWIFT_OUT="shared/proto-gen/swift"
RUST_OUT="shared/proto-gen/rust"

mkdir -p $SWIFT_OUT $RUST_OUT

protoc --swift_out=$SWIFT_OUT \
       --grpc-swift_out=$SWIFT_OUT \
       --proto_path=$PROTO_DIR \
       $PROTO_DIR/*.proto

protoc --rust_out=$RUST_OUT \
       --tonic_out=$RUST_OUT \
       --proto_path=$PROTO_DIR \
       $PROTO_DIR/*.proto

echo "✅ Protobuf generation complete"
