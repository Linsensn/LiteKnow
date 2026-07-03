const app = getApp();

Page({
  data: {
    showLoginPopup: false, // 控制弹窗显示
    tempAvatar: '',
    tempNickName: ''
  },

  onShow() {
    // 每次进入首页，检查登录状态
    if (!app.globalData.isLoggedIn) {
      this.setData({
        showLoginPopup: true,
        tempAvatar: app.globalData.userInfo.avatarUrl
      });
    }
  },

  // 获取头像
  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  // 获取/输入昵称
  onInputChange(e) {
    this.setData({ tempNickName: e.detail.value });
  },

  // 确认登录
  confirmLogin() {
    if (!this.data.tempNickName) {
      wx.showToast({ title: '请输入昵称', icon: 'none' });
      return;
    }
    // 保存到全局状态
    app.globalData.userInfo = {
      avatarUrl: this.data.tempAvatar,
      nickName: this.data.tempNickName
    };
    app.globalData.isLoggedIn = true;
    
    // 关闭弹窗
    this.setData({ showLoginPopup: false });
    wx.showToast({ title: '登录成功', icon: 'success' });
  },

  // 页面跳转拦截
  navigateTo(e) {
    if (!app.globalData.isLoggedIn) {
      this.setData({ showLoginPopup: true });
      return;
    }
    wx.navigateTo({ url: e.currentTarget.dataset.url });
  }
})
