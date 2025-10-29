package com.sonet.network
import io.ktor.client.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*

object HttpClientFactory {
    fun create(): HttpClient = HttpClient {
        install(ContentNegotiation) { json() }
    }
}
