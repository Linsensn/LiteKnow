const util = require('../../utils/util.js');
const app = getApp();

Page({
  data: {
    bankList: [],
    page: 1,
    pageSize: 20,
    keyword: '',
    sortBy: 'desc',
    hasMore: true,
    isLoading: false
  },

  onShow() {
    // 每次显示页面时刷新数据，确保从详情页返回时数据是最新的
    this.fetchBanks(true);
  },

  // 监听搜索框输入
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  // 触发搜索
  onSearch() {
    this.fetchBanks(true);
  },

  // 获取题库列表（isRefresh=true表示刷新/重置，false表示触底加载下一页）
  async fetchBanks(isRefresh = false) {
    if (this.data.isLoading) return;
    if (!isRefresh && !this.data.hasMore) return;

    this.setData({ isLoading: true });
    let currentPage = isRefresh ? 1 : this.data.page;

    try {
      // ⚠️ 路径前缀请确保和您的 main.py 挂载一致，比如 '/api/v1/student/question-banks'
      const res = await util.request('/api/v1/student/question-banks', 'GET', {
        page: currentPage,
        page_size: this.data.pageSize,
        keyword: this.data.keyword,
        sort_by: this.data.sortBy
      });

      // 后端使用了 PageResult 结构，数据列表在 list 字段中
      const newData = res.list || [];
      const total = res.total || 0;

      this.setData({
        bankList: isRefresh ? newData : [...this.data.bankList, ...newData],
        page: currentPage + 1,
        // 判断是否还有更多数据
        hasMore: (isRefresh ? newData.length : this.data.bankList.length + newData.length) < total
      });
    } catch (error) {
      console.error('获取题库失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ isLoading: false });
      wx.stopPullDownRefresh();
    }
  },

  // 新建题库交互
  createBank() {
    wx.showModal({
      title: '新建题库',
      placeholderText: '请输入题库名称（如：高数期末冲刺）',
      editable: true,
      success: async (res) => {
        if (res.confirm && res.content.trim()) {
          wx.showLoading({ title: '创建中...' });
          try {
            // 对接 POST 接口创建题库
            await util.request('/api/v1/student/question-banks', 'POST', {
              name: res.content.trim(),
              description: 'AI 生成的专属题库' // 默认给个描述，您也可以让后端设为可选
            });
            wx.hideLoading();
            wx.showToast({ title: '创建成功', icon: 'success' });
            this.fetchBanks(true); // 创建成功后立刻刷新列表
          } catch (error) {
            wx.hideLoading();
          }
        }
      }
    });
  },

  // 点击卡片跳转到详情页
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/bankDetail/bankDetail?id=${id}`
    });
  },

  onPullDownRefresh() {
    this.fetchBanks(true);
  },

  onReachBottom() {
    this.fetchBanks(false);
  }
})