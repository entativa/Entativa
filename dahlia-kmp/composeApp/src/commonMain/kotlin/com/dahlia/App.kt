package com.dahlia
import androidx.compose.runtime.Composable
import com.dahlia.presentation.theme.DahliaTheme
import com.dahlia.presentation.navigation.AppNavigation

@Composable
fun App() {
    DahliaTheme {
        AppNavigation()
    }
}
