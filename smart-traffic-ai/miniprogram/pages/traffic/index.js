const api = require("../../utils/api");

Page({
  data: {
    hour: 10,
    hourLabel: "10:00",
    weather: "sunny",
    isHoliday: false,
    corridors: [],
    loading: true,
    dayTip: "",
  },

  onLoad() {
    this.refresh();
  },

  onHourChange(e) {
    const hour = +e.detail.value;
    this.setData({ hour, hourLabel: `${String(hour).padStart(2, "0")}:00` });
    this.refresh();
  },

  pickWeather(e) {
    this.setData({ weather: e.currentTarget.dataset.w });
    this.refresh();
  },

  async refresh() {
    this.setData({ loading: true });
    try {
      const d = await api.traffic(this.data.hour, this.data.weather);
      // 最堵的排前面，方便一眼看到问题
      const corridors = d.corridors
        .slice()
        .sort((a, b) => b.ratio - a.ratio)
        .map((c) => ({ ...c, lvClass: this.lvClass(c.level) }));
      this.setData({
        corridors,
        isHoliday: d.is_holiday,
        dayTip: d.is_holiday ? "节假日/周末模式（出游单峰曲线）" : "工作日模式（通勤双峰曲线）",
        loading: false,
      });
    } catch (err) {
      this.setData({ loading: false });
      wx.showToast({ title: "后端未连接，请检查 baseUrl", icon: "none" });
    }
  },

  lvClass(level) {
    return { 畅通: "lv1", 缓行: "lv2", 拥堵: "lv3", 严重拥堵: "lv4" }[level] || "lv1";
  },
});
