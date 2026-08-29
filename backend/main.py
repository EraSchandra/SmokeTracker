from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.smoking_logs import router
from backend.database import Base,engine
from backend.models.smoking_log import SmokingLog

app = FastAPI(title="SmokeTracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(router)
@app.get("/")
def message():
    return{"message": "Welcome to SmokeTracker AI"}
