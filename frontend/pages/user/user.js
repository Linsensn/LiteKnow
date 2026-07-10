const app = getApp();

Page({
  data: { 
    userInfo: {}
  },
  
  onShow() {
    // 强制同步：每次页面显示都读取最新的全局 userInfo
    this.setData({ 
      userInfo: app.globalData.userInfo 
    });
  },

  goToEditProfile() {
    if (!app.globalData.isLoggedIn) {
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    wx.navigateTo({ url: '/pages/profileEdit/profileEdit' });
  },

  navigateTo(e) {
    if (!app.globalData.isLoggedIn) {
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    wx.navigateTo({ url: e.currentTarget.dataset.url });
  }
})