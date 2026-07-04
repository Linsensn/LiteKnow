Page({
  data: {
    bankList: []
  },

  onShow() {
    this.loadBanks();
  },

  loadBanks() {
    // 纯粹地读取真实缓存数据，如果没有，就是个空数组 []
    let myBanks = wx.getStorageSync('localBankList') || [];
    
    this.setData({
      bankList: myBanks
    });
  },

  // 点击具体的题库
  // 点击具体的题库
  goToBankDetail(e) {
    const bankId = e.currentTarget.dataset.id;
    const title = e.currentTarget.dataset.title;
    
    // ✨ 核心跳转：把 id 和 title 通过 URL 参数传给详情页
    wx.navigateTo({
      url: `/pages/bankDetail/bankDetail?id=${bankId}&title=${encodeURIComponent(title)}`
    });
  },
})