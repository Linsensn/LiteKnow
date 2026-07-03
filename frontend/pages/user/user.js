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

  // 唤起编辑资料弹窗
  openEditPopup() {
    if (!app.globalData.isLoggedIn) {
      wx.switchTab({ url: '/pages/index/index' });
      return;
    }
    this.setData({
      showEditPopup: true,
      tempAvatar: this.data.userInfo.avatarUrl,
      tempNickName: this.data.userInfo.nickName
    });
  },

  // 关闭弹窗
  closeEditPopup() {
    this.setData({ showEditPopup: false });
  },

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
    app.globalData.userInfo = {
      avatarUrl: this.data.tempAvatar,
      nickName: this.data.tempNickName
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
  }
})