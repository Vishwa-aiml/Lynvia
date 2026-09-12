from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health():
    return {"status": "ok"}

@router.get("/ready")
def ready():
    # simple readiness probe — can extend with DB check later
    return {"status": "ready"}
