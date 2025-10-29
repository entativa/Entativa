// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "dm-service",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "dm-service", targets: ["dm-service"])
    ],
    dependencies: [
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),
        .package(url: "https://github.com/grpc/grpc-swift.git", from: "1.19.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
    ],
    targets: [
        .executableTarget(
            name: "dm-service",
            dependencies: [
                .product(name: "Vapor", package: "vapor"),
                .product(name: "GRPC", package: "grpc-swift"),
                .product(name: "Logging", package: "swift-log"),
            ]
        ),
        .testTarget(
            name: "dm-serviceTests",
            dependencies: [.target(name: "dm-service")]
        )
    ]
)
