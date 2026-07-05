const util = require('../../utils/util.js')

Page({
  data: {
    inputText: '',
    summaryResult: '',
    isTyping: false
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value })
  },

  onUploadTap() {
    wx.showToast({ title: '文档解析功能开发中...', icon: 'none' })
  },

  async generateSummary() {
    if (!this.data.inputText.trim() || this.data.isTyping) return;

    this.setData({ 
      summaryResult: 'AI 正在为您提炼核心主旨...', 
      isTyping: true 
    });

    let isFirstChunk = true;

    // ✨ 极致精简：直接调用封装好的流式水管
    util.streamRequest(
      '/v1/agent/summary', 
      { content: this.data.inputText },
      (newText) => {
        if (isFirstChunk) {
          this.setData({ summaryResult: '' });
          isFirstChunk = false;
        }
        this.setData({ summaryResult: this.data.summaryResult + newText });
      },
      () => {
        this.setData({ isTyping: false });
      },
      (err) => {
        console.error('Agent请求失败', err);
        this.setData({ 
          summaryResult: '网络请求失败，请稍后重试。',
          isTyping: false 
        });
      }
    );
  },

  copyResult() {
    if (this.data.isTyping) {
      wx.showToast({ title: '请等待生成完毕', icon: 'none' });
      return;
    }
    wx.setClipboardData({
      data: this.data.summaryResult,
      success: () => { wx.showToast({ title: '已复制' }); }
    })
  }
})