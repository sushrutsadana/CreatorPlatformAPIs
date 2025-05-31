from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import creators

app = FastAPI(title="Creator Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(creators.router, prefix="/creators", tags=["creators"])

@app.get("/")
async def root():
    return {"message": "Creator Backend API"}
