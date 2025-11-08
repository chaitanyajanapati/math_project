# Math AI Question Generator - User Guide

## 🚀 Quick Start for Users

### Prerequisites

Before running the application, you need:

1. **Python 3.9 or higher** - [Download here](https://www.python.org/downloads/)
2. **Node.js 18 or higher** - [Download here](https://nodejs.org/)
3. **Ollama** (for AI features) - [Download here](https://ollama.ai/)

### Installation Steps

#### Step 1: Install Ollama and Download Model

```bash
# Install Ollama from https://ollama.ai/
# Then download the phi model:
ollama pull phi
```

#### Step 2: Set Up Backend (Python)

```bash
# Navigate to backend directory
cd mathai_backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be running at: http://localhost:8000

#### Step 3: Set Up Frontend (React)

Open a new terminal:

```bash
# Navigate to frontend directory
cd mathai_frontend

# Install Node.js dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will be running at: http://localhost:5173

#### Step 4: Open in Browser

Open your web browser and go to: **http://localhost:5173**

---

## 🎯 How to Use

### 1. Generate Questions

1. **Select Grade Level** (1-12)
2. **Choose Difficulty** (Easy, Medium, Hard)
3. **Pick a Topic**:
   - Algebra
   - Geometry
   - Arithmetic
   - Statistics
   - Probability
   - Trigonometry
   - Number Theory
   - Calculus
4. **Select Question Type**:
   - **Open-ended**: Type your answer
   - **Multiple Choice**: Select from 4 options
5. Click **"Generate Question"**

### 2. Answer Questions

- **For Open-ended**: Type your answer in the text box
- **For Multiple Choice**: Click on one of the radio button options
- Click **"Submit Answer"** to check if you're correct

### 3. Get Help

- Click **"Get Hint"** for a helpful tip (doesn't reveal the answer)
- Click **"Get Solution"** to see the complete step-by-step solution

---

## 🛠️ Troubleshooting

### Backend Not Starting?

```bash
# Make sure you're in the backend directory
cd mathai_backend

# Check if Python is installed
python --version

# Install dependencies again
pip install -r requirements.txt

# Try starting with explicit Python version
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Not Starting?

```bash
# Make sure you're in the frontend directory
cd mathai_frontend

# Check if Node.js is installed
node --version
npm --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Start again
npm run dev
```

### Port Already in Use?

**Backend (Port 8000):**
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (Port 5173):**
```bash
# Linux/Mac
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Ollama Connection Issues?

```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve

# Download the model if missing
ollama pull phi
```

---

## 📦 Features

### Question Generation
- **8 Math Topics** covering K-12 curriculum
- **613 Question Templates** for variety
- **Difficulty Scaling** by grade level
- **AI-powered** generation with phi model

### Question Types
- **Open-ended**: Practice with free-form answers
- **Multiple Choice**: Test with realistic distractors based on common mistakes

### Learning Support
- **Smart Hints**: Get help without seeing the answer
- **Step-by-Step Solutions**: Understand the complete solving process
- **Instant Feedback**: Know immediately if your answer is correct
- **Progressive Hints**: Additional hints for multiple attempts

### Adaptive Features
- **Complexity Scoring**: Questions matched to grade level
- **Common Mistake Distractors**: Learn from typical errors
- **Multiple Answer Formats**: Fractions, decimals, mixed numbers accepted

---

## 🔍 Technical Details

### Architecture
- **Backend**: FastAPI (Python) - REST API
- **Frontend**: React 19 + Vite + TypeScript
- **AI Model**: Ollama with phi model
- **Storage**: JSON file-based database

### API Endpoints
- `POST /api/generate-question` - Generate new question
- `POST /api/questions/{id}/hint` - Get hint
- `POST /api/questions/{id}/solution` - Get solution
- `POST /api/submit-answer` - Submit and validate answer

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console (F12) for errors
3. Check terminal output for error messages
4. Ensure all prerequisites are installed

---

## 🎓 Educational Use

This tool is designed for:
- **Students**: Practice math problems at your level
- **Teachers**: Generate questions for assignments
- **Parents**: Help children with homework
- **Self-learners**: Improve math skills independently

---

## ⚙️ Advanced Configuration

### Change Backend Port
Edit `mathai_backend/main.py` or start with:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Then update `mathai_frontend/src/config.ts`:
```typescript
export const API_BASE_URL = 'http://localhost:8080';
```

### Change Frontend Port
Edit `mathai_frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3000
  }
})
```

### Use Different AI Model
Edit `mathai_ai_models/generate_math_question.py`:
```python
# Change line 393 from "phi" to another model
ollama pull llama2  # Download model first
```

---

## 🔄 Updating the App

```bash
# Pull latest changes
git pull origin main

# Update backend dependencies
cd mathai_backend
pip install -r requirements.txt

# Update frontend dependencies
cd ../mathai_frontend
npm install

# Restart both servers
```

---

**Version**: 1.0.0  
**Last Updated**: November 2025
