package com.sonet.domain.model
import kotlinx.serialization.Serializable
import kotlinx.datetime.Instant

@Serializable
data class Boo(
    val id: String,
    val userId: String,
    val username: String,
    val content: String,
    val createdAt: Instant,
    val expiresAt: Instant,
    val lifecycle: BooLifecycle = BooLifecycle.LIVE
)

enum class BooLifecycle { LIVE, GHOST, OBLIVION }
