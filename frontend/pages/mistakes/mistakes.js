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

  onShow() {
    this.fetchMistakes(true);
  },

  // 搜索框输入
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  // 触发搜索
  onSearch() {
    this.fetchMistakes(true);
  },

  // 获取错题列表
  async fetchMistakes(isRefresh = false) {
    if (this.data.isLoading) return;
    if (!isRefresh && !this.data.hasMore) return;

    this.setData({ isLoading: true });
    let currentPage = isRefresh ? 1 : this.data.page;

    try {
      // ⚠️ 路径根据后端的挂载前缀调整，假设为 /api/v1/student/wrong-questions/list
      const res = await util.request('/api/v1/student/wrong-questions/list', 'GET', {
        page: currentPage,
        page_size: this.data.pageSize,
        keyword: this.data.keyword,
        sort_by: 'desc'
      });

      // 根据后端定义的 PageResult 结构，数据在 list 字段
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
            // 调用后端的单条删除接口
            await util.request(`/api/v1/student/wrong-questions/${id}`, 'DELETE');
            
            wx.hideLoading();
            wx.showToast({ title: '已移出错题本', icon: 'success' });
            
            // 前端静默删除该条数据，不需要重新请求整个列表，体验更丝滑
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

  // 跳转到详情页（以后如果有独立的详情页可以做）
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.showToast({ title: '详情页开发中', icon: 'none' });
    // wx.navigateTo({ url: `/pages/mistakeDetail/mistakeDetail?id=${id}` });
  },

  onPullDownRefresh() {
    this.fetchMistakes(true);
  },

  onReachBottom() {
    this.fetchMistakes(false);
  }
})