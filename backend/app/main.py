from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, profile, forms
from app.db import engine, Base

# Create all tables (in a real app, use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ApplyPilot AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "chrome-extension://*"], # Replace with exact extension id later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(forms.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
