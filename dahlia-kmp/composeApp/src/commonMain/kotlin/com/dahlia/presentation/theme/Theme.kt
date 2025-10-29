package com.dahlia.presentation.theme
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
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme,
        typography = DahliaTypography,
        content = content
    )
}
