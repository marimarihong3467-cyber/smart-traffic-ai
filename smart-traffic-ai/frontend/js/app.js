/* ═══════════════════════════════════════════
   智游山城 · 前端交互逻辑
   ═══════════════════════════════════════════ */
"use strict";

const API = "";
const state = {
  attractions: [],
  edges: [],
  selected: [],   // 已选景点 id（有序）
  start: null,
  hour: 10,
  weather: "sunny",
};

const $ = (s) => document.querySelector(s);
const NS = "http://www.w3.org/2000/svg";

/* ── 初始化 ── */
async function init() {
  const [atts, eds] = await Promise.all([
    fetch(`${API}/api/attractions`).then((r) => r.json()),
    fetch(`${API}/api/edges`).then((r) => r.json()),
  ]);
  state.attractions = atts;
  state.edges = eds;
  state.start = atts.find((a) => a.id === "beizhan") ? "beizhan" : atts[0].id;

  renderNodes();
  renderChips();
  fillStartSelect();
  await refreshTraffic();
  bindEvents();
}

/* ── 地图：节点 ── */
function renderNodes() {
  const layer = $("#node-layer");
  layer.innerHTML = "";
  state.attractions.forEach((a) => {
    const g = document.createElementNS(NS, "g");
    g.classList.add("node-group");
    g.dataset.id = a.id;

    const dot = document.createElementNS(NS, "circle");
    dot.classList.add("node-dot");
    dot.setAttribute("cx", a.x);
    dot.setAttribute("cy", a.y);
    dot.setAttribute("r", 9);

    const label = document.createElementNS(NS, "text");
    label.classList.add("node-label");
    label.setAttribute("x", a.x + 14);
    label.setAttribute("y", a.y + 4);
    label.textContent = a.name.split("·")[0];

    g.appendChild(dot);
    g.appendChild(label);
    g.addEventListener("click", () => togglePoi(a.id));
    layer.appendChild(g);
  });
}

/* ── 地图：路段热力 ── */
function renderEdges(corridors) {
  const layer = $("#edge-layer");
  layer.innerHTML = "";
  const byId = Object.fromEntries(corridors.map((c) => [c.id, c]));

  state.edges.forEach((e) => {
    const a1 = state.attractions.find((x) => x.id === e.from);
    const a2 = state.attractions.find((x) => x.id === e.to);
    const c = byId[e.id];
    const color = levelColor(c ? c.level : "畅通");

    const path = document.createElementNS(NS, "line");
    path.classList.add("edge");
    path.setAttribute("x1", a1.x); path.setAttribute("y1", a1.y);
    path.setAttribute("x2", a2.x); path.setAttribute("y2", a2.y);
    path.setAttribute("stroke", color);

    const title = document.createElementNS(NS, "title");
    title.textContent = `${e.name} · ${e.km}km · ${c ? c.level : ""} 约${c ? c.minutes : "?"}分钟`;
    path.appendChild(title);
    layer.appendChild(path);
  });
}

function levelColor(level) {
  return { "畅通": "#2e9e6b", "缓行": "#e8a13c", "拥堵": "#e2593b", "严重拥堵": "#b32d2d" }[level] || "#2e9e6b";
}
function levelClass(level) {
  return { "畅通": "lv1", "缓行": "lv2", "拥堵": "lv3", "严重拥堵": "lv4" }[level] || "lv1";
}

/* ── 时间轴刷新路况 ── */
async function refreshTraffic() {
  const data = await fetch(
    `${API}/api/traffic?hour=${state.hour}&weather=${state.weather}`
  ).then((r) => r.json());

  $("#clock-time").textContent = `${String(state.hour).padStart(2, "0")}:00`;
  $("#day-badge").textContent = data.is_holiday ? "节假日/周末" : "工作日";
  renderEdges(data.corridors);
}

/* ── 景点选择 ── */
function togglePoi(id) {
  const i = state.selected.indexOf(id);
  if (i >= 0) state.selected.splice(i, 1);
  else state.selected.push(id);
  renderChips();
  document.querySelectorAll(".node-group").forEach((g) => {
    g.classList.toggle("selected", state.selected.includes(g.dataset.id));
  });
}

function renderChips() {
  const wrap = $("#poi-chips");
  wrap.innerHTML = "";
  state.attractions.forEach((a) => {
    const b = document.createElement("button");
    b.className = "poi-chip" + (state.selected.includes(a.id) ? " on" : "");
    b.textContent = a.name.split("·")[0];
    b.addEventListener("click", () => togglePoi(a.id));
    wrap.appendChild(b);
  });
}

function fillStartSelect() {
  const sel = $("#start-select");
  sel.innerHTML = "";
  state.attractions.forEach((a) => {
    const o = document.createElement("option");
    o.value = a.id;
    o.textContent = a.name;
    if (a.id === state.start) o.selected = true;
    sel.appendChild(o);
  });
}

/* ── 生成行程 ── */
async function planTrip() {
  const start = $("#start-select").value;
  const start_time = $("#depart-time").value || "09:00";
  const box = $("#plan-result");

  if (!state.selected.length) {
    box.innerHTML = `<div class="empty-state">请先在地图上点击至少一个景点 ⛰️</div>`;
    return;
  }
  box.innerHTML = `<div class="empty-state">AI 正在按实时拥堵推演最优顺序…</div>`;

  const resp = await fetch(`${API}/api/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, poi_ids: state.selected, start_time, weather: state.weather }),
  }).then((r) => r.json());

  if (resp.detail) {
    box.innerHTML = `<div class="empty-state">⚠️ ${resp.detail}</div>`;
    return;
  }
  renderPlan(resp);
}

function renderPlan(plan) {
  let html = `
    <div class="trip-head">
      <div>出发 <b>${plan.start_name}</b> · ${plan.depart}</div>
      <div>车上合计 <b>${plan.total_ride_minutes}</b> 分钟</div>
    </div>`;

  plan.segments.forEach((s, i) => {
    const lastLeg = s.legs[s.legs.length - 1];
    html += `
      <div class="stop-item">
        <div class="stop-seq">${i + 1}</div>
        <div>
          <div class="stop-name">${s.to_name}</div>
          <div class="stop-time">⏱ ${s.arrive} 到 → ${s.leave} 离开（游览 ${s.stay_min} 分钟）</div>
        </div>
      </div>`;
    if (lastLeg) {
      html += `
        <div class="ride-note">
          🚗 ${lastLeg.mode} · ${lastLeg.km}km · 约 ${lastLeg.minutes} 分钟<br>
          路段「${lastLeg.road}」当前 <span class="jam ${levelClass(congestionLevel(lastLeg.congestion))}">${congestionLevel(lastLeg.congestion)}</span>
        </div>`;
    }
  });

  if (plan.advice && plan.advice.length) {
    html += `<div class="advice-box"><b>错峰建议</b><br>${plan.advice.join("<br>")}</div>`;
  }
  $("#plan-result").innerHTML = html;
}

function congestionLevel(ratio) {
  return ratio < 1.45 ? "畅通" : ratio < 2.0 ? "缓行" : ratio < 2.6 ? "拥堵" : "严重拥堵";
}

/* ── AI 问答 ── */
async function ask(question) {
  const log = $("#chat-log");
  const u = document.createElement("div");
  u.className = "msg user";
  u.textContent = question;
  log.appendChild(u);

  const b = document.createElement("div");
  b.className = "msg bot";
  b.innerHTML = "思考中…";
  log.appendChild(b);
  log.scrollTop = log.scrollHeight;

  const resp = await fetch(`${API}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, weather: state.weather }),
  }).then((r) => r.json());

  const tag = resp.source === "llm" ? "大模型增强回答" : "知识库检索回答";
  b.innerHTML = `${resp.answer}<span class="src-tag">〔${tag}〕</span>`;
  log.scrollTop = log.scrollHeight;
}

/* ── 事件绑定 ── */
function bindEvents() {
  $("#hour-slider").addEventListener("input", (e) => {
    state.hour = +e.target.value;
    refreshTraffic();
  });
  document.querySelectorAll(".weather-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".weather-btn").forEach((x) => x.classList.remove("active"));
      btn.classList.add("active");
      state.weather = btn.dataset.weather;
      refreshTraffic();
    });
  });
  $("#plan-btn").addEventListener("click", planTrip);
  $("#chat-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const v = $("#chat-input").value.trim();
    if (!v) return;
    $("#chat-input").value = "";
    ask(v);
  });
  document.querySelectorAll(".chip-q").forEach((c) =>
    c.addEventListener("click", () => ask(c.textContent.trim()))
  );
  $("#start-select").addEventListener("change", (e) => (state.start = e.target.value));
}

init();
