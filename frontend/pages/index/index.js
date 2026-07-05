const util = require('../../utils/util.js');
const app = getApp();

Page({
  data: {
    isLoggedIn: false,
    tempAvatar: '',
    tempNickName: ''
  },

  // ✨ 重点修复：改成 onShow，保证每次切回首页都会刷新登录状态
  onShow() {
    this.setData({ 
      isLoggedIn: app.globalData.isLoggedIn || false 
    });
  },

  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  // 接收从 input 传来的昵称值
  onInputChange(e) {
    this.setData({ tempNickName: e.detail.value });
  },

  // 完美对接后端的双步登录逻辑
  async handleLogin() {
    const { tempAvatar, tempNickName } = this.data;

    if (!tempAvatar || !tempNickName) {
      wx.showToast({ title: '请先授权头像和昵称哦', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '验证身份中...', mask: true });

    wx.login({
      success: async (res) => {
        if (res.code) {
          try {
            // 【第一步】调用静默登录接口，换取 Token (路径前缀根据您的 fastapi 调整)
            const loginRes = await util.request('/api/v1/student/auth/wechat', 'POST', { 
              code: res.code 
            });

            // 后端返回的是 access_token，将其存入本地
            wx.setStorageSync('token', loginRes.access_token);
            
            // 【第二步】Token 已经存好，立即调用修改资料接口，把昵称和头像传给后端
            const updateRes = await util.request('/api/v1/student/users/me', 'PUT', {
              avatar_url: tempAvatar,
              nickname: tempNickName
            });

            // 【第三步】拼装全局用户信息（综合两个接口的返回值）
            app.globalData.isLoggedIn = true;
            app.globalData.userInfo = {
              id: updateRes.id,
              nickname: updateRes.nickname,
              avatar_url: updateRes.avatar_url,
              role: loginRes.role // 从登录接口拿到的角色权限
            };

            // 更新本页面状态，隐藏弹窗
            this.setData({ isLoggedIn: true });
            wx.showToast({ title: '登录成功', icon: 'success' });

          } catch (error) {
            console.error('登录或更新资料失败:', error);
            // 失败时清除可能存在的错误 Token
            wx.removeStorageSync('token'); 
          } finally {
            wx.hideLoading();
          }
        } else {
          wx.showToast({ title: '获取微信授权码失败', icon: 'none' });
        }
      }
    });
  }
})