const util = require('../../utils/util.js');

Page({
  data: {
    list: [],
    contentType: 'session', // 默认选中 'session' (会话)
    page: 1,
    pageSize: 20,
    hasMore: true,
    isLoading: false
  },

  onShow() {
    this.fetchData(true);
  },

  // 切换 Tab
  switchTab(e) {
    const type = e.currentTarget.dataset.type;
    if (this.data.contentType === type) return;
    
    this.setData({
      contentType: type,
      list: [],
      page: 1,
      hasMore: true
    }, () => {
      this.fetchData(true);
    });
  },

  // 获取数据 
  async fetchData(isRefresh = false) {
    if (this.data.isLoading || (!isRefresh && !this.data.hasMore)) return;
    
    this.setData({ isLoading: true });
    let page = isRefresh ? 1 : this.data.page;

    try {
      const res = await util.request('/api/v1/student/favorites', 'GET', {
        content_type: this.data.contentType,
        page: page,
        page_size: this.data.pageSize
      });

      const newList = res.data ? res.data.list : (res.list || res || []);
      
      this.setData({
        list: isRefresh ? newList : [...this.data.list, ...newList],
        page: page + 1,
        hasMore: newList.length === this.data.pageSize,
        isLoading: false
      });
    } catch (error) {
      this.setData({ isLoading: false });
      wx.showToast({ title: '获取收藏失败', icon: 'none' });
    }
  },

  // 取消收藏
  async removeFavorite(e) {
    const id = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '提示',
      content: '确定要取消收藏吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            // 对接后端删除接口
            await util.request(`/api/v1/student/favorites/${id}`, 'DELETE');
            wx.showToast({ title: '已取消收藏', icon: 'success' });
            // 刷新列表
            this.fetchData(true);
          } catch (error) {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
        }
      }
    });
  },

  // 跳转到对应的会话或题库详情
  goToDetail(e) {
    const item = e.currentTarget.dataset.item;
    if (item.content_type === 'session') {
      // 假设会话详情页是 history（如果 history 只是列表，则需指向真实的对话页如 index 并带上 session_id）
      wx.navigateTo({ url: `/pages/index/index?session_id=${item.content_id}` });
    } else if (item.content_type === 'bank') {
      wx.navigateTo({ url: `/pages/bankDetail/bankDetail?id=${item.content_id}` });
    }
  },

  onReachBottom() {
    this.fetchData(false);
  }
})