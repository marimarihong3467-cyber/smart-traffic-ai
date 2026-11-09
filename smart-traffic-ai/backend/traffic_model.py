"""
交通拥堵预测模型（轻量、纯 CPU，无第三方 ML 依赖）
====================================================
思路：路段行程时间 = 自由流时间 × 拥堵放大系数(时段, 星期, 节假日, 天气)
放大系数由"基线曲线 + 节点热度 + 节假日系数"构成，并注入确定性噪声，
保证同一输入总是同一输出（便于演示与答辩复现）。

若后续拿到真实数据（如高德/百度交通态势开放数据），可将 fit_from_records()
替换为真实回归训练，接口保持不变。
"""
from __future__ import annotations

import math
import zlib
from datetime import datetime, date

# ---------- 基线：一天 24 小时的通勤/出游双峰曲线 ----------
# 工作日：早晚通勤双峰；节假日：白天出游单峰（10:00-17:00）
_WORKDAY_HOURLY = [
    0.28, 0.22, 0.20, 0.18, 0.20, 0.35, 0.62, 0.88,
    0.95, 0.82, 0.68, 0.72, 0.80, 0.70, 0.66, 0.74,
    0.86, 0.96, 0.92, 0.78, 0.62, 0.50, 0.40, 0.33,
]
_HOLIDAY_HOURLY = [
    0.30, 0.24, 0.20, 0.18, 0.20, 0.28, 0.42, 0.58,
    0.72, 0.86, 0.94, 0.98, 0.92, 0.88, 0.90, 0.96,
    1.00, 0.98, 0.94, 0.90, 0.86, 0.78, 0.64, 0.48,
]

WEATHER_FACTOR = {
    "sunny": 1.00,
    "cloudy": 1.03,
    "rain": 1.18,
    "fog": 1.12,   # 重庆多雾，通行效率下降
}


def _hash_noise(edge_id: str, hour: int) -> float:
    """确定性伪随机波动 [-0.05, +0.05]，模拟路段偶发扰动。"""
    h = (zlib.crc32(f"{edge_id}:{hour}".encode()) & 0xFFFF) / 65535.0
    return (h - 0.5) * 0.10


def baseline_index(hour: int, is_holiday: bool) -> float:
    table = _HOLIDAY_HOURLY if is_holiday else _WORKDAY_HOURLY
    return table[max(0, min(23, int(hour)))]


def is_holiday(d: date | None = None) -> bool:
    """演示规则：周六周日 + 法定节假日高峰（五一/国庆/元旦/春节窗口）均按节假日曲线。"""
    d = d or date.today()
    if d.weekday() >= 5:
        return True
    md = (d.month, d.day)
    holiday_window = {(5, 1), (5, 2), (5, 3), (10, 1), (10, 2), (10, 3),
                      (10, 4), (10, 5), (10, 6), (10, 7), (1, 1), (1, 2)}
    return md in holiday_window


def congestion_ratio(edge: dict, dt: datetime, weather: str = "sunny") -> float:
    """返回拥堵放大系数，范围约 [1.0, 3.2]。越大越堵。"""
    hour = dt.hour + dt.minute / 60.0
    base = baseline_index(dt.hour, is_holiday(dt.date()))

    # 节点热度：路段两端景点越热门，节假日放大越明显
    heat = float(edge.get("heat", 0.5))
    holiday_amp = 1.0 + (0.35 * heat if is_holiday(dt.date()) else 0.0)

    ratio = 1.0 + base * 1.35 * holiday_amp * WEATHER_FACTOR.get(weather, 1.0)
    ratio *= 1.0 + _hash_noise(edge["id"], dt.hour)
    return round(max(1.0, min(3.2, ratio)), 2)


def edge_travel_minutes(edge: dict, dt: datetime, weather: str = "sunny") -> float:
    free_flow = edge["km"] / edge["speed"] * 60.0  # 分钟
    return round(free_flow * congestion_ratio(edge, dt, weather), 1)


def corridor_report(edges: list[dict], dt: datetime, weather: str = "sunny") -> list[dict]:
    """全路段拥堵态势，供热力图使用。"""
    out = []
    for e in edges:
        r = congestion_ratio(e, dt, weather)
        level = "畅通" if r < 1.45 else ("缓行" if r < 2.0 else ("拥堵" if r < 2.6 else "严重拥堵"))
        out.append({
            "id": e["id"], "name": e["name"], "from": e["from"], "to": e["to"],
            "ratio": r, "minutes": edge_travel_minutes(e, dt, weather),
            "level": level,
        })
    return out
