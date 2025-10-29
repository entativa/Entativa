import Foundation

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
