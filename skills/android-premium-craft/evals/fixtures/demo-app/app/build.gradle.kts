plugins {
  id("com.android.application")
  id("org.jetbrains.kotlin.plugin.compose")
}
android {
  namespace = "com.example.demo"
  compileSdk = 36
  defaultConfig { applicationId = "com.example.demo"; minSdk = 24; targetSdk = 36; versionCode = 1; versionName = "1.0" }
  buildFeatures { compose = true }
}
dependencies {
  implementation(platform("androidx.compose:compose-bom:2024.09.00"))
  implementation("androidx.activity:activity-compose:1.10.1")
  implementation("androidx.compose.material3:material3")
  implementation("androidx.compose.material:material-icons-core")
  implementation("androidx.compose.ui:ui")
}
