import Foundation

struct FireBooUseCase {
    private let repository: BooRepositoryProtocol
    
    init(repository: BooRepositoryProtocol) {
        self.repository = repository
    }
    
    func execute() async throws -> [] {
        // Implementation
        fatalError("Not implemented")
    }
}
