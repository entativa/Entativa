import Foundation

struct User: Identifiable, Codable {
    let id: UUID
    let username: String
    let avatar: URL?
    let todaysMood: String?
    var followerCount: Int
    var followingCount: Int
}
