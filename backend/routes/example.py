from fastapi import APIRouter
from backend.api.tautulli import get_tautulli_status
from backend.api.tvdb import get_tvdb_status

router = APIRouter()

@router.get("/status")
def status():
    return {
        "tautulli": get_tautulli_status(),
        "tvdb": get_tvdb_status()
    }
