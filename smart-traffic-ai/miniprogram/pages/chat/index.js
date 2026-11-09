const api = require("../../utils/api");

Page({
  data: {
    messages: [
      {
        role: "bot",
        text: "你好，我是山城出行顾问 🏙️\n可以问我：洪崖洞什么时候去不堵？下雨天去哪玩？",
      },
    ],
    input: "",
    asking: false,
    quickAsks: [
      "洪崖洞什么时候去不堵？",
      "从北站去磁器口怎么走？",
      "下雨天推荐去哪？",
      "长江索道要排多久？",
    ],
  },

  onInput(e) {
    this.setData({ input: e.detail.value });
  },

  quickAsk(e) {
    this.ask(e.currentTarget.dataset.q);
  },

  onSend() {
    const q = this.data.input.trim();
    if (!q || this.data.asking) return;
    this.setData({ input: "" });
    this.ask(q);
  },

  async ask(question) {
    const messages = this.data.messages.concat({ role: "user", text: question });
    this.setData({ messages, asking: true });
    this.scrollBottom();

    // 占位"思考中"，流式体验
    const thinking = messages.concat({ role: "bot", text: "思考中…", loading: true });
    this.setData({ messages: thinking });

    try {
      const resp = await api.chat(question, getApp().globalData.weather);
      const tag = resp.source === "llm" ? "〔大模型增强回答〕" : "〔知识库检索回答〕";
      const done = messages.concat({ role: "bot", text: resp.answer, tag });
      this.setData({ messages: done });
    } catch (err) {
      const done = messages.concat({ role: "bot", text: "⚠️ 后端未连接，请检查 baseUrl 配置。" });
      this.setData({ messages: done });
    }
    this.setData({ asking: false });
    this.scrollBottom();
  },

  scrollBottom() {
    // 让最新消息可见
    wx.pageScrollTo({ scrollTop: 99999, duration: 200 });
  },
});
