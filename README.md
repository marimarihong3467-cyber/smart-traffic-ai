# 智游山城 · AI 交通出行助手

> 2026 川渝大学生“数智”作品设计应用技能大赛 · **人工智能+应用组** 参赛作品

面向节假日拥堵城市的 **AI 智慧出行 Web 应用**：以重庆旅游出行场景为例，融合
**大模型问答、时间依赖路径规划、轻量拥堵预测模型**，帮助游客“错峰出行、聪明看城”。

---

## ✨ 核心功能

| 模块 | 说明 | AI 技术点 |
|---|---|---|
| 🗺️ 两江四岸交互地图 | 点击景点加入行程；拖动时间轴观察 06:00–23:00 全城路况热力变化；晴/雨/雾天气切换 | 时空拥堵推演 |
| 🧭 AI 路线规划 | 输入出发点 + 多个景点 + 出发时间，输出**游览顺序、每段交通方式、到达/离开时刻、错峰建议** | 时间依赖 Dijkstra + 贪心行程编排 |
| 📈 拥堵预测模型 | 路段行程时间 = 自由流时间 × 拥堵系数（时段双峰曲线 + 节假日系数 + 天气系数 + 确定性扰动） | 轻量可解释预测模型（纯 CPU） |
| 💬 AI 出行顾问 | 自然语言问答（“洪崖洞什么时候去不堵？”），知识库检索 + 大模型增强双层架构 | RAG 检索 + LLM 可插拔降级 |

**工程亮点**：大模型未配置时自动降级为知识库检索回答 —— **答辩现场断网/无 Key 也能完整演示**。

## 🚀 快速开始

### Web 端（主演示形态）

```bash
# 环境：Python 3.10+
pip install -r requirements.txt

# 启动（前后端一体）
bash run.sh
# 或
python3 backend/main.py
```

浏览器打开 **http://127.0.0.1:8000** 即可。

### 微信小程序端

小程序端与 Web 端**共用同一套后端 API**，三个 Tab：实时路况 / AI 规划 / 出行顾问。

1. 下载并打开「微信开发者工具」，选择「导入项目」→ 选择 `miniprogram/` 目录
2. 修改 `miniprogram/app.js` 中 `baseUrl` 为后端地址（本机调试填局域网 IP，如 `http://192.168.x.x:8000`）
3. 开发者工具勾选「不校验合法域名」即可本地调试；上线时在小程序后台配置 request 合法域名
4. 后端需先启动（`bash run.sh`）

### 启用大模型增强（可选）

```bash
export LLM_API_KEY=sk-xxxx            # 切勿提交到 git
export LLM_BASE_URL=https://api.openai.com/v1   # 或任意 OpenAI 兼容网关
export LLM_MODEL=gpt-4o-mini
python3 backend/main.py
```

## 📡 API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/attractions` | 景点/枢纽数据（坐标、热度、停留时长、避坑提示） |
| GET | `/api/edges` | 路段拓扑（距离、自由流速度、基础拥堵系数） |
| GET | `/api/traffic?hour=18&weather=rain` | 指定时刻全路段拥堵态势（热力图数据） |
| POST | `/api/plan` | 行程规划：`{start, poi_ids, start_time, weather, day}` |
| POST | `/api/chat` | AI 问答：`{question, weather}` |

## 🧠 拥堵预测模型

```
路段行程时间 = 自由流时间 × congestion_ratio(edge, t, weather)

congestion_ratio = 1 + baseline(hour) × 1.35 × holiday_amp × weather_factor × (1 + noise)
```

- `baseline(hour)`：工作日双峰（08:00 / 18:00）、节假日出游单峰（10:00–17:00）两条 24h 曲线
- `holiday_amp`：路段两端景点热度 × 节假日放大（+35%）
- `weather_factor`：晴 1.00 / 多云 1.03 / 雨 1.18 / 雾 1.12（重庆多雾）
- `noise`：按 (路段, 小时) 的确定性伪随机扰动，**同一输入必得同一输出**，便于答辩复现

模型接口与真实数据训练兼容：接入高德/百度交通态势开放数据后，替换 `fit_from_records()`
即可升级为回归模型，上层 API 不变。

## 📁 目录结构

```
smart-traffic-ai/
├── data/
│   ├── attractions.json     # 13 个景点/枢纽（含 x/y 地图坐标、热度、避坑知识）
│   ├── edges.json           # 17 条路段拓扑
│   └── knowledge.json       # 14 条出行知识库（RAG 检索源）
├── backend/
│   ├── main.py              # FastAPI 入口（API + 静态前端托管）
│   ├── traffic_model.py     # 拥堵预测模型
│   ├── route_planner.py     # 时间依赖路径规划 + 行程编排
│   └── ai_advisor.py        # RAG 检索 + LLM 可插拔问答
├── frontend/
│   ├── index.html           # 交互式单页应用
│   ├── css/style.css        # 视觉系统（纸质导览 × 城市交通图风格）
│   └── js/app.js            # 地图交互 / 时间轴 / 路线规划 / AI 对话
├── miniprogram/             # 微信小程序端（与 Web 共用同一套 API）
│   ├── app.js / app.json / app.wxss
│   ├── utils/api.js         # API 封装
│   └── pages/               # traffic 路况 / plan 规划 / chat 顾问
├── docs/
│   ├── 智游山城-AI交通出行助手-演示PPT.pptx
│   └── 演示视频脚本.md       # 3 分钟分镜+旁白，照着录即可
├── tools/
│   ├── make_ppt.py          # PPT 生成脚本（可改可重跑）
│   └── qa_ppt.py            # PPT 几何 QA（越界/溢出检测）
├── requirements.txt
├── run.sh                   # 一键启动
└── README.md
```

## 🎯 赛道契合度（人工智能+应用组）

- **AI + 文旅交通**：大模型问答 + RAG + 预测模型 + 智能规划，四类 AI 能力协同
- **实用价值**：直接面向游客“怎么走不堵、什么时候去人少”的真实痛点
- **可扩展**：换一份路网数据即可移植到成都、西安等任意旅游城市
- **可落地**：前端交互完整、API 标准化，易接入小程序/公众号

> ⚠️ 免责声明：本系统路况为**模型推演数据**，仅用于作品演示；实际出行请以交管部门发布为准。
