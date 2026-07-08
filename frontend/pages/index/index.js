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

  // ✨ 页面跳转统一处理函数
  navigateTo(e) {
    // 从点击事件中提取 wxml 里配置的 data-url
    const url = e.currentTarget.dataset.url;
    
    if (url) {
      wx.navigateTo({
        url: url,
        fail: (err) => {
          console.error('跳转失败:', err);
          // 如果对应的页面还没在 app.json 里注册，或者文件不存在，给个友好的提示
          wx.showToast({ title: '功能开发中', icon: 'none' });
        }
      });
    }
  },

  onChooseAvatar(e) {
    this.setData({ tempAvatar: e.detail.avatarUrl });
  },

  // 接收从 input 传来的昵称值
  onInputChange(e) {
    this.setData({ tempNickName: e.detail.value });
  },

  // 完美对接后端的双步登录逻辑
  // 完美对接后端的双步登录逻辑
  handleLogin() {
    // ✨ 核心修复：增加 150ms 延迟，等待微信原生键盘的 blur 事件把昵称写进 data 中
    setTimeout(async () => {
      const { tempAvatar, tempNickName } = this.data;

      // 这时候再去检查，就能完美取到 "123" 了
      if (!tempAvatar || !tempNickName) {
        wx.showToast({ title: '请先授权头像和昵称哦', icon: 'none' });
        return;
      }

      wx.showLoading({ title: '验证身份中...', mask: true });

      wx.login({
        success: async (res) => {
          if (res.code) {
            try {
              // 【第一步】调用静默登录接口
              const loginRes = await util.request('/api/v1/student/auth/wechat', 'POST', { 
                code: res.code 
              });

              wx.setStorageSync('token', loginRes.access_token);
              
              // 【第二步】把昵称和头像传给后端
              const updateRes = await util.request('/api/v1/student/users/me', 'PUT', {
                avatar_url: tempAvatar,
                nickname: tempNickName
              });

              // 【第三步】拼装全局用户信息
              app.globalData.isLoggedIn = true;
              app.globalData.userInfo = {
                id: updateRes.id,
                nickname: updateRes.nickname,
                avatar_url: updateRes.avatar_url,
                role: loginRes.role 
              };

              this.setData({ isLoggedIn: true });
              wx.showToast({ title: '登录成功', icon: 'success' });

            } catch (error) {
              console.error('登录或更新资料失败:', error);
              wx.removeStorageSync('token'); 
            } finally {
              wx.hideLoading();
            }
          } else {
            wx.showToast({ title: '获取微信授权码失败', icon: 'none' });
          }
        }
      });
    }, 150); // ✨ 延迟 150 毫秒
  }
})