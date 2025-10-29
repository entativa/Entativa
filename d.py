#!/usr/bin/env python3

import os
import sys

PROJECT_NAME = "Sonet-iOS"
BUNDLE_ID = "com.sonet.app"

PACKAGE_SWIFT = """// swift-tools-version: 5.9
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
"""

SONET_APP = """import SwiftUI

@main
struct SonetApp: App {
    @StateObject private var appState = AppState()
    
    init() {
        setupDependencies()
    }
    
    var body: some Scene {
        WindowGroup {
            MainTabView()
                .environmentObject(appState)
        }
    }
    
    private func setupDependencies() {
        let _ = DIContainer.shared
    }
}
"""

APP_STATE = """import SwiftUI

class AppState: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
}
"""

DI_CONTAINER = """import Foundation

class DIContainer {
    static let shared = DIContainer()
    
    lazy var networkClient: NetworkClient = NetworkClientImpl()
    lazy var databaseManager: DatabaseManager = DatabaseManager()
    
    lazy var booRepository: BooRepositoryProtocol = BooRepository(
        api: BooAPI(client: networkClient),
        cache: BooCache()
    )
    
    lazy var feedRepository: FeedRepositoryProtocol = FeedRepository(
        api: FeedAPI(client: networkClient)
    )
    
    lazy var userRepository: UserRepositoryProtocol = UserRepository(
        api: UserAPI(client: networkClient)
    )
    
    lazy var getFeedUseCase = GetFeedUseCase(repository: feedRepository)
    lazy var createBooUseCase = CreateBooUseCase(repository: booRepository)
    lazy var fireBooUseCase = FireBooUseCase(repository: booRepository)
}
"""

NETWORK_CLIENT = """import Foundation

protocol NetworkClient {
    func request<T: Decodable>(_ endpoint: APIEndpoint, method: HTTPMethod, body: Encodable?) async throws -> T
}

class NetworkClientImpl: NetworkClient {
    private let session: URLSession
    private let baseURL: URL
    
    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        self.session = URLSession(configuration: config)
        self.baseURL = URL(string: "https://api.sonet.app/v1")!
    }
    
    func request<T: Decodable>(_ endpoint: APIEndpoint, method: HTTPMethod, body: Encodable?) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint.path)
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        
        if let token = KeychainManager.shared.getToken() {
            request.setValue("Bearer \\(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        
        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode(T.self, from: data)
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}
"""

API_ENDPOINT = """enum APIEndpoint {
    case boos
    case boo(id: String)
    case feed
    case userProfile(id: String)
    
    var path: String {
        switch self {
        case .boos: return "boos"
        case .boo(let id): return "boos/\\(id)"
        case .feed: return "feed"
        case .userProfile(let id): return "users/\\(id)"
        }
    }
}
"""

BOO_MODEL = """import Foundation

struct Boo: Identifiable, Codable {
    let id: UUID
    let userId: UUID
    let username: String
    let userAvatar: URL?
    let content: String
    let mediaUrls: [URL]
    let createdAt: Date
    let expiresAt: Date
    let ghostsAt: Date
    let oblivionAt: Date
    var fireCount: Int
    var replyCount: Int
    var saveCount: Int
    var duetCount: Int
    var lifecycle: BooLifecycle
    
    var timeRemaining: TimeInterval {
        expiresAt.timeIntervalSinceNow
    }
    
    var isLive: Bool {
        lifecycle == .live
    }
    
    var isGhost: Bool {
        lifecycle == .ghost
    }
}

enum BooLifecycle: String, Codable {
    case live
    case ghost
    case oblivion
}
"""

USER_MODEL = """import Foundation

struct User: Identifiable, Codable {
    let id: UUID
    let username: String
    let avatar: URL?
    let todaysMood: String?
    var followerCount: Int
    var followingCount: Int
}
"""

BOO_REPOSITORY = """import Foundation

protocol BooRepositoryProtocol {
    func createBoo(_ content: String, mediaUrls: [URL]) async throws -> Boo
    func getBoo(id: UUID) async throws -> Boo
    func deleteBoo(id: UUID) async throws
    func fireBoo(id: UUID) async throws
    func archiveBoo(id: UUID) async throws
}

class BooRepository: BooRepositoryProtocol {
    private let api: BooAPI
    private let cache: BooCache
    
    init(api: BooAPI, cache: BooCache) {
        self.api = api
        self.cache = cache
    }
    
    func createBoo(_ content: String, mediaUrls: [URL]) async throws -> Boo {
        let boo = try await api.createBoo(content: content, mediaUrls: mediaUrls)
        cache.save(boo)
        return boo
    }
    
    func getBoo(id: UUID) async throws -> Boo {
        if let cached = cache.get(id) {
            return cached
        }
        let boo = try await api.getBoo(id: id)
        cache.save(boo)
        return boo
    }
    
    func deleteBoo(id: UUID) async throws {
        try await api.deleteBoo(id: id)
        cache.remove(id)
    }
    
    func fireBoo(id: UUID) async throws {
        try await api.fireBoo(id: id)
    }
    
    func archiveBoo(id: UUID) async throws {
        try await api.archiveBoo(id: id)
    }
}
"""

BOO_CACHE = """import Foundation

class BooCache {
    private var cache: [UUID: Boo] = [:]
    
    func save(_ boo: Boo) {
        cache[boo.id] = boo
    }
    
    func get(_ id: UUID) -> Boo? {
        cache[id]
    }
    
    func remove(_ id: UUID) {
        cache.removeValue(forKey: id)
    }
    
    func clear() {
        cache.removeAll()
    }
}
"""

FEED_VIEWMODEL = """import SwiftUI

class FeedViewModel: ObservableObject {
    @Published var boos: [Boo] = []
    @Published var isLoading = false
    @Published var error: Error?
    
    private let getFeedUseCase: GetFeedUseCase
    
    init(getFeedUseCase: GetFeedUseCase = DIContainer.shared.getFeedUseCase) {
        self.getFeedUseCase = getFeedUseCase
    }
    
    func loadFeed() async {
        isLoading = true
        do {
            boos = try await getFeedUseCase.execute()
        } catch {
            self.error = error
        }
        isLoading = false
    }
    
    func refresh() async {
        await loadFeed()
    }
}
"""

FEED_VIEW = """import SwiftUI

struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 16) {
                    ForEach(viewModel.boos) { boo in
                        BooCard(boo: boo)
                    }
                }
                .padding()
            }
            .navigationTitle("Feed")
            .refreshable {
                await viewModel.refresh()
            }
        }
        .task {
            await viewModel.loadFeed()
        }
    }
}
"""

BOO_CARD = """import SwiftUI

struct BooCard: View {
    let boo: Boo
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(boo.username)
                    .font(.headline)
                Spacer()
                CountdownTimer(expiresAt: boo.expiresAt)
            }
            
            Text(boo.content)
                .font(.body)
            
            HStack(spacing: 20) {
                MetricButton(icon: "flame.fill", count: boo.fireCount)
                MetricButton(icon: "bubble.right", count: boo.replyCount)
                MetricButton(icon: "heart", count: boo.saveCount)
                MetricButton(icon: "arrow.turn.up.right", count: boo.duetCount)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
"""

COUNTDOWN_TIMER = """import SwiftUI

struct CountdownTimer: View {
    let expiresAt: Date
    @State private var timeRemaining: TimeInterval
    
    init(expiresAt: Date) {
        self.expiresAt = expiresAt
        self._timeRemaining = State(initialValue: expiresAt.timeIntervalSinceNow)
    }
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: "flame.fill")
                .font(.caption2)
            Text(formattedTime)
                .font(.caption.monospacedDigit())
        }
        .foregroundColor(timeColor)
        .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
            timeRemaining = expiresAt.timeIntervalSinceNow
        }
    }
    
    private var formattedTime: String {
        let hours = Int(timeRemaining) / 3600
        let minutes = (Int(timeRemaining) % 3600) / 60
        return "\\(hours)h \\(minutes)m"
    }
    
    private var timeColor: Color {
        timeRemaining < 3600 ? .red : timeRemaining < 10800 ? .orange : .secondary
    }
}
"""

MAIN_TAB_VIEW = """import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            FeedView()
                .tabItem {
                    Label("Feed", systemImage: "house.fill")
                }
            
            ExploreView()
                .tabItem {
                    Label("Explore", systemImage: "magnifyingglass")
                }
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
            
            MessagesView()
                .tabItem {
                    Label("Messages", systemImage: "message.fill")
                }
        }
    }
}
"""

KEYCHAIN_MANAGER = """import Foundation
import Security

class KeychainManager {
    static let shared = KeychainManager()
    private let service = "com.sonet.app"
    
    func saveToken(_ token: String) {
        let data = token.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token",
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }
    
    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token",
            kSecReturnData as String: true
        ]
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }
    
    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token"
        ]
        SecItemDelete(query as CFDictionary)
    }
}
"""

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    print("🚀 Scaffolding Sonet iOS project...")
    
    create_dir(PROJECT_NAME)
    os.chdir(PROJECT_NAME)
    
    dirs = [
        f"{PROJECT_NAME}/App",
        f"{PROJECT_NAME}/Core/DependencyInjection",
        f"{PROJECT_NAME}/Core/Network",
        f"{PROJECT_NAME}/Core/Storage",
        f"{PROJECT_NAME}/Core/Extensions",
        f"{PROJECT_NAME}/Core/Utils",
        f"{PROJECT_NAME}/Core/Constants",
        f"{PROJECT_NAME}/Domain/Entities",
        f"{PROJECT_NAME}/Domain/UseCases/Boo",
        f"{PROJECT_NAME}/Domain/UseCases/Feed",
        f"{PROJECT_NAME}/Domain/UseCases/User",
        f"{PROJECT_NAME}/Domain/UseCases/Auth",
        f"{PROJECT_NAME}/Domain/UseCases/DM",
        f"{PROJECT_NAME}/Domain/UseCases/Export",
        f"{PROJECT_NAME}/Domain/Repositories",
        f"{PROJECT_NAME}/Data/Repositories",
        f"{PROJECT_NAME}/Data/Network/API",
        f"{PROJECT_NAME}/Data/Network/DTOs",
        f"{PROJECT_NAME}/Data/Network/Mappers",
        f"{PROJECT_NAME}/Data/Local/Database/Models",
        f"{PROJECT_NAME}/Data/Local/Database/Migrations",
        f"{PROJECT_NAME}/Data/Local/Cache",
        f"{PROJECT_NAME}/Data/Export",
        f"{PROJECT_NAME}/Presentation/Common/Components",
        f"{PROJECT_NAME}/Presentation/Common/Modifiers",
        f"{PROJECT_NAME}/Presentation/Common/ViewModels",
        f"{PROJECT_NAME}/Presentation/Auth/Views",
        f"{PROJECT_NAME}/Presentation/Auth/ViewModels",
        f"{PROJECT_NAME}/Presentation/Main",
        f"{PROJECT_NAME}/Presentation/Feed/Views",
        f"{PROJECT_NAME}/Presentation/Feed/ViewModels",
        f"{PROJECT_NAME}/Presentation/Explore/Views",
        f"{PROJECT_NAME}/Presentation/Explore/ViewModels",
        f"{PROJECT_NAME}/Presentation/Profile/Views",
        f"{PROJECT_NAME}/Presentation/Profile/ViewModels",
        f"{PROJECT_NAME}/Presentation/Messages/Views",
        f"{PROJECT_NAME}/Presentation/Messages/ViewModels",
        f"{PROJECT_NAME}/Presentation/Export/Views",
        f"{PROJECT_NAME}/Presentation/Export/ViewModels",
        f"{PROJECT_NAME}/Resources",
        f"{PROJECT_NAME}Tests",
        f"{PROJECT_NAME}UITests",
        "Packages/SonetCore/Sources/SonetCore"
    ]
    
    for d in dirs:
        create_dir(d)
    
    create_file("Packages/SonetCore/Package.swift", PACKAGE_SWIFT)
    create_file(f"{PROJECT_NAME}/App/SonetApp.swift", SONET_APP)
    create_file(f"{PROJECT_NAME}/App/AppState.swift", APP_STATE)
    create_file(f"{PROJECT_NAME}/Core/DependencyInjection/DIContainer.swift", DI_CONTAINER)
    create_file(f"{PROJECT_NAME}/Core/Network/NetworkClient.swift", NETWORK_CLIENT)
    create_file(f"{PROJECT_NAME}/Core/Network/APIEndpoint.swift", API_ENDPOINT)
    create_file(f"{PROJECT_NAME}/Core/Storage/KeychainManager.swift", KEYCHAIN_MANAGER)
    create_file(f"{PROJECT_NAME}/Domain/Entities/Boo.swift", BOO_MODEL)
    create_file(f"{PROJECT_NAME}/Domain/Entities/User.swift", USER_MODEL)
    create_file(f"{PROJECT_NAME}/Domain/Repositories/BooRepositoryProtocol.swift", BOO_REPOSITORY)
    create_file(f"{PROJECT_NAME}/Data/Local/Cache/BooCache.swift", BOO_CACHE)
    create_file(f"{PROJECT_NAME}/Presentation/Feed/ViewModels/FeedViewModel.swift", FEED_VIEWMODEL)
    create_file(f"{PROJECT_NAME}/Presentation/Feed/Views/FeedView.swift", FEED_VIEW)
    create_file(f"{PROJECT_NAME}/Presentation/Common/Components/BooCard.swift", BOO_CARD)
    create_file(f"{PROJECT_NAME}/Presentation/Common/Components/CountdownTimer.swift", COUNTDOWN_TIMER)
    create_file(f"{PROJECT_NAME}/Presentation/Main/MainTabView.swift", MAIN_TAB_VIEW)
    
    placeholder_views = [
        ("Presentation/Explore/Views/ExploreView.swift", "ExploreView"),
        ("Presentation/Profile/Views/ProfileView.swift", "ProfileView"),
        ("Presentation/Messages/Views/MessagesView.swift", "MessagesView")
    ]
    
    for path, name in placeholder_views:
        content = f"""import SwiftUI

struct {name}: View {{
    var body: some View {{
        NavigationView {{
            Text("{name}")
                .navigationTitle("{name}")
        }}
    }}
}}
"""
        create_file(f"{PROJECT_NAME}/{path}", content)
    
    use_case_template = """import Foundation

struct {}UseCase {{
    private let repository: {}RepositoryProtocol
    
    init(repository: {}RepositoryProtocol) {{
        self.repository = repository
    }}
    
    func execute() async throws -> [{}] {{
        // Implementation
        fatalError("Not implemented")
    }}
}}
"""
    
    use_cases = [
        ("GetFeedUseCase", "Feed", "Boo"),
        ("CreateBooUseCase", "Boo", "Boo"),
        ("FireBooUseCase", "Boo", "Void")
    ]
    
    for name, repo, ret in use_cases:
        content = use_case_template.format(name.replace("UseCase", ""), repo, repo, ret if ret != "Void" else "")
        create_file(f"{PROJECT_NAME}/Domain/UseCases/{repo}/{name}.swift", content)
    
    print("✅ Project scaffolded successfully!")
    print(f"📂 Navigate to {PROJECT_NAME}")
    print("🏗️  Open Sonet-iOS.xcodeproj in Xcode")

if __name__ == "__main__":
    main()
