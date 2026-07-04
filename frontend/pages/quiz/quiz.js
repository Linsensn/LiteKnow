const util = require('../../utils/util.js')

Page({
  data: {
    topicText: '',
    quizList: [],      // 题目列表
    hasSubmitted: false // 是否已提交查看解析
  },

  onInput(e) {
    this.setData({
      topicText: e.detail.value
    })
  },

  // 模拟从 AI Agent 获取测验题目
  async generateQuiz() {
    if (!this.data.topicText.trim()) return;

    // 重置状态
    this.setData({ 
      quizList: [],
      hasSubmitted: false
    });
    wx.showLoading({ title: 'AI正在出题...', mask: true });

    try {
      /* * 注意：这里是模拟数据以便您测试前端 UI。
       * 实际开发中，请使用以下代码调用后端：
       * const res = await util.request('/v1/agent/quiz', 'POST', { topic: this.data.topicText }, false);
       */
      
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockData = [
        {
          id: 101,
          title: "关于光合作用，下列说法正确的是？",
          options: ["只在白天进行", "只在夜间进行", "白天夜间均可进行", "需要吸收氧气释放二氧化碳"],
          correct: 0, // 正确答案的索引 (A)
          explanation: "光合作用必须有光才能进行，因此在自然条件下通常只在白天（有光照时）进行。植物在夜间主要进行呼吸作用。"
        },
        {
          id: 102,
          title: "水（H2O）在常温常压下呈什么状态？",
          options: ["固态", "液态", "气态", "等离子态"],
          correct: 1, // (B)
          explanation: "在标准大气压和常温（20-25摄氏度）下，水是液态的。"
        }
      ];

      // 给每道题初始化一个 selected 字段，记录用户的选择
      const formattedList = mockData.map(item => ({
        ...item,
        selected: -1 
      }));

      this.setData({ quizList: formattedList });
      wx.hideLoading();

    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: '出题失败，请重试', icon: 'none' });
    }
  },

  // 用户点击选项
  selectOption(e) {
    // 如果已经交卷，就不能再修改答案了
    if (this.data.hasSubmitted) return;

    const { qindex, oindex } = e.currentTarget.dataset;
    const key = `quizList[${qindex}].selected`;
    
    this.setData({
      [key]: oindex
    });
  },

  // 提交答卷
  submitQuiz() {
    // 简单校验一下是不是所有题都做了
    const allAnswered = this.data.quizList.every(q => q.selected !== -1);
    if (!allAnswered) {
      wx.showToast({
        title: '还有题目未作答哦',
        icon: 'none'
      });
      return;
    }

    // 可以在这里计算分数、将错题通过接口保存到用户的【错题本】中
    // 演示仅展示将状态切换为已提交
    this.setData({
      hasSubmitted: true
    });
    
    wx.showToast({
      title: '已交卷',
      icon: 'success'
    });
  },

  // 重新生成/再来一次
  restartQuiz() {
    this.setData({
      topicText: '',
      quizList: [],
      hasSubmitted: false
    });
  }
})