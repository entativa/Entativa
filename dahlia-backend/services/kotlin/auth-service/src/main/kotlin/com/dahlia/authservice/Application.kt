package com.dahlia.authservice

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun main() {
    embeddedServer(Netty, port = 8081) {
        routing {
            get("/health") {
                call.respondText("OK")
            }
        }
    }.start(wait = true)
}
