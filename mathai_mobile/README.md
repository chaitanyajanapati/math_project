# MathAI Mobile App (Flutter)

This directory will contain the Flutter mobile app for your Math project.

## Setup Instructions

1. Install Flutter SDK: https://docs.flutter.dev/get-started/install
2. Run `flutter create .` in this directory to initialize the project (or let Copilot scaffold it for you).
3. The app will connect to your backend at http://localhost:8000 (or your deployed backend URL).

## Features Implemented
 - Multiple-choice rendering when question_type=mcq.
 - Progress dashboard (GET /student-progress/{student_id}).
 - Configurable grade, difficulty, topic, question type selectors.

## Project Structure
```
lib/
	main.dart                # App entry, routes
	models/question.dart     # Data models for Question & AnswerResponse
	models/progress.dart     # Progress summary model
	services/api.dart        # Backend API wrapper
	screens/question_screen.dart  # UI for practicing a question
	screens/progress_screen.dart  # Progress dashboard
	config.dart              # Environment-based base URL
```

## Running
```bash
flutter pub get
flutter run  # Select emulator/device
```

Override backend URL (e.g. on device)
```bash
flutter run --dart-define=MATHAI_BASE_URL=https://your.domain
```

When using Android emulator, backend base URL maps host machine to 10.0.2.2. For iOS simulator, localhost works.
- Student authentication & real user IDs.
- Student authentication + progress dashboard (GET /student-progress/{student_id}).
- Difficulty/topic selectors on landing screen.
- Multiple choice rendering when `question_type = mcq`.
- Offline caching of last fetched question.
- Error + retry UI polish.
- Flavor config / .env style base URL override.

## Troubleshooting
| Issue | Possible Fix |
|-------|--------------|
| Emulator can’t reach backend | Confirm port forwarding & use 10.0.2.2 for Android |
| CORS errors | Add CORSMiddleware to FastAPI if not present |
| 500 on generate-question | Check backend logs; AI model path availability |

## FastAPI Endpoints Used
- POST /generate-question
- POST /submit-answer
- POST /questions/{id}/hint
- POST /questions/{id}/solution
- POST /questions/{id}/choices
- (future) GET /student-progress/{student_id}
