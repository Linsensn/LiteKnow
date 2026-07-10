// pages/adminBanks/adminBanks.js
const util = require('../../utils/util.js');

Page({
  data: {
    banks: [],
    page: 1,
    pageSize: 20,
    total: 0,
    keyword: '',
    isLoading: false,
    hasMore: true
  },

  onLoad() {
    this.fetchBanks();
  },

  // 【彻底删除 onShow，解决死循环和超时】
  
  fetchBanks() {
    if (this.data.isLoading) return Promise.resolve();
    this.setData({ isLoading: true });

    const { page, pageSize, keyword } = this.data;
    let url = `/api/v1/admin/question-banks?page=${page}&page_size=${pageSize}&sort_by=desc`;
    if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;

    return util.request(url, 'GET')
      .then(res => {
        let list = res.data?.list || res.list || [];
        const total = res.data?.total || res.total || 0;
        this.setData({
          banks: page === 1 ? list : [...this.data.banks, ...list],
          total: total,
          hasMore: this.data.banks.length + list.length < total,
          isLoading: false
        });
      })
      .catch(() => this.setData({ isLoading: false }));
  },

  goToBankDetail(e) {
    const id = e.currentTarget.dataset.id;
    const that = this;
    wx.navigateTo({
      url: `/pages/adminBankDetail/adminBankDetail?bankId=${id}`,
      events: {
        // 只有当详情页明确触发 'refresh' 时，才执行此逻辑
        refresh: () => {
          console.log('列表页收到刷新信号');
          that.searchBanks();
        }
      }
    });
  },

  searchBanks() {
    this.setData({ page: 1, banks: [], hasMore: true }, () => {
      this.fetchBanks();
    });
  }
});