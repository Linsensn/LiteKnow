const util = require('../../utils/util.js');

Page({
  data: {
    mistakesList: [],
    page: 1,
    pageSize: 20,
    keyword: '',
    hasMore: true,
    isLoading: false
  },

  // 🌟 定义一个定时器变量，用于实时搜索的防抖
  searchTimer: null, 

  onShow() {
    this.fetchMistakes(true);
  },

  // ================= 搜索相关逻辑 =================

  // 🌟 1. 实时搜索：监听输入并加入“防抖”逻辑
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });

    // 每次用户输入时，都清除上一次还没来得及发出的请求
    if (this.searchTimer) {
      clearTimeout(this.searchTimer);
    }

    // 设置新的定时器：用户停止输入 500 毫秒后，自动触发查询
    this.searchTimer = setTimeout(() => {
      this.fetchMistakes(true);
    }, 500);
  },

  // 触发搜索（兼容用户依然习惯性点击回车的情况）
  onSearch() {
    if (this.searchTimer) clearTimeout(this.searchTimer);
    this.fetchMistakes(true);
  },

  // 🌟 2. 修复：点击叉号清空搜索框
  clearSearch() {
    this.setData({ keyword: '' });
    if (this.searchTimer) clearTimeout(this.searchTimer);
    
    // 清空后自动重新拉取全部列表
    this.fetchMistakes(true);
  },

  // ================= 核心业务逻辑 =================

  // 获取错题列表
  async fetchMistakes(isRefresh = false) {
    if (this.data.isLoading) return;
    if (!isRefresh && !this.data.hasMore) return;

    this.setData({ isLoading: true });
    let currentPage = isRefresh ? 1 : this.data.page;

    try {
      const res = await util.request('/api/v1/student/wrong-questions/list', 'GET', {
        page: currentPage,
        page_size: this.data.pageSize,
        keyword: this.data.keyword.trim(), // 去除首尾空格
        sort_by: 'desc'
      });

      const newData = res.list || [];
      const total = res.total || 0;

      this.setData({
        mistakesList: isRefresh ? newData : [...this.data.mistakesList, ...newData],
        page: currentPage + 1,
        hasMore: (isRefresh ? newData.length : this.data.mistakesList.length + newData.length) < total
      });
    } catch (error) {
      console.error('获取错题失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ isLoading: false });
      wx.stopPullDownRefresh();
    }
  },

  // 标记掌握（移出错题本）
  removeMistake(e) {
    const id = e.currentTarget.dataset.id;
    const index = e.currentTarget.dataset.index;

    wx.showModal({
      title: '确认移出',
      content: '这道题您已经完全掌握了吗？移出后将不再显示。',
      confirmColor: '#07c160',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '处理中...' });
          try {
            await util.request(`/api/v1/student/wrong-questions/${id}`, 'DELETE');
            
            wx.hideLoading();
            wx.showToast({ title: '已移出错题本', icon: 'success' });
            
            // 静默删除，体验更丝滑
            const currentList = this.data.mistakesList;
            currentList.splice(index, 1);
            this.setData({ mistakesList: currentList });
            
          } catch (error) {
            wx.hideLoading();
            console.error('移除错题失败:', error);
          }
        }
      }
    });
  },

  // 跳转到详情页
  // 跳转到详情页
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    // 解除封印，直接跳转到详情页，并把这道错题的 id 传过去
    wx.navigateTo({ 
      url: `/pages/mistakeDetail/mistakeDetail?id=${id}` 
    });
  },

  onPullDownRefresh() {
    this.fetchMistakes(true);
  },

  onReachBottom() {
    this.fetchMistakes(false);
  }
})