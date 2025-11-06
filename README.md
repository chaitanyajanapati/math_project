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
