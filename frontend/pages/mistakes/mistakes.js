const util = require('../../utils/util.js')

Page({
  data: {
    mistakesList: []
  },

  onLoad() {
    this.fetchMistakes();
  },

  // ✨ 升级：使用 async/await 和全局请求工具获取真实错题
  async fetchMistakes() {
    try {
      // 调用封装好的标准 JSON 请求，自动处理 Loading 和错误拦截
      // 假设获取错题本的接口是 GET 请求
      const res = await util.request('/v1/agent/mistakes', 'GET');
      
      // 给后端返回的每条错题加上 expanded 字段，用于控制 UI 的折叠状态
      const formattedList = res.map(item => ({
        ...item,
        expanded: false 
      }));

      this.setData({ mistakesList: formattedList });

    } catch (error) {
      console.error('获取错题本失败', error);
      // 无需写 wx.showToast，util.js 已经自动报错了
    }
  },

  // 切换展开/折叠状态 (保持不变)
  toggleExpand(e) {
    const index = e.currentTarget.dataset.index;
    const key = `mistakesList[${index}].expanded`;
    const currentState = this.data.mistakesList[index].expanded;

    this.setData({
      [key]: !currentState
    });
  },

  // 跳转到知识精讲页面进行追问 (保持不变)
  goToExplain(e) {
    const question = e.currentTarget.dataset.question;
    
    wx.navigateTo({
      url: `/pages/explain/explain?question=${encodeURIComponent(question)}`
    });
  }
})