from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.routes.tautulli import router as tautulli_router
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv('.env')

# API routes
app.include_router(tautulli_router, prefix="/backend/tautulli")

# front-end routes
@app.get("/")
def dashboard():
    return FileResponse("frontend/pages/dashboard/index.html")

@app.get("/connections")
def connections():
    return FileResponse("frontend/pages/connections/connections.html")

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")