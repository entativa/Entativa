// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Sonet",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "SonetCore", targets: ["SonetCore"])
    ],
    dependencies: [
        .package(url: "https://github.com/groue/GRDB.swift.git", from: "6.0.0"),
        .package(url: "https://github.com/onevcat/Kingfisher.git", from: "7.0.0")
    ],
    targets: [
        .target(
            name: "SonetCore",
            dependencies: [
                .product(name: "GRDB", package: "GRDB.swift")
            ]
        )
    ]
)
