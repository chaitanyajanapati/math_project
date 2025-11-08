# 🎓 Math AI Question Generator - Quick Installation Guide

## For Users (3 Simple Options)

### Option 1: Quick Start Scripts (Easiest) ⭐

**Windows Users:**
1. Double-click `start.bat`
2. Wait for servers to start
3. Browser opens automatically!

**Mac/Linux Users:**
```bash
./start.sh
```

That's it! The script installs everything automatically.

---

### Option 2: Docker (Cross-Platform)

**Prerequisites:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
# Start the app
docker-compose up

# Open browser to http://localhost:5173
```

To stop:
```bash
docker-compose down
```

---

### Option 3: Manual Installation

**Step 1: Install Prerequisites**
- Python 3.9+ from https://www.python.org/
- Node.js 18+ from https://nodejs.org/
- Ollama from https://ollama.ai/

**Step 2: Download AI Model**
```bash
ollama pull phi
```

**Step 3: Start Backend**
```bash
cd mathai_backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 4: Start Frontend** (in new terminal)
```bash
cd mathai_frontend
npm install
npm run dev
```

**Step 5: Open Browser**
Go to http://localhost:5173

---

## 📖 Full Documentation

- **USER_GUIDE.md** - Complete usage instructions
- **DEPLOYMENT_OPTIONS.md** - Advanced deployment methods
- **README.md** - Technical details

---

## 🎯 Features

✅ **8 Math Topics** - Algebra, Geometry, Arithmetic, Statistics, Probability, Trigonometry, Number Theory, Calculus  
✅ **Multiple Choice & Open-ended** questions  
✅ **Smart Hints** - Get help without seeing answers  
✅ **Step-by-Step Solutions** - Understand how to solve  
✅ **Grade Levels 1-12** - Automatically scaled difficulty  
✅ **613 Question Templates** - Diverse practice  

---

## 🆘 Need Help?

**Servers won't start?**
- Check if ports 8000 and 5173 are available
- Make sure Python and Node.js are installed
- Try running `start.bat` or `start.sh` again

**AI not working?**
- Install Ollama from https://ollama.ai/
- Run: `ollama pull phi`

**Other issues?**
- Check `backend.log` and `frontend.log` for errors
- See USER_GUIDE.md troubleshooting section

---

## 🚀 Recommended for:

- **Students**: Practice math problems
- **Teachers**: Generate assignments
- **Parents**: Help with homework
- **Self-learners**: Improve skills

---

**Made with ❤️ for math education**
