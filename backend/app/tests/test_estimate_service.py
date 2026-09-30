import pytest
from fastapi import HTTPException

from app import seed
from app.db import connect
from app.repositories import history, papers
from app.services import estimate_service


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    return tmp_path / "test.db"


def _run_count():
    c = connect()
    try:
        return c.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        c.close()


def test_estimate_requires_paper_and_persists_nothing(fresh_db):
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, None, "cross", True, "")
    assert ei.value.status_code == 422
    assert _run_count() == 0


def test_estimate_unknown_paper_404(fresh_db):
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, 999, None, "cross", True, "")
    assert ei.value.status_code == 404
    assert _run_count() == 0


def test_estimate_rejects_nonpositive_roll_width(fresh_db):
    c = connect()
    c.execute("INSERT INTO papers(name,roll_width,data_quality,note) VALUES ('坏卷',0,'clean','')")
    c.commit()
    bad_id = c.execute("SELECT id FROM papers WHERE name='坏卷'").fetchone()["id"]
    c.close()
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, bad_id, None, "cross", True, "")
    assert ei.value.status_code == 422
    assert _run_count() == 0


def test_saved_run_pins_grain_trials_sheets_and_area(fresh_db):
    r = estimate_service.run_estimate(1, 1, None, "cross", True, "pin")
    saved = history.get_run(r["run_id"])["result"]
    # 书型盒 0.30x0.20x0.15 + 卷宽 1.0：主尺 0.6/0.7，两向各 1 张，破平优先长向
    assert saved["dim_len"] == pytest.approx(0.6)
    assert saved["dim_wid"] == pytest.approx(0.7)
    assert saved["sheets_len"] == 1
    assert saved["sheets_wid"] == 1
    assert saved["grain"] == "length"
    assert saved["sheets"] == 1
    assert saved["tie_break"] is True
    assert saved["roll_width"] == pytest.approx(1.0)
    assert saved["paper_m2"] == pytest.approx(0.31)
    assert saved["paper_id"] == 1


def test_dry_run_with_same_params_matches_persisted(fresh_db):
    r = estimate_service.run_estimate(1, 2, None, "cross", True, "")
    saved = history.get_run(r["run_id"])["result"]
    dry = estimate_service.run_estimate(1, 2, None, "cross", False, "")
    for k in ("grain", "sheets", "sheets_len", "sheets_wid", "tie_break", "dim_len", "dim_wid", "roll_width", "paper_m2"):
        assert dry[k] == saved[k]


def test_replay_consistent_and_not_reselected_after_width_change(fresh_db):
    r = estimate_service.run_estimate(1, 1, None, "cross", True, "")
    rid = r["run_id"]
    before = history.get_run(rid)["result"]
    assert papers.update_roll_width(1, 0.4)
    detail = history.get_run(rid)["result"]
    listed = [x for x in history.list_runs() if x["id"] == rid][0]["result"]
    for k in ("grain", "sheets", "sheets_len", "sheets_wid", "roll_width", "paper_m2"):
        assert detail[k] == before[k]  # 详情回放写入时口径，不按新宽重择
        assert listed[k] == before[k]  # 列表与详情两路一致
