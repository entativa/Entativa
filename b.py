#!/usr/bin/env python3

import os

PROJECT_NAME = "dahlia-kmp"
PACKAGE = "com.dahlia"
PACKAGE_PATH = "com/dahlia"

NEON_YELLOW = "#E8FF24"
LIME_GREEN = "#D4FF00"
BLACK = "#000000"
WHITE = "#FFFFFF"
GRAY_LIGHT = "#F5F5F5"
GRAY_DARK = "#1A1A1A"

GRADLE_VERSIONS = """[versions]
kotlin = "2.0.0"
compose = "1.6.0"
agp = "8.2.0"
ktor = "2.3.8"
sqldelight = "2.0.1"
koin = "3.5.3"
coroutines = "1.8.0"
coil = "3.0.0-alpha04"
voyager = "1.0.0"

[libraries]
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-logging = { module = "io.ktor:ktor-client-logging", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
sqldelight-driver-android = { module = "app.cash.sqldelight:android-driver", version.ref = "sqldelight" }
sqldelight-driver-native = { module = "app.cash.sqldelight:native-driver", version.ref = "sqldelight" }
sqldelight-driver-sqlite = { module = "app.cash.sqldelight:sqlite-driver", version.ref = "sqldelight" }
koin-core = { module = "io.insert-koin:koin-core", version.ref = "koin" }
koin-android = { module = "io.insert-koin:koin-android", version.ref = "koin" }
koin-compose = { module = "io.insert-koin:koin-compose", version = "1.1.2" }
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
kotlinx-datetime = { module = "org.jetbrains.kotlinx:kotlinx-datetime", version = "0.5.0" }
kotlinx-serialization = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version = "1.6.3" }
coil-compose = { module = "io.coil-kt.coil3:coil-compose", version.ref = "coil" }
coil-network = { module = "io.coil-kt.coil3:coil-network-ktor", version.ref = "coil" }
voyager-navigator = { module = "cafe.adriel.voyager:voyager-navigator", version.ref = "voyager" }
voyager-tab = { module = "cafe.adriel.voyager:voyager-tab-navigator", version.ref = "voyager" }
voyager-transitions = { module = "cafe.adriel.voyager:voyager-transitions", version.ref = "voyager" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
compose = { id = "org.jetbrains.compose", version.ref = "compose" }
compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
"""

SETTINGS_GRADLE = """rootProject.name = "dahlia-kmp"
include(":composeApp", ":shared")
"""

ROOT_BUILD = """plugins {
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.compose) apply false
    alias(libs.plugins.compose.compiler) apply false
    alias(libs.plugins.kotlin.serialization) apply false
    alias(libs.plugins.sqldelight) apply false
}
"""

GRADLE_PROPERTIES = """kotlin.code.style=official
kotlin.mpp.stability.nowarn=true
android.useAndroidX=true
android.nonTransitiveRClass=true
org.jetbrains.compose.experimental.uikit.enabled=true
"""

SHARED_BUILD = """plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.sqldelight)
}

kotlin {
    androidTarget()
    
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "DahliaShared"
            isStatic = true
        }
    }
    
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
        
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.driver.native)
        }
    }
}

android {
    namespace = "com.dahlia.shared"
    compileSdk = 34
    defaultConfig { minSdk = 24 }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

sqldelight {
    databases {
        create("DahliaDatabase") {
            packageName.set("com.dahlia.database")
        }
    }
}
"""

COMPOSE_BUILD = """plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.application)
    alias(libs.plugins.compose)
    alias(libs.plugins.compose.compiler)
}

kotlin {
    androidTarget()
    
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "ComposeApp"
            isStatic = true
        }
    }
    
    sourceSets {
        commonMain.dependencies {
            implementation(project(":shared"))
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
            implementation(compose.components.uiToolingPreview)
            implementation(libs.koin.core)
            implementation(libs.koin.compose)
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.coil.compose)
            implementation(libs.coil.network)
            implementation(libs.voyager.navigator)
            implementation(libs.voyager.tab)
            implementation(libs.voyager.transitions)
        }
        
        androidMain.dependencies {
            implementation(libs.koin.android)
        }
    }
}

android {
    namespace = "com.dahlia"
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.dahlia"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }
    
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
"""

THEME_KT = f"""package com.dahlia.presentation.theme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val NeonYellow = Color(0xFFE8FF24)
val LimeGreen = Color(0xFFD4FF00)
val Black = Color(0xFF000000)
val White = Color(0xFFFFFFFF)
val GrayLight = Color(0xFFF5F5F5)
val GrayDark = Color(0xFF1A1A1A)

private val LightColorScheme = lightColorScheme(
    primary = NeonYellow,
    onPrimary = Black,
    secondary = LimeGreen,
    background = White,
    surface = GrayLight,
    onSurface = Black
)

private val DarkColorScheme = darkColorScheme(
    primary = NeonYellow,
    onPrimary = Black,
    secondary = LimeGreen,
    background = Black,
    surface = GrayDark,
    onSurface = White
)

@Composable
fun DahliaTheme(
    darkTheme: Boolean = false,
    content: @Composable () -> Unit
) {{
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme,
        typography = DahliaTypography,
        content = content
    )
}}
"""

TYPOGRAPHY_KT = """package com.dahlia.presentation.theme
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val DahliaTypography = Typography(
    displayLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 57.sp,
        lineHeight = 64.sp
    ),
    headlineLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 40.sp
    ),
    titleLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    bodyLarge = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    bodyMedium = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    labelLarge = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp
    )
)
"""

POST_MODEL = """package com.dahlia.domain.model
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
"""

USER_MODEL = """package com.dahlia.domain.model
import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: String,
    val username: String,
    val displayName: String,
    val bio: String?,
    val location: String?,
    val avatarUrl: String?,
    val followerCount: Int = 0,
    val followingCount: Int = 0,
    val postCount: Int = 0,
    val isFollowing: Boolean = false
)
"""

DI_MODULE = """package com.dahlia.di
import org.koin.dsl.module

val appModule = module {
    
}

val dataModule = module {
    
}

val domainModule = module {
    
}
"""

HTTP_CLIENT = """package com.dahlia.network
import io.ktor.client.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.json.Json

object HttpClientFactory {
    fun create(): HttpClient = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                prettyPrint = true
                isLenient = true
            })
        }
        
        install(Logging) {
            logger = Logger.DEFAULT
            level = LogLevel.INFO
        }
    }
}
"""

SQL_SCHEMA = """CREATE TABLE PostEntity (
    id TEXT PRIMARY KEY NOT NULL,
    userId TEXT NOT NULL,
    username TEXT NOT NULL,
    imageUrl TEXT NOT NULL,
    caption TEXT NOT NULL,
    createdAt INTEGER NOT NULL,
    likeCount INTEGER NOT NULL DEFAULT 0,
    commentCount INTEGER NOT NULL DEFAULT 0
);

selectAll: SELECT * FROM PostEntity ORDER BY createdAt DESC;
selectById: SELECT * FROM PostEntity WHERE id = ?;
insert: INSERT OR REPLACE INTO PostEntity VALUES ?;
deleteById: DELETE FROM PostEntity WHERE id = ?;
"""

APP_KT = """package com.dahlia
import androidx.compose.runtime.Composable
import com.dahlia.presentation.theme.DahliaTheme
import com.dahlia.presentation.navigation.AppNavigation

@Composable
fun App() {
    DahliaTheme {
        AppNavigation()
    }
}
"""

MAIN_ACTIVITY = """package com.dahlia
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { App() }
    }
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
    print("🌸 Scaffolding Dahlia KMP+CMP project...")
    
    create_dir(PROJECT_NAME)
    os.chdir(PROJECT_NAME)
    
    create_file("settings.gradle.kts", SETTINGS_GRADLE)
    create_file("build.gradle.kts", ROOT_BUILD)
    create_file("gradle.properties", GRADLE_PROPERTIES)
    create_file("gradle/libs.versions.toml", GRADLE_VERSIONS)
    
    shared_dirs = [
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/model",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/auth",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/post",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/user",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/feed",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/usecase/story",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/repository",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/repository",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/remote/api",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/remote/dto",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/remote/mapper",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/local/database",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/data/local/cache",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/network",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/util",
        f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/di",
        f"shared/src/commonMain/sqldelight/{PACKAGE_PATH}/database",
        f"shared/src/androidMain/kotlin/{PACKAGE_PATH}/platform",
        f"shared/src/iosMain/kotlin/{PACKAGE_PATH}/platform",
    ]
    
    for d in shared_dirs:
        create_dir(d)
    
    create_file("shared/build.gradle.kts", SHARED_BUILD)
    create_file(f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/model/Post.kt", POST_MODEL)
    create_file(f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/domain/model/User.kt", USER_MODEL)
    create_file(f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/network/HttpClient.kt", HTTP_CLIENT)
    create_file(f"shared/src/commonMain/kotlin/{PACKAGE_PATH}/di/Modules.kt", DI_MODULE)
    create_file(f"shared/src/commonMain/sqldelight/{PACKAGE_PATH}/database/Post.sq", SQL_SCHEMA)
    
    compose_dirs = [
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/theme",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/components",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/navigation",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/auth/login",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/auth/signup",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/auth/onboarding",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/home",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/foryou",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/explore",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/profile",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/post/detail",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/post/create",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/story",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/notifications",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/messages",
        f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/utils",
        f"composeApp/src/androidMain/kotlin/{PACKAGE_PATH}",
        f"composeApp/src/androidMain/kotlin/{PACKAGE_PATH}/native/camera",
        f"composeApp/src/androidMain/kotlin/{PACKAGE_PATH}/native/gallery",
        f"composeApp/src/iosMain/kotlin/{PACKAGE_PATH}",
        f"composeApp/src/iosMain/kotlin/{PACKAGE_PATH}/native/camera",
        f"composeApp/src/iosMain/kotlin/{PACKAGE_PATH}/native/gallery",
    ]
    
    for d in compose_dirs:
        create_dir(d)
    
    create_file("composeApp/build.gradle.kts", COMPOSE_BUILD)
    create_file(f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/App.kt", APP_KT)
    create_file(f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/theme/Theme.kt", THEME_KT)
    create_file(f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/theme/Typography.kt", TYPOGRAPHY_KT)
    create_file(f"composeApp/src/androidMain/kotlin/{PACKAGE_PATH}/MainActivity.kt", MAIN_ACTIVITY)
    
    create_file(f"composeApp/src/commonMain/kotlin/{PACKAGE_PATH}/presentation/navigation/AppNavigation.kt",
                "package com.dahlia.presentation.navigation\nimport androidx.compose.runtime.Composable\n\n@Composable\nfun AppNavigation() {\n\n}")
    
    create_file(".gitignore", "*.iml\n.gradle\n.idea\nlocal.properties\nbuild/\n.DS_Store")
    
    create_file("README.md", """# Dahlia
Visual social platform with Dahlia ID authentication

## Structure
- `/shared` - Business logic, data layer, domain models
- `/composeApp` - UI layer (Compose Multiplatform)
- `/composeApp/src/androidMain/kotlin/.../native` - Android-specific native implementations
- `/composeApp/src/iosMain/kotlin/.../native` - iOS-specific native implementations

## Build
```bash
./gradlew :composeApp:assembleDebug  # Android
./gradlew :composeApp:linkDebugFrameworkIosArm64  # iOS
```

## Design System
- **Primary**: Neon Yellow (#E8FF24)
- **Secondary**: Lime Green (#D4FF00)
- **Backgrounds**: Black/White
""")
    
    print("✅ Dahlia project scaffolded successfully!")
    print(f"📂 Navigate to {PROJECT_NAME}")
    print("🎨 Color scheme: Neon Yellow + Lime Green")
    print("📱 Native folders ready for platform-specific implementations")
    print("🏗️  Run: ./gradlew build")

if __name__ == "__main__":
    main()
