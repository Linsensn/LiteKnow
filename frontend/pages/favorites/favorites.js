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
      // 1. 获取当前类型对应的【收藏夹 ID】
      const folderRes = await util.request('/api/v1/student/favorites', 'GET', {
        content_type: this.data.contentType,
        page: 1,
        page_size: 1
      });
      
      const folders = folderRes.data ? folderRes.data.list : (folderRes.list || []);
      if (!folders || folders.length === 0) {
         this.setData({ list: [], hasMore: false, isLoading: false });
         return;
      }
      
      const folderId = folders[0].id;

      // 2. 获取具体内容
      const contentRes = await util.request(`/api/v1/student/favorites/${folderId}/contents`, 'GET', {
        page: page,
        page_size: this.data.pageSize
      });

      const resultData = contentRes.data || contentRes;
      const newContents = resultData.contents || [];
      
      // 3. 将后端查出的记录格式化
      const formattedList = newContents.map(item => {
         // 处理时间格式，把中间的 'T' 换成空格，去掉毫秒
         let timeStr = item.created_at || '';
         if (timeStr && timeStr.includes('T')) {
             timeStr = timeStr.replace('T', ' ').split('.')[0];
         }

         return {
            id: item.id,
            content_id: item.id,
            content_type: this.data.contentType,
            created_at: timeStr,
            // ✨ 重点修复：依次尝试读取 title, name, bank_name
            title: item.title || item.name || item.bank_name || (this.data.contentType === 'session' ? '摘要会话' : '未命名题库')
         }
      });

      this.setData({
        list: isRefresh ? formattedList : [...this.data.list, ...formattedList],
        page: page + 1,
        hasMore: newContents.length === this.data.pageSize,
        isLoading: false
      });

    } catch (error) {
      console.error(error);
      this.setData({ isLoading: false });
      wx.showToast({ title: '获取收藏失败', icon: 'none' });
    }
  },

  // 取消收藏
  async removeFavorite(e) {
    const item = e.currentTarget.dataset.item; 
    
    wx.showModal({
      title: '提示',
      content: '确定要取消收藏吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await util.request('/api/v1/student/favorites/remove', 'POST', {
              content_type: item.content_type,
              content_id: item.content_id
            });
            wx.showToast({ title: '已取消收藏', icon: 'success' });
            this.fetchData(true); // 刷新列表
          } catch (error) {
            wx.showToast({ title: '操作失败', icon: 'none' });
          }
        }
      }
    });
  },

  // 跳转到详情
  goToDetail(e) {
    const item = e.currentTarget.dataset.item;
    if (item.content_type === 'session') {
      wx.navigateTo({ url: `/pages/summary/summary?sessionId=${item.content_id}` });
    } else if (item.content_type === 'bank') {
      wx.navigateTo({ url: `/pages/bankDetail/bankDetail?id=${item.content_id}` });
    }
  },

  onReachBottom() {
    this.fetchData(false);
  }
})