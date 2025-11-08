# Deployment Options for Math AI App

## 🎯 Distribution Strategies

### Option 1: **Docker Container** (Recommended)
**Best for**: Easy deployment, cross-platform compatibility

#### Advantages:
- ✅ Single package contains everything
- ✅ Works on Windows, Mac, Linux
- ✅ No dependency installation needed
- ✅ Isolated environment

#### Implementation:

**Create `Dockerfile` in project root:**
```dockerfile
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend
COPY mathai_backend /app/mathai_backend
WORKDIR /app/mathai_backend
RUN pip install --no-cache-dir -r requirements.txt

# Copy AI models
COPY mathai_ai_models /app/mathai_ai_models

# Copy and build frontend
COPY mathai_frontend /app/mathai_frontend
WORKDIR /app/mathai_frontend
RUN npm install && npm run build

# Copy startup script
COPY docker-start.sh /app/
RUN chmod +x /app/docker-start.sh

WORKDIR /app
EXPOSE 8000 5173

CMD ["/app/docker-start.sh"]
```

**Usage:**
```bash
# Build image
docker build -t math-ai-app .

# Run container
docker run -p 8000:8000 -p 5173:5173 math-ai-app

# Or use docker-compose (easier)
docker-compose up
```

---

### Option 2: **Python Executable (PyInstaller)**
**Best for**: Windows users, standalone backend

#### Advantages:
- ✅ Single .exe file
- ✅ No Python installation needed
- ✅ Good for backend service

#### Limitations:
- ⚠️ Frontend still needs separate packaging
- ⚠️ Large file size (100-200MB)
- ⚠️ Windows-only builds require Windows

#### Implementation:

**Create `build_exe.py`:**
```python
# Install: pip install pyinstaller
import PyInstaller.__main__

PyInstaller.__main__.run([
    'mathai_backend/main.py',
    '--onefile',
    '--name=MathAIBackend',
    '--add-data=mathai_ai_models:mathai_ai_models',
    '--add-data=mathai_backend/data:data',
    '--hidden-import=uvicorn.lifespan.on',
    '--hidden-import=uvicorn.lifespan.off',
    '--hidden-import=uvicorn.protocols.websockets.auto',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.protocols.websockets.wsproto_impl',
    '--hidden-import=uvicorn.protocols.http.h11_impl',
    '--collect-all=fastapi',
    '--collect-all=pydantic',
])
```

**Build:**
```bash
python build_exe.py
# Output: dist/MathAIBackend.exe
```

---

### Option 3: **Electron App** (Full Desktop App)
**Best for**: True desktop experience, all platforms

#### Advantages:
- ✅ Real desktop application
- ✅ Contains both frontend and backend
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Auto-updates possible

#### Limitations:
- ⚠️ Large file size (150-300MB)
- ⚠️ Complex setup
- ⚠️ Requires learning Electron

#### Implementation:

**Create Electron wrapper:**
```bash
npm install electron electron-builder
```

**`electron-main.js`:**
```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let backendProcess;
let mainWindow;

function startBackend() {
  backendProcess = spawn('python', [
    path.join(__dirname, 'mathai_backend', 'main.py')
  ]);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  // Wait for backend, then load frontend
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:8000');
  }, 3000);
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  app.quit();
});
```

**Build:**
```bash
electron-builder --win --x64
```

---

### Option 4: **Web Deployment (Cloud)**
**Best for**: Wide accessibility, no installation

#### Advantages:
- ✅ Access from any device
- ✅ No installation needed
- ✅ Automatic updates
- ✅ Centralized management

#### Platforms:

**1. Heroku** (Easiest)
```bash
# Create Procfile
web: cd mathai_backend && uvicorn main:app --host=0.0.0.0 --port=${PORT}

# Deploy
heroku create math-ai-app
git push heroku main
```

**2. Vercel** (Frontend) + Railway (Backend)
```bash
# Frontend on Vercel
npm run build
vercel deploy

# Backend on Railway
# Connect GitHub repo, Railway auto-detects FastAPI
```

**3. AWS / Google Cloud / Azure**
- Use AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service

---

### Option 5: **Installer Package**
**Best for**: Traditional software distribution

#### Windows - NSIS Installer
```bash
# Install NSIS
# Create installer script with shortcuts, uninstaller
makensis installer.nsi
# Output: MathAI_Setup.exe
```

#### Mac - DMG Package
```bash
npm install electron-installer-dmg
electron-installer-dmg ./dist/Math-AI-darwin-x64.app Math-AI --out=./dist
```

#### Linux - AppImage / .deb
```bash
# AppImage
electron-builder --linux AppImage

# Debian package
electron-builder --linux deb
```

---

## 🏆 Recommended Approach

### For General Users:
**Docker + Docker Desktop**
- Download Docker Desktop
- Double-click to start
- Single command to run everything

### For Schools/Organizations:
**Web Deployment**
- Deploy to cloud
- Share URL with students
- No installation needed

### For Offline Use:
**Electron Desktop App**
- Portable .exe (Windows)
- .dmg (Mac)
- .AppImage (Linux)

---

## 🚀 Quick Start Scripts

### Windows Quick Start (`start.bat`)
```batch
@echo off
echo Starting Math AI Application...

REM Start backend
start /B python -m uvicorn mathai_backend.main:app --reload --host 0.0.0.0 --port 8000

REM Wait for backend
timeout /t 5

REM Start frontend
cd mathai_frontend
start /B npm run dev

echo Application starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
timeout /t 3
start http://localhost:5173
```

### Linux/Mac Quick Start (`start.sh`)
```bash
#!/bin/bash
echo "Starting Math AI Application..."

# Start backend in background
cd mathai_backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend
sleep 5

# Start frontend in background
cd ../mathai_frontend
npm run dev &
FRONTEND_PID=$!

echo "Application started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"

# Open browser
sleep 3
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5173
else
    xdg-open http://localhost:5173
fi

# Keep script running
wait
```

---

## 📦 Production Build

### Build Frontend for Production:
```bash
cd mathai_frontend
npm run build
# Output: dist/ folder with optimized static files
```

### Serve Frontend from Backend:
```python
# In mathai_backend/main.py
from fastapi.staticfiles import StaticFiles

# Serve built frontend
app.mount("/", StaticFiles(directory="../mathai_frontend/dist", html=True))
```

Now single backend serves everything on port 8000!

---

## 🎓 Summary

| Method | Difficulty | Size | Cross-Platform | Best For |
|--------|-----------|------|----------------|----------|
| Docker | Medium | ~500MB | ✅ Yes | Most users |
| PyInstaller | Easy | ~200MB | ⚠️ Per OS | Backend only |
| Electron | Hard | ~300MB | ✅ Yes | Desktop app |
| Web Deploy | Easy | N/A | ✅ Yes | Schools |
| Scripts | Very Easy | Small | ✅ Yes | Developers |

**Recommendation**: Start with **Docker** for ease, or **Quick Start Scripts** for simplicity.

---

## 🔧 Next Steps

1. Choose deployment method
2. Test locally first
3. Create installation guide
4. Package for target platform
5. Test on clean machine
6. Distribute to users

