const util = require('../../utils/util.js');
const app = getApp();

Page({
  data: {
    sessionList: [],     // 存放历史会话的数组
    page: 1,             // 当前页码（用于计算 skip）
    pageSize: 10,        // 每页条数（limit）
    hasMore: true,       // 是否还有更多数据
    isLoading: false     // 是否正在加载中，防止重复触发
  },

  onLoad() {
    this.fetchSessions(true); // 首次进入页面，强制刷新拉取第一页
  },

  // ✨ 核心方法：拉取真实历史数据
  // 参数 isRefresh: 是否是下拉刷新/首次加载（true表示清空重置，false表示触底追加）
  async fetchSessions(isRefresh = false) {
    if (this.data.isLoading) return; // 防抖，避免重复请求
    if (!isRefresh && !this.data.hasMore) return; // 如果不是刷新，且没有更多数据了，直接退出

    this.setData({ isLoading: true });

    // 如果是刷新，重置页码和状态
    let currentPage = isRefresh ? 1 : this.data.page;
    let currentSkip = (currentPage - 1) * this.data.pageSize;

    try {
      // ⚠️ 注意：这里的路径请确保与您主程序挂载的真实前缀一致（假设包含 /api/v1/student）
      const res = await util.request('/api/v1/student/sessions/', 'GET', {
        skip: currentSkip,
        limit: this.data.pageSize
        // keyword: '', // 以后加搜索框可以传这个
        // task_type: '' // 以后加分类 Tab 可以传这个
      });

      // 获取到的新数据数组
      const newData = res || []; 
      
      this.setData({
        // 如果是刷新，直接覆盖；如果是触底，则将新数据拼接到老数据后面
        sessionList: isRefresh ? newData : [...this.data.sessionList, ...newData],
        page: currentPage + 1,
        // 如果后端返回的数据条数小于我们请求的每页条数，说明到底了
        hasMore: newData.length === this.data.pageSize
      });

    } catch (error) {
      console.error('获取历史记录失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ isLoading: false });
      wx.stopPullDownRefresh(); // 停止顶部转圈动画
    }
  },

  // 小程序原生生命周期：监听用户下拉刷新动作
  onPullDownRefresh() {
    this.fetchSessions(true);
  },

  // 小程序原生生命周期：监听页面滑动到底部
  onReachBottom() {
    this.fetchSessions(false);
  }
})