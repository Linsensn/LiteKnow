const util = require('../../utils/util.js');
const app = getApp();

Page({
  data: {
    tempAvatar: '',
    tempNickname: ''
  },

  onLoad() {
    // 页面加载时，把全局变量里当前的头像和昵称先填上去
    const userInfo = app.globalData.userInfo;
    if (userInfo) {
      this.setData({
        tempAvatar: userInfo.avatar_url,
        tempNickname: userInfo.nickname
      });
    }
  },

  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  onInputNickname(e) {
    this.setData({ tempNickname: e.detail.value });
  },

  async submitProfile() {
    const { tempAvatar, tempNickname } = this.data;
    
    if (!tempNickname.trim()) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '保存中...', mask: true });

    try {
      // 对接咱们后端的修改资料接口
      const updateRes = await util.request('/api/v1/student/users/me', 'PUT', {
        avatar_url: tempAvatar,
        nickname: tempNickname
      });

      // 保存成功后，同步更新小程序的全局状态
      app.globalData.userInfo.avatar_url = updateRes.avatar_url;
      app.globalData.userInfo.nickname = updateRes.nickname;

      wx.hideLoading();
      wx.showToast({ title: '保存成功', icon: 'success' });
      
      // 延迟 1 秒后自动返回上一页（“我的”页面）
      setTimeout(() => {
        wx.navigateBack();
      }, 1000);

    } catch (error) {
      wx.hideLoading();
      console.error('更新资料失败:', error);
    }
  }
})