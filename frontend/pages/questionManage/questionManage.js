const util = require('../../utils/util.js');

Page({
  data: {
    bankId: null,
    questionList: [],
    totalQuestions: 0,
    page: 1,
    pageSize: 10,
    isLoading: false,
    hasMore: true
  },

  onLoad(options) {
    if (options.bankId) {
      this.setData({ bankId: options.bankId });
      this.fetchQuestions(true);
    }
  },

  async fetchQuestions(isRefresh = false) {
    if (this.data.isLoading || (!this.data.hasMore && !isRefresh)) return;
    
    this.setData({ isLoading: true });
    if (isRefresh) this.setData({ page: 1, questionList: [] });

    try {
      const res = await util.request(`/api/v1/student/questions`, 'GET', {
        bank_id: this.data.bankId,
        page: this.data.page,
        page_size: this.data.pageSize
      });

      // ✨ 核心修改：适配后端的 JSON 选项和答案
      const newList = (res.list || []).map(q => {
        // 将 [{"id": "A", "content": "..."}] 转换为 ["A. ..."] 的展示字符串
        let displayOptions = [];
        if (Array.isArray(q.options_json)) {
            displayOptions = q.options_json.map(o => `${o.id}. ${o.content}`);
        }
        // 将 ["A", "C"] 转换为 "A, C"
        let displayAnswer = q.correct_answer;
        if (Array.isArray(q.correct_answer)) {
            displayAnswer = q.correct_answer.join(', ');
        }
        return { ...q, displayOptions, displayAnswer };
      });

      this.setData({
        questionList: isRefresh ? newList : [...this.data.questionList, ...newList],
        totalQuestions: res.total || 0,
        hasMore: newList.length === this.data.pageSize,
        page: this.data.page + 1,
        isLoading: false
      });
    } catch (e) {
      this.setData({ isLoading: false });
      wx.showToast({ title: '获取题目失败', icon: 'none' });
    }
  },

  loadMore() {
    this.fetchQuestions();
  },

  deleteQuestion(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这道题吗？',
      success: (res) => {
        if (res.confirm) {
          wx.showToast({ title: '模拟删除成功', icon: 'success' });
        }
      }
    })
  }
})