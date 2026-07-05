const app = getApp();

Page({
  data: { 
    userInfo: {},
    showEditPopup: false,
    tempAvatar: '',
    tempNickName: ''
  },
  
  onShow() {
    this.setData({ userInfo: app.globalData.userInfo });
  },

  openEditPopup() {
    if (!app.globalData.isLoggedIn) {
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    this.setData({
      showEditPopup: true,
      // ✨ 对齐数据库字段名
      tempAvatar: this.data.userInfo.avatar_url,
      tempNickName: this.data.userInfo.nickname
    });
  },

  closeEditPopup() {
    this.setData({ showEditPopup: false });
  },

  // ⚠️ 注意：这里的 e.detail.avatarUrl 是微信原生 API 传回来的固定名字，不能改！
  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  onInputChange(e) {
    this.setData({ tempNickName: e.detail.value });
  },

  // 保存修改
  saveProfile() {
    if (!this.data.tempNickName) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' });
      return;
    }
    
    // ✨ 重点：拼装成和数据库一模一样的对象格式，存入全局
    app.globalData.userInfo = {
      avatar_url: this.data.tempAvatar,
      nickname: this.data.tempNickName
    };
    
    this.setData({ 
      userInfo: app.globalData.userInfo,
      showEditPopup: false 
    });
    
    wx.showToast({ title: '保存成功', icon: 'success' });
  },

  navigateTo(e) {
    if (!app.globalData.isLoggedIn) {
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    wx.navigateTo({ url: e.currentTarget.dataset.url });
  },

  // 修改 user.js 里的绑定事件
  navigateToFavorites() {
    wx.navigateTo({ url: '/pages/favorites/favorites' });
  },
  navigateToHistory() {
    wx.navigateTo({ url: '/pages/history/history' });
  }
})