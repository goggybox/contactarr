from pydantic import BaseModel
from fastapi import APIRouter
from backend.api import tautulli
from fastapi.responses import PlainTextResponse

router = APIRouter()

class APIModel(BaseModel):
    key: str

@router.get("/apikey")
def apikey():
    return PlainTextResponse(tautulli.apikey())

@router.post("/set_apikey")
def set_apikey(data: APIModel):
    return tautulli.set_apikey(data.key)

@router.get("/url")
def url():
    return PlainTextResponse(tautulli.url())

@router.post("/set_url")
def set_url(data: APIModel):
    return tautulli.set_url(data.key)

@router.get("/alive")
def alive():
    return tautulli.alive()

@router.get("/get_users")
def get_users():
    return tautulli.get_users()