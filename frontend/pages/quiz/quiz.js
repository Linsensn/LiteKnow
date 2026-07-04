const util = require('../../utils/util.js')

Page({
  data: {
    topicText: '',
    quizList: [],      // 题目列表
    hasSubmitted: false, // 是否已提交查看解析
    
    // ✨ 新增双核引擎所需状态
    bankId: '',        // 记录从哪个题库来的
    mode: '',          // 记录练习模式（如：随机练习）
    isBankMode: false  // 判断当前是不是题库刷题模式
  },

  // ✨ 核心一：监听页面加载，捕捉参数
  onLoad(options) {
    if (options.bankId) {
      this.setData({
        bankId: options.bankId,
        mode: decodeURIComponent(options.mode || '默认练习'),
        isBankMode: true // 开启题库模式！
      });
      
      // 如果是题库模式，一进页面就自动拉取题目，无需用户再点按钮
      this.fetchBankQuiz();
    }
  },

  onInput(e) {
    this.setData({ topicText: e.detail.value })
  },

  // 🚀 引擎 A：工作台模式 (AI 实时出题)
  async generateQuiz() {
    if (!this.data.topicText.trim()) return;

    this.setData({ quizList: [], hasSubmitted: false });

    try {
      const res = await util.request('/v1/agent/quiz', 'POST', { 
        topic: this.data.topicText 
      });
      
      const formattedList = res.map(item => ({ ...item, selected: -1 }));
      this.setData({ quizList: formattedList });
    } catch (error) {
      console.error('出题请求失败', error);
    }
  },

  // 🚀 引擎 B：题库模式 (从已有题库抽题)
  async fetchBankQuiz() {
    this.setData({ quizList: [], hasSubmitted: false });

    try {
      // 替换为真实的题库抽题接口，把题库 ID 和模式传给后端
      const res = await util.request(`/v1/agent/bank/quiz?bankId=${this.data.bankId}&mode=${this.data.mode}`, 'GET');
      
      const formattedList = res.map(item => ({ ...item, selected: -1 }));
      this.setData({ quizList: formattedList });
    } catch (error) {
      console.error('获取题库题目失败', error);
    }
  },

  // 👇 以下答题与判分逻辑，两套引擎完全共享，无需改动！
  selectOption(e) {
    if (this.data.hasSubmitted) return;
    const { qindex, oindex } = e.currentTarget.dataset;
    const key = `quizList[${qindex}].selected`;
    this.setData({ [key]: oindex });
  },

  submitQuiz() {
    const allAnswered = this.data.quizList.every(q => q.selected !== -1);
    if (!allAnswered) {
      wx.showToast({ title: '还有题目未作答哦', icon: 'none' });
      return;
    }
    this.setData({ hasSubmitted: true });
    wx.showToast({ title: '已交卷', icon: 'success' });
  },

  // ✨ 核心二：智能的“再来一次”按钮
  restartQuiz() {
    if (this.data.isBankMode) {
      // 如果是题库模式，点击重新开始，就再向后端抽一次题
      this.fetchBankQuiz();
    } else {
      // 如果是工作台模式，清空状态，让用户重新输入知识点
      this.setData({
        topicText: '',
        quizList: [],
        hasSubmitted: false
      });
    }
  }
})