// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "api-gateway",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "api-gateway", targets: ["api-gateway"])
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),
        .package(url: "https://github.com/grpc/grpc-swift.git", from: "1.19.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
    ],
    targets: [
        .executableTarget(
            name: "api-gateway",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "GRPC", package: "grpc-swift"),
                .product(name: "Logging", package: "swift-log"),
            ]
        ),
        .testTarget(
            name: "api-gatewayTests",
            dependencies: [.target(name: "api-gateway")]
        )
    ]
)
