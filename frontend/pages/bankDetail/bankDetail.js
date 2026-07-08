const util = require('../../utils/util.js');

Page({
  data: {
    bankId: null,
    bankInfo: {} // 存放当前题库数据
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ bankId: options.id });
      this.fetchBankDetail(options.id);
    }
  },

  // 获取题库详情
  // 建议在 fetchBankDetail 中对数据进行一次“别名处理”
  async fetchBankDetail(id) {
    try {
      const res = await util.request(`/api/v1/student/question-banks/${id}`, 'GET');
      
      // ✨ 修正：后端返回的是 bank_name，我们映射给 bankInfo.name
      // 这样前端 WXML 里就不用改那么多地方了
      this.setData({ 
        bankInfo: {
          ...res,
          name: res.bank_name,
          question_count: res.total_questions 
        }
      });
    } catch (e) {
      console.error('获取题库详情失败', e);
    }
  },

  // 去“题库管理”看具体的题目列表
  goToManage() {
    if (!this.data.bankId) return;
    
    // ✨ 解除封印：直接跳转到咱们刚写好的精美管理页，并把 bankId 传过去
    wx.navigateTo({ 
      url: `/pages/questionManage/questionManage?bankId=${this.data.bankId}` 
    });
  },

  // 🚀 核心：点击不同的练习卡片，发起不同的 PracticeSession
  async startPractice(e) {
    const mode = e.currentTarget.dataset.mode; // 获取点击的是哪种模式
    
    if (!this.data.bankId) return;

    wx.showLoading({ title: '准备练习中...' });

    try {
      // 1. 发起请求创建一次新的练习记录
      // 这里的参数对齐之前写的 practice_session_schemas.py
      const payload = {
        bank_id: parseInt(this.data.bankId),
        practice_mode: mode, 
        question_sequence: [] // 如果是随机/顺序，后端通常会自动生成序列，前端可以传空或由后端决定
      };

      const sessionRes = await util.request('/api/v1/student/practice-sessions', 'POST', payload);
      
      wx.hideLoading();
      
      // 2. 带着生成的 practice_session_id 去往真正的刷题页面
      wx.navigateTo({
        url: `/pages/doPractice/doPractice?sessionId=${sessionRes.id}`
      });

    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: '无法开启练习', icon: 'none' });
    }
  },

  // 分享给好友的配置
  onShareAppMessage() {
    return {
      title: `快来和我一起刷《${this.data.bankInfo.name || '这个题库'}》吧！`,
      path: `/pages/bankDetail/bankDetail?id=${this.data.bankId}`
    };
  }
})