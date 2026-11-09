"""
智游山城 · AI 交通出行助手 —— 后端 API
启动：  python main.py        （默认 http://127.0.0.1:8000）
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import ai_advisor
import traffic_model as tm
from route_planner import Planner

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FRONTEND = ROOT / "frontend"


def _load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


attractions = _load("attractions.json")
edges = _load("edges.json")
knowledge = _load("knowledge.json")
planner = Planner(attractions, edges)

app = FastAPI(title="智游山城 AI 交通出行助手", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class PlanRequest(BaseModel):
    start: str
    poi_ids: list[str]
    start_time: str  # "HH:MM"
    weather: str = "sunny"
    day: str | None = None  # "YYYY-MM-DD"，缺省今天


class ChatRequest(BaseModel):
    question: str
    weather: str = "sunny"


def _parse_dt(day: str | None, hhmm: str) -> datetime:
    try:
        if day:
            base = datetime.strptime(day, "%Y-%m-%d")
        else:
            base = datetime.now()
        h, m = hhmm.split(":")
        return base.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
    except ValueError:
        raise HTTPException(400, "时间格式应为 HH:MM，日期为 YYYY-MM-DD")


@app.get("/api/attractions")
def get_attractions():
    return attractions


@app.get("/api/edges")
def get_edges():
    return edges


@app.get("/api/traffic")
def get_traffic(day: str | None = None, hour: int = 10, weather: str = "sunny"):
    """全路段拥堵态势（热力图数据）。hour: 0-23"""
    dt = _parse_dt(day, f"{max(0, min(23, hour)):02d}:00")
    return {
        "time": dt.strftime("%Y-%m-%d %H:%M"),
        "is_holiday": tm.is_holiday(dt.date()),
        "weather": weather,
        "corridors": tm.corridor_report(edges, dt, weather),
    }


@app.post("/api/plan")
def plan_route(req: PlanRequest):
    dt = _parse_dt(req.day, req.start_time)
    if req.start not in planner.attractions:
        raise HTTPException(404, f"未知出发点: {req.start}")
    bad = [p for p in req.poi_ids if p not in planner.attractions]
    if bad:
        raise HTTPException(404, f"未知景点: {bad}")
    if not req.poi_ids:
        raise HTTPException(400, "请至少选择一个想去的景点")
    return planner.plan_trip(req.start, req.poi_ids, dt, req.weather)


@app.post("/api/chat")
def chat(req: ChatRequest):
    dt = datetime.now()
    report = tm.corridor_report(edges, dt, req.weather)
    busy = sorted(report, key=lambda r: -r["ratio"])[:3]
    ctx = "全城最堵路段: " + "; ".join(
        f"{b['name']}({b['level']}, 约{b['minutes']}分钟)" for b in busy)
    result = ai_advisor.answer(req.question, knowledge, ctx)
    result["context"] = ctx
    return result


# 静态前端（放最后注册，避免盖住 /api）
app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
