fn main() {
    tonic_build::configure()
        .build_server(true)
        .compile(&["../../protos/feed.proto"], &["../../protos"])
        .unwrap();
}
