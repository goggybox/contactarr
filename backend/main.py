from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.routes.example import router as example_router
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv('.env')

# API routes
app.include_router(example_router, prefix="/api")

# front-end routes
@app.get("/")
def dashboard():
    return FileResponse("frontend/index.html")

@app.get("/connections")
def connections():
    return FileResponse("frontend/connections.html")

# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")