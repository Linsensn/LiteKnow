const util = require('../../utils/util.js')

Page({
  data: {
    questionText: '',
    explainResult: '',
    isTyping: false
  },

  onLoad(options) {
    if (options.question) {
      this.setData({ questionText: decodeURIComponent(options.question) });
    }
  },

  onInput(e) {
    this.setData({ questionText: e.detail.value })
  },

  async generateExplanation() {
    if (!this.data.questionText.trim() || this.data.isTyping) return;

    this.setData({ 
      explainResult: 'AI 正在深度思考中...', 
      isTyping: true 
    });

    let isFirstChunk = true;

    // ✨ 极致精简：直接调用封装好的流式水管
    util.streamRequest(
      '/v1/agent/explain', // 接口地址
      { question: this.data.questionText }, // 发送的数据
      (newText) => { // 收到新文字的回调
        if (isFirstChunk) {
          this.setData({ explainResult: '' });
          isFirstChunk = false;
        }
        this.setData({ explainResult: this.data.explainResult + newText });
      },
      () => { // 传输结束的回调
        this.setData({ isTyping: false });
      },
      (err) => { // 报错的回调
        console.error('精讲请求失败', err);
        this.setData({ 
          explainResult: '网络请求失败，请稍后重试。',
          isTyping: false 
        });
      }
    );
  },

  askMore() {
    wx.showToast({ title: '多轮对话功能接入中...', icon: 'none' })
  },

  copyResult() {
    if (this.data.isTyping) {
      wx.showToast({ title: '请等待生成完毕', icon: 'none' });
      return;
    }
    wx.setClipboardData({
      data: this.data.explainResult,
      success: () => { wx.showToast({ title: '已复制讲解内容' }); }
    })
  }
})