Page({
  // 页面跳转统一处理函数
  navigateTo(e) {
    const url = e.currentTarget.dataset.url;
    if (url) {
      wx.navigateTo({
        url: url,
        fail: (err) => {
          console.error('跳转失败:', err);
          wx.showToast({ title: '页面尚未开发', icon: 'none' });
        }
      });
    }
  }
})