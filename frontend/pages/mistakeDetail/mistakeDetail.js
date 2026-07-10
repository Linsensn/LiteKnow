const util = require('../../utils/util.js');

Page({
  data: {
    detail: null,   // 存放错题记录信息（如我的答案）
    question: null, // 存放原题完整信息（如选项、题型）
    optionsList: []
  },

  onLoad(options) {
    if (options.id) {
      this.fetchMistakeDetail(options.id);
    }
  },

  async fetchMistakeDetail(id) {
    wx.showLoading({ title: '加载解析中...' });
    try {
      // 1. 获取错题本轻量级记录
      const wqRes = await util.request(`/api/v1/student/wrong-questions/${id}`, 'GET');
      
      let qRes = wqRes.question || {};
      
      // 2. 🌟 核心破案：如果错题接口没有返回完整的选项，我们就用关联的 question_id 单独拉取完整原题
      if (!qRes.options_json && wqRes.question_id) {
        try {
          qRes = await util.request(`/api/v1/student/questions/${wqRes.question_id}`, 'GET');
        } catch (e) {
          console.error('拉取原题详情失败', e);
        }
      }

      let optionsList = [];
      const optionsJson = qRes.options_json;
      const qType = qRes.question_type;
      
      // 3. 解析并组装选项
      if (optionsJson && qType !== 'essay') {
        try {
          const rawOpts = typeof optionsJson === 'string' ? JSON.parse(optionsJson) : optionsJson;
                          
          // 以原题的正确答案为准，结合错题记录里的用户答案
          const correctAns = String(qRes.correct_answer || wqRes.correct_answer || '');
          const userAns = String(wqRes.user_answer || '');
          
          optionsList = rawOpts.map(opt => ({
            id: opt.id,
            content: opt.content,
            isCorrect: correctAns.includes(opt.id),
            // 用户选了这个且它不是正确答案，那就是做错的选项
            isUserChoice: userAns.includes(opt.id) && !correctAns.includes(opt.id) 
          }));
        } catch(e) {
          console.error("解析选项 JSON 失败", e);
        }
      }

      // 将两条数据都存入 data 供视图渲染
      this.setData({ 
        detail: wqRes,
        question: qRes,
        optionsList: optionsList
      });

    } catch (error) {
      wx.showToast({ title: '加载详情失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  }
})