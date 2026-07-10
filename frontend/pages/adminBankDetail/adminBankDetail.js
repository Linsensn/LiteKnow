// pages/adminBankDetail/adminBankDetail.js
const util = require('../../utils/util.js');

// 兼容多种后端命名习惯的终极解析方案
function parseOptions(options) {
  if (!options) return [];
  let parsed = options;
  if (typeof parsed === 'string') {
    try { parsed = JSON.parse(parsed); } catch (e) { return []; }
  }
  if (Array.isArray(parsed)) {
    return parsed.map((opt, i) => {
      if (typeof opt === 'string') return { label: String.fromCharCode(65 + i), text: opt };
      return {
        // 兼容后端可能是 id 或是 label
        label: opt.label || opt.id || String.fromCharCode(65 + i),
        // 兼容后端可能是 text 或是 content
        text: opt.text || opt.content || ''
      };
    });
  }
  return [];
}

Page({
  data: {
    bankId: null,
    questions: [],
    page: 1,
    pageSize: 20,
    total: 0,
    isLoading: false,
    hasMore: true,
    selectedIds: [],
    isAllSelected: false
  },

  onLoad(options) {
    if (options.bankId) {
      this.setData({ bankId: parseInt(options.bankId) });
      this.fetchQuestions();
    }
  },

  fetchQuestions() {
    if (this.data.isLoading) return;
    this.setData({ isLoading: true });

    let url = `/api/v1/admin/questions?bank_id=${this.data.bankId}&page=${this.data.page}&page_size=${this.data.pageSize}`;
    util.request(url, 'GET').then(res => {
      const list = res.data?.list || res.list || [];
      const formattedList = list.map(item => ({ 
        ...item, 
        checked: false,
        options_json: parseOptions(item.options_json) 
      }));
      const total = res.data?.total || res.total || 0;
      
      this.setData({
        questions: this.data.page === 1 ? formattedList : [...this.data.questions, ...formattedList],
        total: total,
        hasMore: this.data.questions.length + list.length < total,
        isLoading: false,
        isAllSelected: false,
        selectedIds: []
      });
    }).catch(() => this.setData({ isLoading: false }));
  },

  onCheckboxChange(e) {
    const selectedIds = e.detail.value.map(id => parseInt(id));
    this.setData({
      selectedIds: selectedIds,
      isAllSelected: selectedIds.length === this.data.questions.length && this.data.questions.length > 0
    });
  },

  toggleSelectAll() {
    const nextState = !this.data.isAllSelected;
    const nextQuestions = this.data.questions.map(q => ({ ...q, checked: nextState }));
    const nextSelectedIds = nextState ? nextQuestions.map(q => q.id) : [];
    this.setData({ isAllSelected: nextState, questions: nextQuestions, selectedIds: nextSelectedIds });
  },

  deleteQuestion(e) {
    const { id, index } = e.currentTarget.dataset;
    const that = this;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除吗？',
      success: (res) => {
        if (res.confirm) {
          util.request(`/api/v1/admin/questions/${id}`, 'DELETE').then(() => {
            wx.showToast({ title: '删除成功', icon: 'success' });
            let newQuestions = [...that.data.questions];
            newQuestions.splice(index, 1);
            that.setData({ questions: newQuestions });
            const eventChannel = that.getOpenerEventChannel();
            if (eventChannel && eventChannel.emit) eventChannel.emit('refresh', { deleted: true });
          });
        }
      }
    });
  },

  batchDelete() {
    const ids = this.data.selectedIds;
    if (ids.length === 0) return;
    const that = this;
    wx.showModal({
      title: '批量删除',
      content: `确定删除选中的 ${ids.length} 道题目吗？`,
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' });
          const deletePromises = ids.map(id => util.request(`/api/v1/admin/questions/${id}`, 'DELETE'));
          Promise.all(deletePromises).then(() => {
              wx.hideLoading();
              wx.showToast({ title: '批量删除成功', icon: 'success' });
              that.setData({ page: 1, questions: [], selectedIds: [], isAllSelected: false });
              that.fetchQuestions();
              const eventChannel = that.getOpenerEventChannel();
              if (eventChannel && eventChannel.emit) eventChannel.emit('refresh', { deleted: true });
            }).catch(() => {
              wx.hideLoading();
              wx.showToast({ title: '部分删除失败', icon: 'none' });
            });
        }
      }
    });
  },

  editQuestion(e) {
    const qId = e.currentTarget.dataset.id;
    const that = this; // 保存当前页面的 this 引用
    
    wx.navigateTo({
      url: `/pages/adminEditQuestion/adminEditQuestion?questionId=${qId}`,
      events: {
        // 监听编辑页发出的 'refresh' 信号
        refresh: function(data) {
          // 收到信号后，重置页码和列表，重新拉取最新数据
          that.setData({ 
            page: 1, 
            questions: [], 
            selectedIds: [], 
            isAllSelected: false 
          }, () => {
            that.fetchQuestions();
          });
        }
      }
    });
  }
});