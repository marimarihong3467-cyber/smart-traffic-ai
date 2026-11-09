// 统一 API 封装：与 Web 端共用同一套后端
const app = getApp();

function request(path, method, data) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.baseUrl + path,
      method,
      data,
      header: { "Content-Type": "application/json" },
      success: (res) => resolve(res.data),
      fail: reject,
    });
  });
}

module.exports = {
  traffic: (hour, weather) => request(`/api/traffic?hour=${hour}&weather=${weather}`, "GET"),
  attractions: () => request("/api/attractions", "GET"),
  plan: (payload) => request("/api/plan", "POST", payload),
  chat: (question, weather) => request("/api/chat", "POST", { question, weather }),
};
