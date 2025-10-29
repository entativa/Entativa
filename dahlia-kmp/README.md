# Dahlia
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
