// pages/adminUsers/adminUsers.js
const util = require('../../utils/util.js');

Page({
  data: {
    users: [],
    page: 1,
    pageSize: 20,
    total: 0,
    keyword: '',
    isLoading: false,
    hasMore: true
  },

  onLoad() {
    this.fetchUsers();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, users: [], hasMore: true });
    this.fetchUsers().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.isLoading) {
      this.setData({ page: this.data.page + 1 });
      this.fetchUsers();
    }
  },

  // 监听搜索输入（防抖）
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
    if (this.searchTimer) clearTimeout(this.searchTimer);
    
    this.searchTimer = setTimeout(() => {
      this.searchUsers();
    }, 500);
  },

  // 执行搜索
  searchUsers() {
    this.setData({ page: 1, users: [], hasMore: true });
    this.fetchUsers();
  },

  // 获取用户列表
  fetchUsers() {
    if (this.data.isLoading) return Promise.resolve();
    this.setData({ isLoading: true });

    const { page, pageSize, keyword } = this.data;
    // 适配后端最新的路由参数
    let url = `/api/v1/admin/users/?page=${page}&page_size=${pageSize}`;
    if (keyword) {
      url += `&keyword=${encodeURIComponent(keyword)}`;
    }
    
    return util.request(url, 'GET')
      .then(res => {
        let list = res.data?.list || res.list || [];
        const total = res.data?.total || res.total || 0;

        list = list.map(item => ({
          ...item,
          short_date: item.created_at ? item.created_at.substring(0, 10) : '未知'
        }));

        this.setData({
          users: this.data.page === 1 ? list : [...this.data.users, ...list],
          total: total,
          hasMore: this.data.users.length + list.length < total,
          isLoading: false
        });
      })
      .catch(err => {
        console.error('获取用户失败', err);
        this.setData({ isLoading: false });
      });
  },

  // 点击卡片，跳转到用户的详情页 (带上 userId)
  goToUserDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/adminUserDetail/adminUserDetail?userId=${id}`
    });
  },

  // 封禁/解封操作
  toggleStatus(e) {
    const { id, active, index } = e.currentTarget.dataset;
    const newStatus = !active;
    const actionText = newStatus ? '解封' : '封禁';

    wx.showModal({
      title: '操作确认',
      content: `确定要${actionText}该用户吗？`,
      success: (res) => {
        if (res.confirm) {
          util.request(`/api/v1/admin/users/batch/status`, 'PUT', {
            user_ids: [id],
            status_data: { is_active: newStatus }
          }).then(() => {
            wx.showToast({ title: `${actionText}成功`, icon: 'success' });
            this.setData({ [`users[${index}].is_active`]: newStatus });
          });
        }
      }
    });
  },

  // 逻辑删除用户
  deleteUser(e) {
    const { id, index } = e.currentTarget.dataset;
    wx.showModal({
      title: '危险操作',
      content: '确定要注销此用户吗？（逻辑删除）',
      confirmColor: '#ff3b30',
      success: (res) => {
        if (res.confirm) {
          util.request(`/api/v1/admin/users/${id}`, 'DELETE').then(() => {
            wx.showToast({ title: '已注销', icon: 'success' });
            const newUsers = [...this.data.users];
            newUsers.splice(index, 1);
            this.setData({ users: newUsers, total: this.data.total - 1 });
          });
        }
      }
    });
  }
});