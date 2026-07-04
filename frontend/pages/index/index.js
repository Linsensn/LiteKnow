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

  // 获取头像 (保持不变)
  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  // 确认登录 (已改造：通过表单提交获取数据)
  // 确认登录
  confirmLogin(e) {
    const finalNickName = e.detail.value.nickname;

    if (!finalNickName) {
      wx.showToast({ title: '请输入昵称', icon: 'none' });
      return;
    }
    
    // ✨ 这里也要对齐数据库字段！
    app.globalData.userInfo = {
      avatar_url: this.data.tempAvatar,
      nickname: finalNickName
    };
    app.globalData.isLoggedIn = true;
    
    this.setData({ 
      tempNickName: finalNickName,
      showLoginPopup: false 
    });
    
    wx.showToast({ title: '登录成功', icon: 'success' });
  },

  // 页面跳转拦截 (保持不变)
  navigateTo(e) {
    if (!app.globalData.isLoggedIn) {
      this.setData({ showLoginPopup: true });
      return;
    }
    wx.navigateTo({ url: e.currentTarget.dataset.url });
  }
})