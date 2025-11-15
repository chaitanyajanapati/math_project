# Math Project

An AI-powered math learning platform with question generation, hints, and step-by-step solutions.

## Project Structure

- `mathai_frontend/`: React + TypeScript frontend with Tailwind CSS
- `mathai_backend/`: FastAPI backend service
- `mathai_ai_models/`: LLM integration and math solution generation

## Setup

### Frontend Setup
```bash
cd mathai_frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd mathai_backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### AI Models Setup
```bash
cd mathai_ai_models
# Add model-specific setup here
```

## Features

- AI-powered math question generation
- Step-by-step solutions with explanations
- Progressive hint system
- Support for fractions, decimals, and various math topics
- Real-time answer validation

## Flutter Mobile & Desktop (Experimental)

The Flutter client (`mathai_mobile/`) provides a cross-platform interface (mobile + emerging desktop) for generating questions, viewing hints/solutions, and tracking progress.

### Android (Debug)
```bash
cd mathai_mobile
flutter pub get
flutter build apk --debug
flutter run -d <device_id_or_emulator>
```

### Linux Desktop (Debug)
Requires toolchain packages (see `mathai_mobile/INSTALL_FLUTTER.md`).
```bash
cd mathai_mobile
flutter build linux --debug
flutter run -d linux
```
WSL users: ensure GUI availability (WSLg or X server + DISPLAY export).

### Newly Scaffolded Platforms
The directories for macOS and Windows have been generated (platform scaffolding only). Building requires host OS:
- macOS desktop: Use a macOS machine with Xcode installed, then `flutter build macos` / `flutter run -d macos`.
- Windows desktop: Use a Windows machine with Visual Studio (Desktop development with C++ workload), then `flutter build windows` / `flutter run -d windows`.

### Platform Summary
| Component | Tech | Status |
|-----------|------|--------|
| Backend API | FastAPI | Stable |
| Web Frontend | React + Vite | Stable Dev |
| Flutter Mobile (Android) | Flutter | Debug build verified |
| Flutter Desktop (Linux) | Flutter | Experimental debug build |
| Flutter Desktop (macOS) | Flutter | Scaffolded (build on macOS) |
| Flutter Desktop (Windows) | Flutter | Scaffolded (build on Windows) |

For environment override when running Flutter:
```bash
flutter run --dart-define=MATHAI_BASE_URL=http://localhost:8000
```

Refer to `mathai_mobile/INSTALL_FLUTTER.md` for detailed SDK, toolchain, and troubleshooting guidance.

## Testing

### Backend Tests
Run all backend tests (unit + integration) with pytest:
```bash
cd mathai_backend
pytest -q
```
The test suite includes:
- Unit tests for math service, solver, and question quality validation.
- Integration test (`tests/test_integration_flow.py`) exercising generate-question → submit-answer → hint → solution → progress endpoints.

### Flutter Tests
Run Flutter unit/widget tests:
```bash
cd mathai_mobile
flutter test
```

Run Flutter integration tests (requires backend running on `localhost:8000`):
```bash
# Terminal 1: start backend
cd mathai_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: integration test
cd mathai_mobile
flutter test integration_test/flow_test.dart --dart-define=MATHAI_BASE_URL=http://localhost:8000
```
The integration test (`integration_test/flow_test.dart`) validates:
- Question generation UI interaction.
- Answer submission and feedback display.
- Full end-to-end flow with live backend.
