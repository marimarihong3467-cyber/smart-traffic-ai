const api = require("../../utils/api");

Page({
  data: {
    attractions: [],
    startId: "",
    startName: "",
    poiIds: [],
    poiOn: {},
    time: "09:00",
    plan: null,
    planning: false,
  },

  async onLoad() {
    const attractions = await api.attractions();
    const start = attractions.find((a) => a.id === "beizhan") || attractions[0];
    this.setData({
      attractions,
      startId: start.id,
      startName: start.name,
    });
  },
  onTimeChange(e) {
    this.setData({ time: e.detail.value });
  },

  pickStart(e) {
    const a = this.data.attractions[+e.detail.value];
    this.setData({ startId: a.id, startName: a.name });
  },

  togglePoi(e) {
    const id = e.currentTarget.dataset.id;
    const poiIds = this.data.poiIds.slice();
    const i = poiIds.indexOf(id);
    if (i >= 0) poiIds.splice(i, 1);
    else poiIds.push(id);
    // WXML 不保证支持 includes()，用查表对象渲染选中态
    const poiOn = {};
    poiIds.forEach((p) => (poiOn[p] = true));
    this.setData({ poiIds, poiOn });
  },

  async plan() {
    const { startId, poiIds, time } = this.data;
    if (!poiIds.length) {
      wx.showToast({ title: "请先选至少一个景点", icon: "none" });
      return;
    }
    this.setData({ planning: true, plan: null });
    try {
      const plan = await api.plan({
        start: startId,
        poi_ids: poiIds,
        start_time: time,
        weather: getApp().globalData.weather,
      });
      if (plan.detail) {
        wx.showToast({ title: String(plan.detail), icon: "none" });
      } else {
        // 逐段处理：渲染用
        plan.segments.forEach((s, idx) => {
          s.seq = idx + 1;
          const leg = s.legs[s.legs.length - 1];
          if (leg) {
            s.lastMode = leg.mode;
            s.lastKm = leg.km;
            s.lastMinutes = leg.minutes;
            s.lastRoad = leg.road;
            s.lv = leg.congestion < 1.45 ? "畅通" : leg.congestion < 2.0 ? "缓行" : leg.congestion < 2.6 ? "拥堵" : "严重拥堵";
            s.lvClass = { 畅通: "lv1", 缓行: "lv2", 拥堵: "lv3", 严重拥堵: "lv4" }[s.lv];
          }
        });
        this.setData({ plan });
      }
    } catch (err) {
      wx.showToast({ title: "后端未连接", icon: "none" });
    }
    this.setData({ planning: false });
  },
});
