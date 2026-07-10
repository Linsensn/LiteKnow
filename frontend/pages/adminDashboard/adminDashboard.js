// pages/adminDashboard/adminDashboard.js
const util = require('../../utils/util.js');

Page({
  data: {
    userStats: [],    // 用户角色统计
    sessionStats: [], // 会话任务统计
    isLoading: true
  },

  onLoad(options) {
    this.fetchDashboardData();
  },

  onPullDownRefresh() {
    this.fetchDashboardData().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  // 获取面板统计数据
  fetchDashboardData() {
    this.setData({ isLoading: true });
    
    const p1 = util.request('/api/v1/admin/users/data/statistics', 'GET');
    const p2 = util.request('/api/v1/admin/sessions/statistics/task_type', 'GET');

    return Promise.all([p1, p2])
      .then(([userData, sessionData]) => {
        this.setData({
          userStats: userData || [],
          sessionStats: sessionData || [],
          isLoading: false
        });
      })
      .catch(err => {
        console.error('获取统计数据失败', err);
        this.setData({ isLoading: false });
      });
  },

  // 页面跳转统一处理
  navigateTo(e) {
    const target = e.currentTarget.dataset.target;
    
    // 👇 新增拦截逻辑：提示暂未开放
    if (target === 'adminSessions' || target === 'adminAttachments') {
      wx.showToast({
        title: '该功能后续开发，敬请期待',
        icon: 'none',
        duration: 2000
      });
      return; // 拦截跳转
    }

    wx.navigateTo({
      url: `/pages/${target}/${target}`
    });
  }
});