const util = require('../../utils/util.js');

Page({
  data: {
    bankId: null,
    bankInfo: {} // 存放当前题库数据
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ bankId: options.id });
      this.fetchBankDetail(options.id);
    }
  },

  onShow() {
    if (this.data.bankId) {
      this.fetchBankDetail(this.data.bankId);
    }
  },

  // 获取题库详情
  async fetchBankDetail(id) {
    try {
      const res = await util.request(`/api/v1/student/question-banks/${id}`, 'GET');
      
      this.setData({ 
        bankInfo: {
          ...res,
          name: res.bank_name,
          question_count: res.total_questions,
          // ⚠️ 这里由于后端 schema 还没给统计数据，前端先暂时做一层兜底
          // 等后端加了 completion_rate 和 accuracy_rate 字段后，这里会自动读取！
          completion_rate: res.completion_rate || 0, 
          accuracy_rate: res.accuracy_rate || 0
        }
      });
    } catch (e) {
      console.error('获取题库详情失败', e);
    }
  },

  // 调起题库管理面板
  goToManage() {
    if (!this.data.bankId) return;
    
    wx.showActionSheet({
      itemList: ['📝 题目列表管理', '✏️ 修改题库名称', '🗑️ 删除题库'],
      itemColor: '#333333',
      success: (res) => {
        if (res.tapIndex === 0) {
          wx.navigateTo({ 
            url: `/pages/questionManage/questionManage?bankId=${this.data.bankId}` 
          });
        } else if (res.tapIndex === 1) {
          this.handleRenameBank();
        } else if (res.tapIndex === 2) {
          this.handleDeleteBank();
        }
      }
    });
  },

  // 处理：修改题库名称
  handleRenameBank() {
    wx.showModal({
      title: '修改题库名称',
      content: this.data.bankInfo.name,
      editable: true,
      placeholderText: '请输入新题库名称',
      success: async (res) => {
        if (res.confirm && res.content.trim()) {
          const newName = res.content.trim();
          if (newName === this.data.bankInfo.name) return;

          wx.showLoading({ title: '修改中...' });
          try {
            await util.request(`/api/v1/student/question-banks/${this.data.bankId}`, 'PUT', {
              bank_name: newName, 
              name: newName 
            });
            wx.hideLoading();
            wx.showToast({ title: '修改成功', icon: 'success' });
            
            this.setData({
              ['bankInfo.name']: newName
            });
          } catch (error) {
            wx.hideLoading();
          }
        }
      }
    });
  },

  // 处理：删除题库
  handleDeleteBank() {
    wx.showModal({
      title: '高危操作确认',
      content: '确定要删除该题库吗？删除后里面的所有题目和练习记录将永久丢失。',
      confirmColor: '#ff4d4f',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' });
          try {
            await util.request(`/api/v1/student/question-banks/${this.data.bankId}`, 'DELETE');
            wx.hideLoading();
            wx.showToast({ title: '删除成功', icon: 'success' });
            
            setTimeout(() => {
              wx.navigateBack();
            }, 1500);
          } catch (error) {
            wx.hideLoading();
          }
        }
      }
    });
  },

  // 跳转到练习统计页
  goToHistory() {
    // 🚧 因为你目前还没有专门的练习统计页，先给个提示：
    wx.showToast({ title: '统计功能开发中，敬请期待', icon: 'none' });
    
    // 如果你后面建了这个页面（比如叫 practiceStats），再把上面那行删掉，换成下面这行：
    // wx.navigateTo({ url: `/pages/practiceStats/practiceStats?bankId=${this.data.bankId}` });
  },

  // 跳转到我的笔记页
  goToNotes() {
    // 🚧 同理，先给个开发中提示：
    wx.showToast({ title: '笔记功能开发中，敬请期待', icon: 'none' });

    // 如果你后面建了这个页面（比如叫 myNotes），再换成：
    // wx.navigateTo({ url: `/pages/myNotes/myNotes?bankId=${this.data.bankId}` });
  },

  // 发起不同的 PracticeSession
  async startPractice(e) {
    const mode = e.currentTarget.dataset.mode; 
    
    if (!this.data.bankId) return;
    wx.showLoading({ title: '准备练习中...' });

    try {
      const payload = {
        bank_id: parseInt(this.data.bankId),
        practice_mode: mode, 
        question_sequence: [] 
      };

      const sessionRes = await util.request('/api/v1/student/practice-sessions', 'POST', payload);
      wx.hideLoading();
      
      wx.navigateTo({
        url: `/pages/doPractice/doPractice?sessionId=${sessionRes.id}`
      });
    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: '无法开启练习', icon: 'none' });
    }
  },

  onShareAppMessage() {
    return {
      title: `快来和我一起刷《${this.data.bankInfo.name || '这个题库'}》吧！`,
      path: `/pages/bankDetail/bankDetail?id=${this.data.bankId}`
    };
  }
});