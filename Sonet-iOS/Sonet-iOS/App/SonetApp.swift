import SwiftUI

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
