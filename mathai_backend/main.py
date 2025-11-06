from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_router

app = FastAPI(title="MathAI Backend")

# --- Enable CORS for frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later to ["http://127.0.0.1:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the AI router
app.include_router(ai_router.router, prefix="/api")

# --- Root test endpoint ---
@app.get("/")
def root():
    return {"message": "MathAI backend is running!"}
