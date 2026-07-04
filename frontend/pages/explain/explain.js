const util = require('../../utils/util.js')

Page({
  data: {
    questionText: '',
    explainResult: ''
  },

  // 页面加载时触发
  onLoad(options) {
    // 接收从其他页面（如错题本）传过来的问题参数
    if (options.question) {
      this.setData({
        // 使用 decodeURIComponent 解码，防止中文或特殊符号变成乱码
        questionText: decodeURIComponent(options.question)
      });
    }
  },

  onInput(e) {
    this.setData({
      questionText: e.detail.value
    })
  },

  async generateExplanation() {
    if (!this.data.questionText.trim()) return;

    this.setData({ explainResult: '' });

    try {
      // 替换为实际的精讲 API 路由
      const res = await util.request('/v1/agent/explain', 'POST', {
        question: this.data.questionText
      });
      
      this.setData({
        explainResult: res.explanation
      });
      
    } catch (error) {
      console.error('精讲请求失败', error);
    }
  },

  // 预留的多轮对话/追问接口
  askMore() {
    wx.showToast({
      title: '多轮对话功能接入中...',
      icon: 'none'
    })
  },

  copyResult() {
    wx.setClipboardData({
      data: this.data.explainResult,
      success: () => {
        wx.showToast({ title: '已复制讲解内容' });
      }
    })
  }
})