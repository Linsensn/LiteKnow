const util = require('../../utils/util.js');
const app = getApp();

Page({
  data: {
    tempAvatar: '',
    tempNickname: '',
    tempSignature: ''
  },

  onLoad() {
    const userInfo = app.globalData.userInfo;
    if (userInfo) {
      this.setData({
        tempAvatar: userInfo.avatar_url || '',
        tempNickname: userInfo.nickname || '',
        tempSignature: userInfo.signature || '' 
      });
    }
  },

  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  onInputNickname(e) {
    this.setData({ tempNickname: e.detail.value });
  },

  onInputSignature(e) {
    this.setData({ tempSignature: e.detail.value });
  },

  async submitProfile() {
    const { tempAvatar, tempNickname, tempSignature } = this.data;
    
    if (!tempNickname.trim()) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '保存中...', mask: true });

    try {
      // 提交到后端
      const updateRes = await util.request('/api/v1/student/users/me', 'PUT', {
        avatar_url: tempAvatar,
        nickname: tempNickname,
        signature: tempSignature 
      });

      // ✨ 关键同步：必须确保更新的是 app.globalData
      app.globalData.userInfo = {
        ...app.globalData.userInfo, // 保留其他可能存在的属性
        avatar_url: updateRes.avatar_url,
        nickname: updateRes.nickname,
        signature: updateRes.signature 
      };

      wx.hideLoading();
      wx.showToast({ title: '保存成功', icon: 'success' });
      
      setTimeout(() => {
        wx.navigateBack();
      }, 1000);

    } catch (error) {
      wx.hideLoading();
      console.error('更新资料失败:', error);
    }
  }
})