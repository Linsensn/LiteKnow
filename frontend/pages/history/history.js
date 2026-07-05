// pages/favorites/favorites.js
const util = require('../../utils/util.js');

Page({
  data: {
    list: [] // 统一叫 list
  },
  onShow() {
    this.fetchData();
  },
  async fetchData() {
    try {
      // 以后后端写好了，直接改这里即可
      const res = await util.request('/v1/user/history', 'GET');
      this.setData({ list: res });
    } catch (error) {
      console.error('获取收藏失败', error);
    }
  }
})