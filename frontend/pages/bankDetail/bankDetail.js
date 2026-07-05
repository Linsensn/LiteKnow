const util = require('../../utils/util.js');

Page({
  data: {
    bankId: '',
    bankTitle: '',
    questionCount: 0,
    createDate: '--/--/--',
    completionRate: '0.0', // 真实默认值
    accuracyRate: '0.0'    // 真实默认值
  },

  onLoad(options) {
    if (options.id && options.title) {
      this.setData({
        bankId: options.id,
        bankTitle: decodeURIComponent(options.title)
      });
      
      // 页面加载时，立刻向后端请求真实的统计数据
      this.fetchBankDetail(options.id);
    }
  },

  // ✨ 补充：配置微信原生分享卡片
  onShareAppMessage() {
    return {
      title: `我分享了一个超赞的题库：【${this.data.bankTitle}】`,
      // 必须带上参数，这样好友点开卡片，就能直接看到这个题库的数据
      path: `/pages/bankDetail/bankDetail?id=${this.data.bankId}&title=${this.data.bankTitle}`,
      // imageUrl: '/assets/share-cover.png' // 还可以配一张好看的自定义封面图
    }
  },

  // ✨ 真实功能：向后端请求题库的详情和统计数据
  async fetchBankDetail(id) {
    try {
      // 替换为您实际的后端接口路由，比如 /v1/agent/bank/detail
      const res = await util.request(`/v1/agent/bank/detail?id=${id}`, 'GET');
      
      // 拿到后端真实数据后，直接渲染到界面上（这里预设了后端返回的字段名，可根据实际数据库调整）
      this.setData({
        questionCount: res.question_count || 0,
        createDate: res.created_at || '--/--/--',
        completionRate: res.completion_rate || '0.0',
        accuracyRate: res.accuracy_rate || '0.0'
      });

    } catch (error) {
      console.error('获取题库详情失败', error);
      // 如果后端没写好或者报错，就安安静静地展示 0，绝对不出现奇怪的假数据
    }
  },

  // ✨ 真实功能：点击任意练习模式，携带参数跳转到测验页面
  startPractice(e) {
    const mode = e.currentTarget.dataset.mode;
    const bankId = this.data.bankId;

    if (!bankId) return;

    // 真正跳转到咱们之前写好的“智能测验 (quiz)”页面！
    // 把当前题库的 ID 和用户选的模式（如“随机练习”）作为参数传过去
    wx.navigateTo({
      url: `/pages/quiz/quiz?bankId=${bankId}&mode=${encodeURIComponent(mode)}`
    });
  }
})