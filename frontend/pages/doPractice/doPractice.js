const util = require('../../utils/util.js');

Page({
  data: {
    sessionId: null,
    questionSequence: [],
    currentIndex: 0,
    
    currentQuestion: null,
    optionsList: [],
    
    // ✨ 现在里面存的是数组（比如 { 0: ['A', 'C'], 1: ['B'] } ）或字符串（简答题）
    userAnswers: {}, 
    userAnswerDisplay: '', // 用于 WXML 渲染用户答案
    
    isSessionSubmitted: false,
    isAnswerCorrect: false
  },

  onLoad(options) {
    if (options.sessionId) {
      this.setData({ sessionId: options.sessionId });
      this.initSession(options.sessionId);
    }
  },

  // pages/doPractice/doPractice.js 局部修改：
  
  async initSession(sessionId) {
    wx.showLoading({ title: '加载题库中...' });
    try {
      const res = await util.request(`/api/v1/student/practice-sessions/${sessionId}`, 'GET');
      let sequence = res.question_sequence || [];
      
      // 🌟 新增：如果后端返回的是字符串（例如 "[1, 2, 3]"），将其解析为数组
      if (typeof sequence === 'string') {
        try {
          sequence = JSON.parse(sequence);
        } catch (e) {
          sequence = [];
        }
      }

      // 🌟 删除：删掉了 if (sequence.length === 0) { sequence = [9991, 9992]; } 这段 Mock 逻辑
      if (sequence.length === 0) {
        wx.hideLoading();
        return wx.showToast({ title: '当前会话没有题目', icon: 'none' });
      }

      this.setData({
        questionSequence: sequence,
        currentIndex: 0,
        userAnswers: {},
        isSessionSubmitted: false
      });
      this.fetchCurrentQuestion();
    } catch (e) {
      wx.hideLoading();
    }
  },

  async fetchCurrentQuestion() {
    const { questionSequence, currentIndex, userAnswers, isSessionSubmitted } = this.data;
    if (!questionSequence || questionSequence.length === 0) return;
    
    wx.showLoading({ title: '加载中...' });
    const questionId = questionSequence[currentIndex];
    
    try {
      // 🌟 删除：删掉对 questionId === 9991 的 if/else 判断，直接请求真实接口
      let qRes = await util.request(`/api/v1/student/questions/${questionId}`, 'GET');
      
      const savedAnswerArr = userAnswers[currentIndex] || (qRes.question_type === 'essay' ? '' : []);
      
      let parsedOptions = [];
      if (qRes.options_json && Array.isArray(qRes.options_json)) {
        parsedOptions = qRes.options_json.map(opt => {
          const prefix = opt.id;        
          const text = opt.content;     
          
          let isSelected = Array.isArray(savedAnswerArr) && savedAnswerArr.includes(prefix);
          let isCorrect = false;
          
          if (isSessionSubmitted) {
             isCorrect = Array.isArray(qRes.correct_answer) && qRes.correct_answer.includes(prefix);
          }
          
          return { prefix, text, original: opt, isSelected, isCorrect };
        });

        if (qRes.option_sequence && Array.isArray(qRes.option_sequence)) {
          parsedOptions.sort((a, b) => qRes.option_sequence.indexOf(a.prefix) - qRes.option_sequence.indexOf(b.prefix));
        }
      }

      let correctAnswerDisplay = Array.isArray(qRes.correct_answer) ? qRes.correct_answer.join(', ') : qRes.correct_answer;
      let userAnswerDisplay = Array.isArray(savedAnswerArr) ? savedAnswerArr.join(', ') : savedAnswerArr;

      let isAnswerCorrect = false;
      if (isSessionSubmitted) {
        if (Array.isArray(qRes.correct_answer) && Array.isArray(savedAnswerArr)) {
          isAnswerCorrect = [...qRes.correct_answer].sort().join(',') === [...savedAnswerArr].sort().join(',');
        } else {
          isAnswerCorrect = (savedAnswerArr === qRes.correct_answer);
        }
      }

      this.setData({
        currentQuestion: { ...qRes, correctAnswerDisplay },
        optionsList: parsedOptions,
        isAnswerCorrect: isAnswerCorrect,
        userAnswerDisplay: userAnswerDisplay
      });
      wx.hideLoading();
    } catch (e) {
      wx.hideLoading();
    }
  },

  toggleOption(e) {
    if (this.data.isSessionSubmitted) return; 
    
    const index = e.currentTarget.dataset.index;
    const { currentQuestion, optionsList, currentIndex } = this.data;
    const isSingle = currentQuestion.question_type === 'single_choice';

    let newList = [...optionsList];
    if (isSingle) {
      newList.forEach((item, idx) => item.isSelected = (idx === index));
    } else {
      newList[index].isSelected = !newList[index].isSelected;
    }

    // ✨ 重点：现在直接提取出一个纯数组存下来，对应后端的 user_answer JSON
    const currentAnswerArr = newList.filter(item => item.isSelected).map(item => item.prefix);
    
    this.setData({ 
      optionsList: newList,
      [`userAnswers.${currentIndex}`]: currentAnswerArr,
      userAnswerDisplay: currentAnswerArr.join(', ') // 同步更新展示
    });
  },

  onEssayInput(e) {
    this.setData({ 
      [`userAnswers.${this.data.currentIndex}`]: e.detail.value,
      userAnswerDisplay: e.detail.value 
    });
  },

  goPrev() {
    if (this.data.currentIndex > 0) {
      this.setData({ currentIndex: this.data.currentIndex - 1 });
      this.fetchCurrentQuestion();
    }
  },

  goNext() {
    if (this.data.currentIndex < this.data.questionSequence.length - 1) {
      this.setData({ currentIndex: this.data.currentIndex + 1 });
      this.fetchCurrentQuestion();
    }
  },

  // pages/doPractice/doPractice.js 局部修改：
  async submitPaper() {
    const { questionSequence, userAnswers, sessionId } = this.data;
    const answeredCount = Object.keys(userAnswers).length;
    
    if (answeredCount < questionSequence.length) {
       const confirm = await new Promise(resolve => {
         wx.showModal({
           title: '提示',
           content: `还有 ${questionSequence.length - answeredCount} 道题未做，确定要交卷吗？`,
           success: (res) => resolve(res.confirm)
         });
       });
       if (!confirm) return;
    }

    wx.showLoading({ title: 'AI 批阅中...', mask: true });

    // 🌟 核心升级：将前端按 index 存储的答案，转换为以 question_id 为 Key 的字典发给后端
    const answerPayload = {};
    questionSequence.forEach((qId, index) => {
      answerPayload[qId] = userAnswers[index] || []; 
    });

    try {
      // 发起真实的交卷请求
      await util.request(`/api/v1/student/practice-sessions/${sessionId}/submit-paper`, 'POST', {
        answers: answerPayload
      });

      this.setData({ 
        isSessionSubmitted: true, 
        currentIndex: 0 
      });
      
      // 交卷后重新拉取第一题，此时 isSessionSubmitted 为 true，前端会展示答案和解析
      this.fetchCurrentQuestion(); 
      wx.hideLoading();
      wx.showToast({ title: '批阅完成', icon: 'success' });
      
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '交卷失败，请重试', icon: 'none' });
    }
  },

  async exitReview() {
    const sessionId = this.data.sessionId;
    try {
      await util.request(`/api/v1/student/practice-sessions/${sessionId}/status`, 'PATCH', { status: 'completed' });
    } catch (e) {}
    wx.navigateBack({ delta: 1 });
  }
})