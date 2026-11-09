"""
时间依赖路径规划 + 行程编排
============================
1. Dijkstra（时间依赖版）：边权 = 当前时刻的预测行程时间
2. 行程编排：给定 出发点 + 若干想去的景点 + 出发时间，
   输出游览顺序、每段交通方式、到达/离开时间、错峰建议。
"""
from __future__ import annotations

import heapq
import math
from datetime import datetime, timedelta

from traffic_model import edge_travel_minutes, congestion_ratio, is_holiday


class Planner:
    def __init__(self, attractions: list[dict], edges: list[dict]):
        self.attractions = {a["id"]: a for a in attractions}
        self.edges = edges
        self.adj: dict[str, list[dict]] = {a["id"]: [] for a in attractions}
        for e in edges:
            self.adj[e["from"]].append(e)
            self.adj[e["to"]].append(e)

    # ---------- 时间依赖最短路 ----------
    def shortest_path(self, src: str, dst: str, start: datetime,
                      weather: str = "sunny") -> dict | None:
        if src not in self.adj or dst not in self.adj:
            return None
        dist = {src: 0.0}
        prev: dict[str, tuple[str, dict]] = {}
        pq = [(0.0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == dst:
                break
            if d > dist.get(u, math.inf):
                continue
            t_u = start + timedelta(minutes=d)
            for e in self.adj[u]:
                v = e["to"] if e["from"] == u else e["from"]
                w = edge_travel_minutes(e, t_u, weather)
                nd = d + w
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    prev[v] = (u, e)
                    heapq.heappush(pq, (nd, v))
        if dst not in prev and dst != src:
            return None
        # 回溯
        legs = []
        cur = dst
        while cur != src:
            u, e = prev[cur]
            t_u = start + timedelta(minutes=dist[u])
            legs.append({
                "edge_id": e["id"], "road": e["name"], "from": u, "to": cur,
                "km": e["km"], "depart": t_u.strftime("%H:%M"),
                "minutes": edge_travel_minutes(e, t_u, weather),
                "mode": self._mode(e),
                "congestion": congestion_ratio(e, t_u, weather),
            })
            cur = u
        legs.reverse()
        return {"minutes": round(dist[dst], 1), "legs": legs}

    @staticmethod
    def _mode(edge: dict) -> str:
        if edge.get("metro"):
            return edge["metro"]
        return "打车/公交" if edge["km"] > 2.5 else "步行+公交"

    # ---------- 行程编排 ----------
    def plan_trip(self, start_id: str, poi_ids: list[str], start_time: datetime,
                  weather: str = "sunny") -> dict:
        remaining = [p for p in poi_ids if p != start_id]
        order: list[str] = []
        cur, cur_t = start_id, start_time
        segments = []
        total_ride = 0.0

        # 贪心：每步选择"到达时间最早"的景点（自然规避拥堵）
        while remaining:
            best = None
            for pid in remaining:
                sp = self.shortest_path(cur, pid, cur_t, weather)
                if sp is None:
                    continue
                arrive = cur_t + timedelta(minutes=sp["minutes"])
                key = (arrive, sp["minutes"])
                if best is None or key < best[0]:
                    best = (key, pid, sp, arrive)
            if best is None:
                break
            _, pid, sp, arrive = best
            stay = self.attractions[pid]["stay_min"]
            segments.append({
                "to": pid,
                "to_name": self.attractions[pid]["name"],
                "legs": sp["legs"],
                "ride_minutes": sp["minutes"],
                "arrive": arrive.strftime("%H:%M"),
                "leave": (arrive + timedelta(minutes=stay)).strftime("%H:%M"),
                "stay_min": stay,
            })
            total_ride += sp["minutes"]
            order.append(pid)
            cur, cur_t = pid, arrive + timedelta(minutes=stay)
            remaining.remove(pid)

        # 错峰建议：热门景点如果到达时刻落在 19-21 点高峰，提示可延后/提前
        advice = []
        for s in segments:
            a = self.attractions[s["to"]]
            hh = int(s["arrive"][:2])
            if a["popularity"] >= 0.75 and 19 <= hh <= 21:
                advice.append(
                    f"{a['name']}到达时间 {s['arrive']} 正值夜景人流高峰，"
                    f"建议先在附近用餐，21:30 后入场可显著减少排队。")
            if a["popularity"] >= 0.75 and 11 <= hh <= 14:
                advice.append(
                    f"{a['name']}到达时间 {s['arrive']} 处于午间高峰，"
                    f"可将游览顺序与冷门景点对调，错开 1-2 小时。")
        if is_holiday(start_time.date()):
            advice.append("今天是节假日/周末，渝中半岛热门路段全天压力较大，"
                          "建议以轨道交通为主，预留 30% 机动时间。")

        return {
            "start": start_id,
            "start_name": self.attractions[start_id]["name"],
            "depart": start_time.strftime("%H:%M"),
            "order": order,
            "segments": segments,
            "total_ride_minutes": round(total_ride, 1),
            "weather": weather,
            "advice": advice,
        }
