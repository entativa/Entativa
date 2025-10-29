import SwiftUI

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
