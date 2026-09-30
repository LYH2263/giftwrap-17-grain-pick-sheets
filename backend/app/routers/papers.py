from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import papers as repo

router = APIRouter()

class PaperPatch(BaseModel):
    roll_width: float

@router.get("/papers")
def list_papers(): return {"items": repo.list_papers()}

@router.patch("/papers/{pid}")
def patch_paper(pid: int, body: PaperPatch):
    if body.roll_width <= 0:
        raise HTTPException(422, "roll_width must be positive")
    if not repo.update_roll_width(pid, body.roll_width):
        raise HTTPException(404)
    return repo.get_paper(pid)
