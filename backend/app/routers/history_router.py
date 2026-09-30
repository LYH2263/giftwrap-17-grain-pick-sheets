from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
router = APIRouter()
@router.get("/runs")
def runs(limit: int = 50): return {"items": repo.list_runs(limit)}
@router.get("/runs/{rid}")
def run_detail(rid: int):
    r = repo.get_run(rid)
    if not r: raise HTTPException(404)
    return r
