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

  // 获取数据 (两步走：先获取文件夹，再获取内容)
  async fetchData(isRefresh = false) {
    if (this.data.isLoading || (!isRefresh && !this.data.hasMore)) return;
    
    this.setData({ isLoading: true });
    let page = isRefresh ? 1 : this.data.page;

    try {
      // 1. 获取当前类型对应的【收藏夹 ID】
      const folderRes = await util.request('/api/v1/student/favorites', 'GET', {
        content_type: this.data.contentType,
        page: 1,
        page_size: 1 // 我们只需要拿到收藏夹的壳子
      });
      
      const folders = folderRes.data ? folderRes.data.list : (folderRes.list || []);
      if (!folders || folders.length === 0) {
         this.setData({ list: [], hasMore: false, isLoading: false });
         return;
      }
      
      const folderId = folders[0].id;

      // 2. 根据收藏夹 ID，调用 /contents 接口获取里面的【具体内容】
      const contentRes = await util.request(`/api/v1/student/favorites/${folderId}/contents`, 'GET', {
        page: page,
        page_size: this.data.pageSize
      });

      const resultData = contentRes.data || contentRes;
      const newContents = resultData.contents || [];
      
      // 3. 将后端查出的具体表记录格式化为卡片需要的字段
      const formattedList = newContents.map(item => {
         return {
            id: item.id,            // 方便 key="id"
            content_id: item.id,    // 真实内容的 ID
            content_type: this.data.contentType,
            created_at: item.created_at,
            // 如果是会话展示会话标题，题库展示题库标题
            title: item.title || (this.data.contentType === 'session' ? '摘要会话' : '未命名题目')
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

  // ✨修改点：适配后端的 POST /remove 接口
  async removeFavorite(e) {
    const item = e.currentTarget.dataset.item; // 获取整个对象
    
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
      wx.navigateTo({ url: `/pages/index/index?session_id=${item.content_id}` });
    } else if (item.content_type === 'bank') {
      wx.navigateTo({ url: `/pages/bankDetail/bankDetail?id=${item.content_id}` });
    }
  },

  onReachBottom() {
    this.fetchData(false);
  }
})