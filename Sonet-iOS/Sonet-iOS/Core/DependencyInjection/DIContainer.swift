import Foundation

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
