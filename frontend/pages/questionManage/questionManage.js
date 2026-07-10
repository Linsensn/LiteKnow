const util = require('../../utils/util.js');

Page({
  data: {
    bankId: null,
    questionList: [],
    selectedIds: [],
    page: 1,
    pageSize: 20,
    hasMore: true,
    isLoading: false,

    // 弹窗相关
    showEditModal: false,
    editIndex: -1,
    editForm: {}
  },

  onLoad(options) {
    if (options.bankId) {
      this.setData({ bankId: options.bankId });
      this.fetchQuestions(true);
    }
  },

  // ================= 1. 列表获取 =================
  async fetchQuestions(isRefresh = false) {
    if (this.data.isLoading) return;
    if (!isRefresh && !this.data.hasMore) return;

    this.setData({ isLoading: true });
    let currentPage = isRefresh ? 1 : this.data.page;

    try {
      // 调用你已有的获取题目列表 GET 接口
      const res = await util.request('/api/v1/student/questions', 'GET', {
        bank_id: this.data.bankId,
        page: currentPage,
        page_size: this.data.pageSize
      });

      const newData = (res.list || []).map(q => {
        // 预处理数据：解析 JSON 选项和数组答案，方便展示
        let parsedOptions = [];
        if (q.options_json) {
          try {
            parsedOptions = typeof q.options_json === 'string' ? JSON.parse(q.options_json) : q.options_json;
          } catch(e) {}
        }
        let correctAnswerDisplay = Array.isArray(q.correct_answer) ? q.correct_answer.join(',') : q.correct_answer;
        return { ...q, parsedOptions, correctAnswerDisplay, checked: false };
      });

      this.setData({
        questionList: isRefresh ? newData : [...this.data.questionList, ...newData],
        page: currentPage + 1,
        hasMore: (isRefresh ? newData.length : this.data.questionList.length + newData.length) < (res.total || 0),
        selectedIds: isRefresh ? [] : this.data.selectedIds // 刷新时清空选择
      });
    } catch (error) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  onReachBottom() {
    this.fetchQuestions(false);
  },

  // ================= 2. 删除功能 =================
  onCheckboxChange(e) {
    this.setData({ selectedIds: e.detail.value });
  },

  // 单条删除
  deleteSingle(e) {
    const { id, index } = e.currentTarget.dataset;
    this.executeDelete([id], () => {
      const newList = this.data.questionList;
      newList.splice(index, 1);
      this.setData({ questionList: newList });
    });
  },

  // 批量删除
  deleteBatch() {
    if (this.data.selectedIds.length === 0) return;
    this.executeDelete(this.data.selectedIds, () => {
      // 删除成功后直接刷新整个列表
      this.fetchQuestions(true);
    });
  },

  executeDelete(ids, successCallback) {
    wx.showModal({
      title: '危险操作',
      content: `确定要删除这 ${ids.length} 道题目吗？`,
      confirmColor: '#ff4d4f',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' });
          try {
            // ⚠️ 这里需要后端提供 DELETE 接口
            if (ids.length === 1) {
              await util.request(`/api/v1/student/questions/${ids[0]}`, 'DELETE');
            } else {
              await util.request('/api/v1/student/questions/bulk', 'DELETE', { question_ids: ids });
            }
            wx.hideLoading();
            wx.showToast({ title: '删除成功', icon: 'success' });
            successCallback();
          } catch (e) {
            wx.hideLoading();
            wx.showToast({ title: '删除失败', icon: 'none' });
          }
        }
      }
    });
  },

  // ================= 3. 编辑功能 =================
  openEditModal(e) {
    const index = e.currentTarget.dataset.index;
    const q = this.data.questionList[index];
    
    // 深拷贝一份当前题目的数据用于编辑
    this.setData({
      showEditModal: true,
      editIndex: index,
      editForm: {
        id: q.id,
        content: q.content,
        parsedOptions: JSON.parse(JSON.stringify(q.parsedOptions)),
        correct_answer: q.correctAnswerDisplay
      }
    });
  },

  closeEditModal() {
    this.setData({ showEditModal: false, editIndex: -1, editForm: {} });
  },

  // 监听选项内容的动态修改
  onOptionInput(e) {
    const idx = e.currentTarget.dataset.index;
    const val = e.detail.value;
    const key = `editForm.parsedOptions[${idx}].content`;
    this.setData({ [key]: val });
  },

  // 提交修改保存
  async saveEdit() {
    const { editForm, editIndex } = this.data;
    
    // 将字符串形式的 'A,C' 重新转为数组 ['A', 'C']
    const ansArray = editForm.correct_answer.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
    
    const payload = {
      content: editForm.content,
      // 🌟 核心修正：后端要求 List[Any]，所以直接传数组，不要用 JSON.stringify
      options_json: editForm.parsedOptions, 
      correct_answer: ansArray
    };

    wx.showLoading({ title: '保存中...', mask: true });
    try {
      await util.request(`/api/v1/student/questions/${editForm.id}`, 'PUT', payload);
      
      // 前端静默更新，体验更好
      const updateKey1 = `questionList[${editIndex}].content`;
      const updateKey2 = `questionList[${editIndex}].parsedOptions`;
      const updateKey3 = `questionList[${editIndex}].correctAnswerDisplay`;
      const updateKey4 = `questionList[${editIndex}].correct_answer`;
      
      this.setData({
        [updateKey1]: editForm.content,
        [updateKey2]: editForm.parsedOptions,
        [updateKey3]: ansArray.join(','),
        [updateKey4]: ansArray,
        showEditModal: false
      });

      wx.hideLoading();
      wx.showToast({ title: '修改成功', icon: 'success' });
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '修改失败', icon: 'none' });
    }
  }
})