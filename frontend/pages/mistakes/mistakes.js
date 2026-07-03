const util = require('../../utils/util.js')

Page({
  data: {
    // 模拟的错题本数据
    mistakesList: []
  },

  onLoad() {
    this.fetchMistakes();
  },

  // 获取错题列表（当前使用模拟数据）
  fetchMistakes() {
    wx.showLoading({ title: '加载中...' });

    // 模拟网络请求延迟
    setTimeout(() => {
      const mockData = [
        {
          id: 1,
          topic: "物理 / 经典力学",
          date: "2023-10-24 14:30",
          question: "一辆汽车在平直公路上匀速行驶，关于汽车受到的力，以下说法正确的是？",
          userAnswer: "C. 汽车受到的牵引力大于阻力",
          correctAnswer: "A. 汽车受到的牵引力等于阻力",
          explanation: "根据牛顿第一定律，物体在不受外力或受力平衡时，将保持静止或匀速直线运动状态。汽车做匀速直线运动，说明其在水平方向上受力平衡，即牵引力等于阻力。",
          expanded: false // 控制是否展开解析
        },
        {
          id: 2,
          topic: "历史 / 唐朝",
          date: "2023-10-23 09:15",
          question: "唐朝著名的“安史之乱”爆发于哪位皇帝在位时期？",
          userAnswer: "B. 唐太宗",
          correctAnswer: "D. 唐玄宗",
          explanation: "安史之乱是中国唐代玄宗末年至代宗初年由唐朝将领安禄山与史思明背叛唐朝后发动的战争，是同唐朝皇室争夺统治权的内战，为唐由盛而衰的转折点。",
          expanded: false
        }
      ];

      this.setData({
        mistakesList: mockData
      });
      wx.hideLoading();
    }, 800);
  },

  // 切换展开/折叠状态
  toggleExpand(e) {
    const index = e.currentTarget.dataset.index;
    const key = `mistakesList[${index}].expanded`;
    const currentState = this.data.mistakesList[index].expanded;

    this.setData({
      [key]: !currentState
    });
  },

  // 跳转到知识精讲页面进行追问
  // catchtap 阻止了事件冒泡，不会触发卡片的折叠/展开
  goToExplain(e) {
    const question = e.currentTarget.dataset.question;
    
    // 我们将错题内容作为参数传递给精讲页面
    // 请确保您的 app.json 中 explain 页面的路径是正确的
    wx.navigateTo({
      url: `/pages/explain/explain?question=${encodeURIComponent(question)}`
    });
  }
})