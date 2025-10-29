import Foundation

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
