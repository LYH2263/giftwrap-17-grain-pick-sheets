# 20-giftwrap（礼品包装纸）

Giftwrap — 盒体展开近似面积（含重叠余量系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4900 |
| API | http://localhost:9900 |

## 主链

盒长宽高 → 包装纸面积 → 展开示意

## 测算口径（卷向择优）

测算必须绑卷（`paper_id` 必传；未选卷或卷宽非正 → 422，不落库）。

- 展开主尺（净几何，不含折边系数 overlap）：
  - 长向展开主尺 `dim_len = L + 2H`（顶面全长 + 两端各折起一个盒高）
  - 宽向展开主尺 `dim_wid = 2 × (W + H)`（绕盒身 W-H 截面一周）
- 双向试算：`sheets_len = ⌈dim_len / roll_width⌉`（卷宽对齐长向主尺）、`sheets_wid = ⌈dim_wid / roll_width⌉`（卷宽对齐宽向主尺）。
- 择优：选 sheets 更小的卷向；两向相同固定破平优先长向（`grain="length"`）并记 `tie_break=true`。
- 落库钉：`grain`、`sheets_len`、`sheets_wid`、`sheets`、`tie_break`、`dim_len`、`dim_wid`、`roll_width`（写入时快照）、`paper_m2`。
- 落库为唯一真相：纸张页改 `roll_width` 后，用纸档列表/详情仍回放写入时口径不重择；算纸台同参干算与回看互证。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
