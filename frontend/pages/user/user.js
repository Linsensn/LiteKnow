const app = getApp();

Page({
  data: { 
    userInfo: {}
  },
  
  onShow() {
    // 每次显示该页面时，自动获取最新的全局数据（比如从修改页返回时，这里会实时刷新）
    this.setData({ userInfo: app.globalData.userInfo });
  },

  // ✨ 新增：点击头像区域，跳转到独立的全屏修改页
  goToEditProfile() {
    if (!app.globalData.isLoggedIn) {
      // 没登录的话，踢回首页触发一键登录弹窗
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    // 已经登录，跳转到专属编辑页
    wx.navigateTo({ url: '/pages/profileEdit/profileEdit' });
  },

  // 列表菜单的通用跳转函数
  navigateTo(e) {
    if (!app.globalData.isLoggedIn) {
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    wx.navigateTo({ url: e.currentTarget.dataset.url });
  }
})