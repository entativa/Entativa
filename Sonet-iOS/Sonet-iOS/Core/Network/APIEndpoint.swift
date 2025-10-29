enum APIEndpoint {
    case boos
    case boo(id: String)
    case feed
    case userProfile(id: String)
    
    var path: String {
        switch self {
        case .boos: return "boos"
        case .boo(let id): return "boos/\(id)"
        case .feed: return "feed"
        case .userProfile(let id): return "users/\(id)"
        }
    }
}
