import Foundation

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
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
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
