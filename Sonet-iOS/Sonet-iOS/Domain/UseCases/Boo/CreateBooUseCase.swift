import Foundation

struct CreateBooUseCase {
    private let repository: BooRepositoryProtocol
    
    init(repository: BooRepositoryProtocol) {
        self.repository = repository
    }
    
    func execute() async throws -> [Boo] {
        // Implementation
        fatalError("Not implemented")
    }
}
