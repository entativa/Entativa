// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "user-service",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "user-service", targets: ["user-service"])
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),
        .package(url: "https://github.com/grpc/grpc-swift.git", from: "1.19.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
    ],
    targets: [
        .executableTarget(
            name: "user-service",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "GRPC", package: "grpc-swift"),
                .product(name: "Logging", package: "swift-log"),
            ]
        ),
        .testTarget(
            name: "user-serviceTests",
            dependencies: [.target(name: "user-service")]
        )
    ]
)
