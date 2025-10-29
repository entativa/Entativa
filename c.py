#!/usr/bin/env python3

import os
import sys

PROJECT_NAME = "sonet-kmp"
PACKAGE = "com.sonet"
PACKAGE_PATH = "com/sonet"

GRADLE_VERSIONS = """[versions]
kotlin = "1.9.20"
compose = "1.5.10"
agp = "8.1.4"
ktor = "2.3.6"
sqldelight = "2.0.1"
koin = "3.5.0"
coroutines = "1.7.3"

[libraries]
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-logging = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
ktor-client-js = { module = "io.ktor:ktor-client-js", version.ref = "ktor" }
sqldelight-driver-android = { module = "app.cash.sqldelight:android-driver", version.ref = "sqldelight" }
sqldelight-driver-native = { module = "app.cash.sqldelight:native-driver", version.ref = "sqldelight" }
sqldelight-driver-sqlite = { module = "app.cash.sqldelight:sqlite-driver", version.ref = "sqldelight" }
sqldelight-driver-js = { module = "app.cash.sqldelight:web-worker-driver", version.ref = "sqldelight" }
koin-core = { module = "io.insert-koin:koin-core", version.ref = "koin" }
koin-android = { module = "io.insert-koin:koin-android", version.ref = "koin" }
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
kotlinx-datetime = { module = "org.jetbrains.kotlinx:kotlinx-datetime", version = "0.5.0" }
kotlinx-serialization = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version = "1.6.2" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
compose = { id = "org.jetbrains.compose", version.ref = "compose" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
"""

SETTINGS_GRADLE = """rootProject.name = "sonet-kmp"
include(":composeApp", ":shared")
"""

ROOT_BUILD_GRADLE = """plugins {
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.compose) apply false
    alias(libs.plugins.sqldelight) apply false
}
"""

GRADLE_PROPERTIES = """kotlin.code.style=official
kotlin.mpp.stability.nowarn=true
android.useAndroidX=true
android.nonTransitiveRClass=true
org.jetbrains.compose.experimental.wasm.enabled=true
"""

SHARED_BUILD = """plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.sqldelight)
}

kotlin {
    androidTarget()
    jvm("desktop")
    wasmJs { browser() }
    
    sourceSets {
        commonMain.dependencies {
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.json)
            implementation(libs.ktor.client.logging)
            implementation(libs.koin.core)
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.datetime)
            implementation(libs.kotlinx.serialization)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
            implementation(libs.sqldelight.driver.android)
            implementation(libs.koin.android)
        }
        val desktopMain by getting {
            dependencies {
                implementation(libs.ktor.client.okhttp)
                implementation(libs.sqldelight.driver.sqlite)
            }
        }
        val wasmJsMain by getting {
            dependencies {
                implementation(libs.ktor.client.js)
                implementation(libs.sqldelight.driver.js)
            }
        }
    }
}

android {
    namespace = "com.sonet.shared"
    compileSdk = 34
    defaultConfig { minSdk = 24 }
}

sqldelight {
    databases {
        create("SonetDatabase") {
            packageName.set("com.sonet.database")
        }
    }
}
"""

COMPOSE_BUILD = """plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.application)
    alias(libs.plugins.compose)
}

kotlin {
    androidTarget()
    jvm("desktop")
    wasmJs { browser() }
    
    sourceSets {
        commonMain.dependencies {
            implementation(project(":shared"))
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
            implementation(libs.koin.core)
            implementation(libs.kotlinx.coroutines.core)
        }
        androidMain.dependencies {
            implementation(libs.koin.android)
        }
    }
}

android {
    namespace = "com.sonet"
    compileSdk = 34
    defaultConfig {
        applicationId = "com.sonet"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.sonet.MainKt"
    }
}
"""

BOO_MODEL = """package com.sonet.domain.model
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
"""

HTTP_CLIENT = """package com.sonet.network
import io.ktor.client.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*

object HttpClientFactory {
    fun create(): HttpClient = HttpClient {
        install(ContentNegotiation) { json() }
    }
}
"""

SQL_SCHEMA = """CREATE TABLE BooEntity (
    id TEXT PRIMARY KEY NOT NULL,
    userId TEXT NOT NULL,
    content TEXT NOT NULL,
    createdAt INTEGER NOT NULL
);

selectAll: SELECT * FROM BooEntity;
selectById: SELECT * FROM BooEntity WHERE id = ?;
insert: INSERT OR REPLACE INTO BooEntity VALUES ?;
"""

APP_KT = """package com.sonet
import androidx.compose.material3.*
import androidx.compose.runtime.Composable

@Composable
fun App() {
    MaterialTheme {
        Surface {
            Text("Sonet")
        }
    }
}
"""

MAIN_ACTIVITY = """package com.sonet
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { App() }
    }
}
"""

DESKTOP_MAIN = """package com.sonet
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application

fun main() = application {
    Window(onCloseRequest = ::exitApplication, title = "Sonet") {
        App()
    }
}
"""

WEB_MAIN = """package com.sonet
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.window.CanvasBasedWindow

@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    CanvasBasedWindow("Sonet") { App() }
}
"""

def create_file(path, content):
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def main():
    print("🚀 Scaffolding Sonet KMP + CMP project...")
    
    create_dir(PROJECT_NAME)
    os.chdir(PROJECT_NAME)
    
    create_file("settings.gradle.kts", SETTINGS_GRADLE)
    create_file("build.gradle.kts", ROOT_BUILD_GRADLE)
    create_file("gradle.properties", GRADLE_PROPERTIES)
    create_file("gradle/libs.versions.toml", GRADLE_VERSIONS)
    
    shared_dirs = [
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/model",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/boo",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/feed",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/user",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/auth",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/messages",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/repository",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/repository",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/remote/api",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/remote/dto",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/remote/mapper",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/local/database",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/local/cache",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/export",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/network",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/util",
        f"shared/src/commonMain/sqldelight/{PACKAGE_PATH}/database",
        f"shared/src/androidMain/kotlin/{PACKAGE_PATH}",
        f"shared/src/desktopMain/kotlin/{PACKAGE_PATH}",
        f"shared/src/wasmJsMain/kotlin/{PACKAGE_PATH}",
    ]
    
    for d in shared_dirs:
        create_dir(d)
    
    create_file("shared/build.gradle.kts", SHARED_BUILD)
    create_file(f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/model/Boo.kt", BOO_MODEL)
    create_file(f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/network/HttpClient.kt", HTTP_CLIENT)
    create_file(f"shared/src/commonMain/sqldelight/{PACKAGE_PATH}/database/Boo.sq", SQL_SCHEMA)
    
    compose_dirs = [
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/di",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/theme",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/components",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/navigation",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/auth",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/feed",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/explore",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/profile",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/messages",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/export",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/utils",
        f"composeApp/src/androidMain/kotlin/{PACKAGE_PATH}",
        f"composeApp/src/desktopMain/kotlin/{PACKAGE_PATH}",
        f"composeApp/src/wasmJsMain/kotlin/{PACKAGE_PATH}",
    ]
    
    for d in compose_dirs:
        create_dir(d)
    
    create_file("composeApp/build.gradle.kts", COMPOSE_BUILD)
    create_file(f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/App.kt", APP_KT)
    create_file(f"composeApp/src/androidMain/kotlin/{PACKAGE_PATH}/MainActivity.kt", MAIN_ACTIVITY)
    create_file(f"composeApp/src/desktopMain/kotlin/{PACKAGE_PATH}/main.kt", DESKTOP_MAIN)
    create_file(f"composeApp/src/wasmJsMain/kotlin/{PACKAGE_PATH}/main.kt", WEB_MAIN)
    
    print("✅ Project scaffolded successfully!")
    print(f"📂 Navigate to {PROJECT_NAME}")
    print("🏗️  Run: ./gradlew build")

if __name__ == "__main__":
    main()
