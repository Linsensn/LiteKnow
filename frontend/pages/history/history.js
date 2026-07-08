const util = require('../../utils/util.js');
const app = getApp();

Page({
  data: {
    sessionList: [],     // 存放历史会话的数组
    page: 1,             // 当前页码（用于计算 skip）
    pageSize: 10,        // 每页条数（limit）
    hasMore: true,       // 是否还有更多数据
    isLoading: false     // 是否正在加载中，防止重复触发
  },

  onLoad() {
    this.fetchSessions(true); // 首次进入页面，强制刷新拉取第一页
  },

  // ✨ 核心方法：拉取真实历史数据
  async fetchSessions(isRefresh = false) {
    if (this.data.isLoading) return; 
    if (!isRefresh && !this.data.hasMore) return; 

    this.setData({ isLoading: true });

    // ✨ 修复 1：直接使用页码，不再计算 skip
    let currentPage = isRefresh ? 1 : this.data.page;

    try {
      const res = await util.request('/api/v1/student/sessions/', 'GET', {
        page: currentPage,            // 对齐后端的 page
        page_size: this.data.pageSize // 对齐后端的 page_size
      });

      // ✨ 修复 2：从后端的 PageResult 结构中提取真正的数组 list
      const newData = (res && res.list) ? res.list : []; 
      
      this.setData({
        sessionList: isRefresh ? newData : [...this.data.sessionList, ...newData],
        page: currentPage + 1,
        hasMore: newData.length === this.data.pageSize
      });

    } catch (error) {
      console.error('获取历史记录失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ isLoading: false });
      wx.stopPullDownRefresh(); 
    }
  },

  // ✨ 新增：点击历史卡片，根据任务类型跳转到对应的 AI 页面恢复上下文
  goToDetail(e) {
    const { id, type } = e.currentTarget.dataset;
    
    if (type === 'summary') {
      wx.navigateTo({ url: `/pages/summary/summary?sessionId=${id}` });
    } else if (type === 'explain') {
      wx.navigateTo({ url: `/pages/explain/explain?sessionId=${id}` });
    } else {
      wx.showToast({ title: '该任务类型暂未开放历史查看', icon: 'none' });
    }
  },

  // 小程序原生生命周期：监听用户下拉刷新动作
  onPullDownRefresh() {
    this.fetchSessions(true);
  },

  // 小程序原生生命周期：监听页面滑动到底部
  onReachBottom() {
    this.fetchSessions(false);
  }
})