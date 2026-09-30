import math


def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def unfolded_mains(length: float, width: float, height: float) -> dict:
    """展开主尺（净几何尺寸，不含折边系数 overlap）。

    口径（自洽、可测）：盒置于纸面，纸绕盒身 W-H 截面一周，两端沿盒长方向折起盖端面。
    - dim_len 长向展开主尺 = L + 2H（顶面全长 + 两端各折起一个盒高）
    - dim_wid 宽向展开主尺 = 2*(W + H)（绕盒身一周的周长）
    """
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    return {"dim_len": round(L + 2 * H, 4), "dim_wid": round(2 * (W + H), 4)}


def sheet_trials(length: float, width: float, height: float, roll_width: float) -> dict:
    """两种卷向的 sheets 试算与择优。

    - 卷向 length：卷宽对齐长向展开主尺，sheets_len = ceil(dim_len / roll_width)
    - 卷向 width ：卷宽对齐宽向展开主尺，sheets_wid = ceil(dim_wid / roll_width)
    选用 sheets 更小者；两向相同按固定破平优先长向（grain="length"）并记 tie_break=True。
    roll_width 必须为正，否则 ValueError。
    """
    rw = float(roll_width)
    if rw <= 0:
        raise ValueError("roll_width must be positive")
    mains = unfolded_mains(length, width, height)
    sheets_len = math.ceil(mains["dim_len"] / rw)
    sheets_wid = math.ceil(mains["dim_wid"] / rw)
    tie = sheets_len == sheets_wid
    grain = "length" if sheets_len <= sheets_wid else "width"
    return {
        **mains,
        "roll_width": rw,
        "sheets_len": sheets_len,
        "sheets_wid": sheets_wid,
        "grain": grain,
        "sheets": sheets_len if grain == "length" else sheets_wid,
        "tie_break": tie,
    }


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
