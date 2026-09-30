import pytest
from app.engines.wrap_math import paper_area, ribbon_estimate, sheet_trials, unfolded_mains

def test_book_box():
    r = paper_area(0.30, 0.20, 0.15, 1.15)
    assert r["box_surface"] == 0.27
    assert r["paper_m2"] == 0.31

def test_ribbon_cross():
    rb = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert rb["ribbon_m"] > 0.5

def test_unfolded_mains_spec():
    # 口径：长向主尺 = L + 2H；宽向主尺 = 2*(W + H)，净几何不含折边系数
    m = unfolded_mains(0.30, 0.20, 0.15)
    assert m["dim_len"] == pytest.approx(0.60)
    assert m["dim_wid"] == pytest.approx(0.70)

def test_unfolded_mains_rejects_nonpositive():
    with pytest.raises(ValueError):
        unfolded_mains(0.3, 0.2, 0)

def test_trials_both_directions_present():
    t = sheet_trials(0.30, 0.20, 0.15, 0.65)
    assert t["sheets_len"] == 1  # ceil(0.60 / 0.65)
    assert t["sheets_wid"] == 2  # ceil(0.70 / 0.65)
    assert t["grain"] == "length"
    assert t["sheets"] == 1
    assert t["tie_break"] is False

def test_trials_width_orientation_wins():
    # 长条盒：长向主尺 1.1 > 宽向主尺 0.5，卷宽对齐宽向更省
    t = sheet_trials(1.0, 0.2, 0.05, 0.6)
    assert t["sheets_len"] == 2  # ceil(1.1 / 0.6)
    assert t["sheets_wid"] == 1  # ceil(0.5 / 0.6)
    assert t["grain"] == "width"
    assert t["sheets"] == 1
    assert t["tie_break"] is False

def test_trials_tie_break_prefers_length():
    t = sheet_trials(0.30, 0.20, 0.15, 1.0)
    assert t["sheets_len"] == t["sheets_wid"] == 1
    assert t["grain"] == "length"
    assert t["sheets"] == 1
    assert t["tie_break"] is True

@pytest.mark.parametrize("rw", [0, -0.5])
def test_trials_reject_nonpositive_roll_width(rw):
    with pytest.raises(ValueError):
        sheet_trials(0.30, 0.20, 0.15, rw)
