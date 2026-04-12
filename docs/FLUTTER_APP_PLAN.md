# 📱 Speak-Sync Flutter App - Comprehensive Development Plan

## ✅ Local Environment Status

**Flutter Setup:**
- ✅ Flutter 3.38.4 (Stable - Latest)
- ✅ Dart 3.10.3
- ✅ Android SDK 36.1.0
- ✅ Android Studio installed
- ✅ Chrome (Web support)
- ✅ Linux toolchain

**Recommendation:** ⚠️ Update to latest Flutter when available: `flutter upgrade`

---

## 🎯 App Overview

**Speak-Sync** is an AI-powered personal assistant app with:
1. **Voice Conversations** - STT, NLU, TTS integration
2. **Task Management** - Smart scheduling with AI optimization
3. **Habit Tracking** - Exercise, food, finance logging
4. **AI Chat** - Context-aware conversations with vector memory
5. **Calendar** - Event management with conflict detection

---

## 🏗️ Architecture

### **Backend Services (Already Deployed ✅)**
- Gateway: `http://210.79.128.219:3000` - Main API entry point
- Scheduler: `http://210.79.128.219:3001` - Tasks & calendar
- AI Brain: `http://210.79.128.219:8000` - AI features
- Lifestyle: `http://210.79.128.219:8001` - Habits & logs

### **App Architecture**
```
speak_sync_app/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── core/
│   │   ├── config/          # API endpoints, env
│   │   ├── di/              # Dependency injection (GetIt)
│   │   ├── network/         # HTTP client, interceptors
│   │   ├── storage/         # Secure storage, cache
│   │   ├── constants/       # App-wide constants
│   │   └── utils/           # Helpers, extensions
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/        # API, models, repos
│   │   │   ├── domain/      # Entities, use cases
│   │   │   └── presentation/ # UI, BLoC/Riverpod
│   │   ├── chat/            # AI conversations
│   │   ├── tasks/           # Task management
│   │   ├── calendar/        # Events & scheduling
│   │   ├── habits/          # Habit tracking
│   │   ├── voice/           # Voice interaction
│   │   └── profile/         # User settings
│   ├── shared/
│   │   ├── widgets/         # Reusable components
│   │   ├── models/          # Shared data models
│   │   └── theme/           # Material 3 theme
│   └── routes/              # Navigation (GoRouter)
```

---

## 📦 Flutter Packages (Latest & Stable)

### **State Management**
```yaml
# Option 1: Riverpod (Recommended - Modern & Type-safe)
flutter_riverpod: ^2.6.1
riverpod_annotation: ^2.6.1

# Option 2: BLoC (Alternative - Popular & Robust)
flutter_bloc: ^8.1.6
```

### **Networking & API**
```yaml
dio: ^5.7.0                      # HTTP client
retrofit: ^4.5.0                 # Type-safe API (optional)
retrofit_generator: ^9.1.4       # Code generation
pretty_dio_logger: ^1.4.0        # Request logging
```

### **Storage & Cache**
```yaml
flutter_secure_storage: ^9.2.2   # Secure token storage
shared_preferences: ^2.3.3       # Simple key-value
hive: ^2.2.3                     # Fast local DB
hive_flutter: ^1.1.0
```

### **Authentication & Security**
```yaml
jwt_decoder: ^2.0.1              # JWT parsing
crypto: ^3.0.6                   # Encryption
```

### **UI & Navigation**
```yaml
go_router: ^14.6.2               # Declarative routing (Material 3)
flutter_svg: ^2.0.10+1           # SVG support
cached_network_image: ^3.4.1     # Image caching
shimmer: ^3.0.0                  # Loading skeletons
lottie: ^3.2.1                   # Animations
```

### **Voice & Media**
```yaml
speech_to_text: ^7.0.0           # STT (uses platform APIs)
flutter_tts: ^4.2.0              # TTS
audio_session: ^0.1.21           # Audio management
just_audio: ^0.9.42              # Audio playback
record: ^5.1.3                   # Audio recording
permission_handler: ^11.3.1      # Runtime permissions
```

### **Date & Time**
```yaml
intl: ^0.20.2                    # Internationalization
timezone: ^0.9.4                 # Timezone handling
table_calendar: ^3.1.2           # Calendar widget
```

### **Forms & Validation**
```yaml
reactive_forms: ^17.0.1          # Form management
reactive_forms_annotations: ^5.0.0
```

### **Utilities**
```yaml
freezed: ^2.5.7                  # Code generation (models)
freezed_annotation: ^2.4.4
json_annotation: ^4.9.0
json_serializable: ^6.8.0
logger: ^2.5.0                   # Logging
connectivity_plus: ^6.1.1        # Network status
```

### **Development Tools**
```yaml
build_runner: ^2.4.13            # Code generation
flutter_launcher_icons: ^0.14.2  # App icons
flutter_native_splash: ^2.4.2    # Splash screen
very_good_analysis: ^6.0.0       # Linting rules
```

---

## 🚀 Development Phases

### **Phase 1: Foundation (Week 1)**
1. ✅ Project setup with folder structure
2. ✅ Install & configure packages
3. ✅ Setup DI (GetIt/Riverpod)
4. ✅ HTTP client with interceptors
5. ✅ Secure storage for tokens
6. ✅ Theme (Material 3 - Dynamic colors)
7. ✅ Navigation setup (GoRouter)
8. ✅ Error handling & logging

### **Phase 2: Authentication (Week 1)**
1. ✅ Login screen
2. ✅ Registration screen
3. ✅ JWT token management
4. ✅ Auto token refresh
5. ✅ Splash screen with auto-login
6. ✅ Logout functionality

### **Phase 3: Core Features (Week 2-3)**

#### **3.1 Task Management**
- ✅ Task list (with filters)
- ✅ Create/edit task
- ✅ Mark complete
- ✅ Priority badges (Eisenhower Matrix)
- ✅ Category grouping
- ✅ Task statistics dashboard

#### **3.2 Calendar & Events**
- ✅ Calendar view (table_calendar)
- ✅ Create/edit events
- ✅ Event details
- ✅ Conflict detection UI
- ✅ Smart suggestions display

#### **3.3 AI Chat**
- ✅ Chat interface
- ✅ Message bubbles
- ✅ Typing indicator
- ✅ Intent recognition display
- ✅ Context-aware responses
- ✅ Conversation history

### **Phase 4: Advanced Features (Week 3-4)**

#### **4.1 Voice Interaction**
- ✅ Voice recording UI
- ✅ STT integration
- ✅ Real-time transcription
- ✅ TTS playback
- ✅ Voice conversation mode
- ✅ Voice profiles selection

#### **4.2 Habit Tracking**
- ✅ Exercise logging
- ✅ Food diary
- ✅ Financial tracking
- ✅ Habit streak display
- ✅ Pattern analysis charts

#### **4.3 Scheduling AI**
- ✅ Conflict alerts
- ✅ Optimal time slot suggestions
- ✅ Schedule optimization
- ✅ Productivity patterns

### **Phase 5: Polish & Testing (Week 5)**
1. ✅ Loading states & error handling
2. ✅ Offline support (cache)
3. ✅ Push notifications (FCM)
4. ✅ Dark mode
5. ✅ Unit tests
6. ✅ Integration tests
7. ✅ Performance optimization

---

## 🎨 UI Design Principles

### **Material 3 (Material You)**
- Dynamic color scheme
- Elevated cards
- Filled buttons
- Modern typography
- Smooth animations

### **Key Screens**
1. **Splash Screen** - Auto-login check
2. **Auth Screens** - Login/Register with validation
3. **Home Dashboard** - Quick stats & actions
4. **Task List** - Swipe actions, filters
5. **Task Detail** - Full CRUD
6. **Calendar View** - Monthly/weekly/daily
7. **Chat Interface** - AI conversation
8. **Voice Mode** - Recording UI
9. **Habit Tracker** - Charts & logs
10. **Profile & Settings** - User preferences

---

## 🔐 Security Implementation

### **Token Management**
```dart
// Store JWT securely
final storage = FlutterSecureStorage();
await storage.write(key: 'access_token', value: token);
await storage.write(key: 'refresh_token', value: refreshToken);
```

### **Auto Token Refresh**
```dart
// Dio interceptor
if (response.statusCode == 401) {
  // Refresh token
  final newToken = await authService.refreshToken();
  // Retry original request
}
```

### **API Security**
- HTTPS only
- JWT in Authorization header
- Secure storage (Android KeyStore, iOS Keychain)
- Certificate pinning (optional)

---

## 🌐 API Integration Examples

### **1. Authentication**
```dart
// Register
POST http://210.79.128.219:3000/api/auth/register
Body: {
  "email": "user@example.com",
  "password": "Pass1234!",
  "name": "User Name"
}

// Login
POST http://210.79.128.219:3000/api/auth/login
Body: {
  "email": "user@example.com",
  "password": "Pass1234!"
}

// Response
{
  "success": true,
  "data": {
    "user": { "id": "...", "email": "...", "name": "..." },
    "tokens": {
      "accessToken": "eyJ...",
      "refreshToken": "eyJ..."
    }
  }
}
```

### **2. Tasks**
```dart
// Get tasks with filters
GET http://210.79.128.219:3000/api/scheduler/tasks?status=pending&sortBy=priority
Headers: Authorization: Bearer <JWT_TOKEN>

// Create task
POST http://210.79.128.219:3000/api/scheduler/tasks
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "title": "Morning workout",
  "description": "30 min run",
  "priority": "VI",
  "dueDate": "2025-12-15T07:00:00Z",
  "categoryId": "fitness_category_id"
}
```

### **3. AI Chat**
```dart
// Send message
POST http://210.79.128.219:3000/api/gateway/ai/chat
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "message": "Schedule a workout for tomorrow morning",
  "context": { "user_id": "user123" }
}

// Response
{
  "intent": "create_task",
  "domain": "scheduling",
  "response": "I'll schedule a workout for tomorrow morning...",
  "entities": { "date": "2025-12-14", "time": "07:00" }
}
```

### **4. Voice**
```dart
// STT - Upload audio
POST http://210.79.128.219:3000/api/gateway/ai/voice/transcribe
Headers: 
  Authorization: Bearer <JWT_TOKEN>
  Content-Type: multipart/form-data
Body: audio file

// TTS - Synthesize speech
POST http://210.79.128.219:3000/api/gateway/ai/voice/synthesize
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "text": "Hello, how can I help you today?",
  "voice": "friendly"
}
// Returns: audio/mpeg
```

### **5. Habits**
```dart
// Log exercise
POST http://210.79.128.219:3000/api/lifestyle/exercise
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "type": "running",
  "duration": 30,
  "distance": 5,
  "caloriesBurned": 250,
  "date": "2025-12-13T07:00:00Z"
}

// Analyze patterns
POST http://210.79.128.219:3000/api/gateway/habits/analyze-patterns
Headers: Authorization: Bearer <JWT_TOKEN>
Body: {
  "user_id": "user123",
  "habit_type": "exercise"
}
```

---

## 🔧 Configuration

### **API Base URLs**
```dart
// lib/core/config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://210.79.128.219:3000';
  static const String gatewayUrl = 'http://210.79.128.219:3000';
  static const String schedulerUrl = 'http://210.79.128.219:3001';
  static const String aiBrainUrl = 'http://210.79.128.219:8000';
  static const String lifestyleUrl = 'http://210.79.128.219:8001';
  
  // Recommended: Use Gateway for all requests (handles auth)
  static const String apiBaseUrl = gatewayUrl;
}
```

### **Environment Variables**
```dart
// .env (use flutter_dotenv)
API_BASE_URL=http://210.79.128.219:3000
API_TIMEOUT=30000
LOG_LEVEL=debug
```

---

## 📝 Models Example

```dart
// lib/features/auth/data/models/user_model.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';
part 'user_model.g.dart';

@freezed
class UserModel with _$UserModel {
  const factory UserModel({
    required String id,
    required String email,
    required String name,
    @Default('user') String role,
    DateTime? lastLoginAt,
  }) = _UserModel;

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);
}

@freezed
class AuthResponse with _$AuthResponse {
  const factory AuthResponse({
    required UserModel user,
    required TokenModel tokens,
  }) = _AuthResponse;

  factory AuthResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseFromJson(json);
}

@freezed
class TokenModel with _$TokenModel {
  const factory TokenModel({
    required String accessToken,
    required String refreshToken,
  }) = _TokenModel;

  factory TokenModel.fromJson(Map<String, dynamic> json) =>
      _$TokenModelFromJson(json);
}
```

---

## 🎯 Next Steps

### **Immediate Actions:**
1. ✅ **Create Flutter project**
   ```bash
   flutter create --org com.speaksync speak_sync_app
   cd speak_sync_app
   ```

2. ✅ **Add dependencies** (pubspec.yaml)
   - Copy from "Flutter Packages" section above

3. ✅ **Setup folder structure**
   - Create folders as per architecture

4. ✅ **Configure API client**
   - Setup Dio with interceptors
   - Add token management

5. ✅ **Build authentication**
   - Login/Register screens
   - Token storage

### **Development Workflow:**
1. Start backend: Already running ✅
2. Start Flutter: `flutter run`
3. Hot reload: Press `r` in terminal
4. Test on Android: Connect device or emulator
5. Test on Chrome: `flutter run -d chrome`

---

## 📊 Project Timeline

| Phase | Duration | Features |
|-------|----------|----------|
| Foundation | 3-4 days | Setup, DI, networking, theme |
| Auth | 2-3 days | Login, register, token mgmt |
| Tasks | 4-5 days | CRUD, filters, categories |
| Calendar | 3-4 days | Events, conflicts |
| AI Chat | 4-5 days | Chat UI, NLU integration |
| Voice | 4-5 days | STT, TTS, recording |
| Habits | 3-4 days | Exercise, food, finance |
| Polish | 5-7 days | Testing, optimization |
| **Total** | **28-37 days** | **Full app** |

---

## 🚨 Important Notes

### **API Rate Limits**
- ⚠️ OpenAI embedding API: Currently at quota limit
- ✅ Groq LLM: Working (used for chat)
- ✅ All other endpoints: No limits

### **Testing Tips**
- Use Gateway (port 3000) for all requests
- JWT required for all endpoints except auth
- Test user: Already created on server

### **Common Issues & Solutions**
1. **401 Unauthorized**: Token expired → Refresh token
2. **Network error**: Check server IP/port
3. **CORS**: Not an issue with Flutter (no browser)
4. **Android permissions**: Add to AndroidManifest.xml

---

## 📚 Resources

- **Flutter Docs**: https://docs.flutter.dev
- **Riverpod**: https://riverpod.dev
- **Material 3**: https://m3.material.io
- **Backend API**: Check `docs/api/` in project

---

## ✅ Ready to Start!

Your environment is **fully configured** and backend is **100% operational**. 

**Next command:**
```bash
# Create Flutter project
cd ~/AndroidStudioProjects  # or your preferred location
flutter create --org com.speaksync speak_sync_app
cd speak_sync_app
flutter run
```

Let me know when you're ready to create the project and I'll guide you step by step! 🚀
