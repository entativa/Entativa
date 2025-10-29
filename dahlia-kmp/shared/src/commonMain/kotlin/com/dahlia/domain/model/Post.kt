package com.dahlia.domain.model
import kotlinx.serialization.Serializable
import kotlinx.datetime.Instant

@Serializable
data class Post(
    val id: String,
    val userId: String,
    val username: String,
    val userAvatar: String?,
    val imageUrl: String,
    val caption: String,
    val location: String?,
    val createdAt: Instant,
    val likeCount: Int = 0,
    val commentCount: Int = 0,
    val isLiked: Boolean = false
)
