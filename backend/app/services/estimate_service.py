from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate, sheet_trials
from app.repositories import boxes, history, papers, settings_repo


def run_estimate(box_id: int, paper_id: int | None, overlap: float | None, wrap_style: str, save: bool, note: str):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    if paper_id is None:
        raise HTTPException(422, "paper required: estimate must bind a roll")
    paper = papers.get_paper(paper_id)
    if not paper:
        raise HTTPException(404, "paper not found")
    if float(paper["roll_width"]) <= 0:
        raise HTTPException(422, "roll_width must be positive")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    trial = sheet_trials(box["length"], box["width"], box["height"], paper["roll_width"])
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    payload = {
        **calc,
        **trial,
        "paper_id": paper["id"],
        "paper_name": paper["name"],
        "ribbon": ribbon,
        "box_id": box_id,
    }
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "paper": paper, "run_id": run_id, **payload}
