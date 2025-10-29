import Foundation

struct GetFeedUseCase {
    private let repository: FeedRepositoryProtocol
    
    init(repository: FeedRepositoryProtocol) {
        self.repository = repository
    }
    
    func execute() async throws -> [Boo] {
        // Implementation
        fatalError("Not implemented")
    }
}
