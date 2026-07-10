const util = require('../../utils/util.js');

function parseOptionsForEdit(options, type) {
  let parsed = options;
  if (typeof parsed === 'string') {
    try { parsed = JSON.parse(parsed); } catch (e) { parsed = []; }
  }
  
  let result = [];
  if (Array.isArray(parsed) && parsed.length > 0) {
    result = parsed.map((opt, i) => {
      const label = String.fromCharCode(65 + i); 
      if (typeof opt === 'string') return { label, text: opt };
      // 同样处理 id/content 映射
      return { 
        label: opt.label || opt.id || label, 
        text: opt.text || opt.content || '' 
      };
    });
  }
  
  if (result.length === 0 && (type === 'single_choice' || type === 'multi_choice' || type === 'multiple_choice')) {
    result = [
      {label: 'A', text: ''}, {label: 'B', text: ''},
      {label: 'C', text: ''}, {label: 'D', text: ''}
    ];
  }
  return result;
}

Page({
  data: {
    questionId: null,
    formData: {
      content: '',
      question_type: '',
      difficulty_level: '',
      options_json: [],
      correct_answer: '',
      ai_analysis: ''
    },
    difficulties: ['easy', 'medium', 'hard'],
    difficultyIndex: 1,
    isSubmitting: false
  },

  onLoad(options) {
    if (options.questionId) {
      this.setData({ questionId: options.questionId });
      this.fetchQuestionDetail(options.questionId);
    }
  },

  fetchQuestionDetail(id) {
    util.request(`/api/v1/admin/questions/${id}`, 'GET').then(res => {
      const data = res.data || res;
      const dIndex = this.data.difficulties.indexOf(data.difficulty_level);
      
      // 注意正确答案的回显处理：后端可能返回 ["A", "B"]，这里转为 "A,B" 给前端输入框
      let correctAnswer = data.correct_answer || '';
      if (Array.isArray(correctAnswer)) correctAnswer = correctAnswer.join(',');
      
      this.setData({
        formData: {
          content: data.content || '',
          question_type: data.question_type || '',
          difficulty_level: data.difficulty_level || 'medium',
          options_json: parseOptionsForEdit(data.options_json, data.question_type),
          correct_answer: correctAnswer,
          ai_analysis: data.ai_analysis || ''
        },
        difficultyIndex: dIndex !== -1 ? dIndex : 1
      });
    }).catch(() => wx.showToast({ title: '加载失败', icon: 'none' }));
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ [`formData.${field}`]: e.detail.value });
  },

  onOptionInput(e) {
    const { index } = e.currentTarget.dataset;
    const value = e.detail.value;
    const options = [...this.data.formData.options_json];
    options[index].text = value; 
    this.setData({ 'formData.options_json': options });
  },

  onDifficultyChange(e) {
    const index = e.detail.value;
    this.setData({
      difficultyIndex: index,
      'formData.difficulty_level': this.data.difficulties[index]
    });
  },

  submitUpdate() {
    if (!this.data.formData.content.trim()) {
      return wx.showToast({ title: '题干不能为空', icon: 'none' });
    }

    this.setData({ isSubmitting: true });
    
    // 如果后端存答案要求是数组格式，在提交前切回数组
    let answerPayload = this.data.formData.correct_answer;
    if (typeof answerPayload === 'string') {
      answerPayload = answerPayload.split(',').map(s => s.trim()).filter(s => s);
    }

    // 为了迁就后端的 `id` 和 `content` 结构，提交时再转回去
    const optionsPayload = this.data.formData.options_json.map(opt => ({
      id: opt.label,
      content: opt.text
    }));

    const updatePayload = {
      content: this.data.formData.content,
      difficulty_level: this.data.formData.difficulty_level,
      options_json: optionsPayload,
      correct_answer: answerPayload,
      ai_analysis: this.data.formData.ai_analysis
    };

    util.request(`/api/v1/admin/questions/${this.data.questionId}`, 'PUT', updatePayload)
      .then(() => {
        wx.showToast({ title: '修改成功', icon: 'success' });
        const eventChannel = this.getOpenerEventChannel();
        if (eventChannel && eventChannel.emit) {
          eventChannel.emit('refresh', { updated: true });
        }
        setTimeout(() => wx.navigateBack(), 1500);
      })
      .catch(() => {
        wx.showToast({ title: '修改失败', icon: 'none' });
        this.setData({ isSubmitting: false });
      });
  }
});