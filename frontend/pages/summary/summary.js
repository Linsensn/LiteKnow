const util = require('../../utils/util.js')

Page({
  data: {
    inputText: '',
    summaryResult: ''
  },

  // 监听输入
  onInput(e) {
    this.setData({
      inputText: e.detail.value
    })
  },

  // 模拟/处理多模态上传预留接口
  onUploadTap() {
    wx.showToast({
      title: '文档解析功能开发中...',
      icon: 'none'
    })
  },

  // 调用 Agent 接口生成摘要
  async generateSummary() {
    if (!this.data.inputText.trim()) return;

    // 清空历史结果
    this.setData({ summaryResult: '' });

    try {
      // 这里的 '/v1/agent/summary' 需替换为您实际的 FastAPI 路由
      const res = await util.request('/v1/agent/summary', 'POST', {
        content: this.data.inputText
      });
      
      // 假设后端返回的数据在 res.summary 中
      this.setData({
        summaryResult: res.summary
      });
      
    } catch (error) {
      console.error('Agent请求失败', error);
      // 兜底提示在 util.request 中已处理
    }
  },

  // 复制结果到剪贴板
  copyResult() {
    wx.setClipboardData({
      data: this.data.summaryResult,
      success: () => {
        wx.showToast({ title: '已复制' });
      }
    })
  }
})