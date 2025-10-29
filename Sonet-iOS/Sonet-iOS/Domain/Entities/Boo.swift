import Foundation

struct Boo: Identifiable, Codable {
    let id: UUID
    let userId: UUID
    let username: String
    let userAvatar: URL?
    let content: String
    let mediaUrls: [URL]
    let createdAt: Date
    let expiresAt: Date
    let ghostsAt: Date
    let oblivionAt: Date
    var fireCount: Int
    var replyCount: Int
    var saveCount: Int
    var duetCount: Int
    var lifecycle: BooLifecycle
    
    var timeRemaining: TimeInterval {
        expiresAt.timeIntervalSinceNow
    }
    
    var isLive: Bool {
        lifecycle == .live
    }
    
    var isGhost: Bool {
        lifecycle == .ghost
    }
}

enum BooLifecycle: String, Codable {
    case live
    case ghost
    case oblivion
}
