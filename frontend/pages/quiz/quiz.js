// pages/quiz/quiz.js
const util = require('../../utils/util.js');

Page({
  /**
   * 页面的初始数据
   */
  data: {
    materialText: '', // 文本素材内容
    attachments: [],  // 已上传的附件列表，格式 [{ id: 1, name: 'xxx.pdf' }]
    questionCount: 5, // 默认生成 5 题
    difficulty: 'basic', // 难度选项：basic | advanced | hard
    
    bankList: [], // 题库列表
    selectedBank: null, // 当前选中的题库对象
    targetBankId: null, // 要保存到的目标题库 ID (如果不选则为空，后端新建)
    customBankName: '', // 绑定自定义题库名称
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.fetchQuestionBanks();
  },

  /**
   * 获取用户的题库列表 (用于下拉选择)
   */
  fetchQuestionBanks() {
    util.request('/api/v1/student/question-banks?page=1&page_size=100', 'GET')
      .then(res => {
        if (res && res.list) {
          const bankList = [{ id: null, bank_name: '+ 自动新建题库' }, ...res.list];
          this.setData({ bankList });
        }
      })
      .catch(err => {
        console.error('获取题库列表失败', err);
      });
  },

  /**
   * 监听：题库选择器改变
   */
  onBankChange(e) {
    const index = e.detail.value;
    const selectedBank = this.data.bankList[index];
    this.setData({
      selectedBank: selectedBank,
      targetBankId: selectedBank.id,
      customBankName: '' // 切换选项时，清空之前填写的自定义名称
    });
  },

  /**
   * 监听：滑动条改变题数
   */
  onCountChange(e) {
    this.setData({
      questionCount: e.detail.value
    });
  },

  /**
   * 监听：点击切换难度标签
   */
  onDifficultyChange(e) {
    const level = e.currentTarget.dataset.level;
    this.setData({
      difficulty: level
    });
  },

  /**
   * 监听：点击上传素材 (文档/图片)
   */
  handleUpload() {
    wx.chooseMessageFile({
      count: 1, 
      type: 'all', 
      success: (res) => {
        const tempFile = res.tempFiles[0];
        this.uploadFileToServer(tempFile);
      }
    });
  },

  /**
   * 执行文件上传逻辑
   */
  uploadFileToServer(file) {
    wx.showLoading({ title: '上传中...' });
    
    const token = wx.getStorageSync('token');
    // 请确认此处的附件上传实际接口地址，这里我假设前缀为 /api/v1/student
    wx.uploadFile({
      url: 'http://127.0.0.1:8000/api/v1/student/attachments/upload', 
      filePath: file.path,
      name: 'file',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        wx.hideLoading();
        try {
          const result = JSON.parse(res.data);
          if (result.code === 200) {
            const newAttachment = {
              id: result.data.id,
              name: file.name 
            };
            this.setData({
              attachments: [...this.data.attachments, newAttachment]
            });
            wx.showToast({ title: '上传成功', icon: 'success' });
          } else {
            wx.showToast({ title: result.message || '上传失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '解析上传响应失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({ title: '网络异常，上传失败', icon: 'none' });
      }
    });
  },

  /**
   * 监听：删除已上传的附件
   */
  removeAttachment(e) {
    const index = e.currentTarget.dataset.index;
    const newAttachments = [...this.data.attachments];
    newAttachments.splice(index, 1);
    this.setData({
      attachments: newAttachments
    });
  },

  /**
   * 核心逻辑：一键生成练习
   */
  generateQuiz() {
    const { materialText, attachments, questionCount, difficulty, targetBankId, selectedBank, customBankName } = this.data;

    if (!materialText.trim() && attachments.length === 0) {
      wx.showToast({ title: '请填写素材内容或上传附件', icon: 'none' });
      return;
    }

    let backendDifficulty = 'medium';
    if (difficulty === 'basic') backendDifficulty = 'easy';
    if (difficulty === 'advanced') backendDifficulty = 'medium';
    if (difficulty === 'hard') backendDifficulty = 'hard';

    // 动态决定最终提交的题库名
    let finalBankName = '《书途》智能测试题'; 
    if (targetBankId && selectedBank) {
      finalBankName = selectedBank.bank_name; // 选了已有题库
    } else if (customBankName.trim()) {
      finalBankName = customBankName.trim(); // 填了自定义新建名称
    }

    const formData = {
      session_id: 1, 
      bank_name: finalBankName, 
      content: materialText.trim(),
      attachment_ids: JSON.stringify(attachments.map(item => item.id)), 
      question_count: questionCount,
      difficulty: backendDifficulty,
      question_types: 'single_choice,multi_choice,essay',
      model_name: 'deepseek-ai/DeepSeek-V3' 
    };

    if (targetBankId) {
      formData.target_bank_id = targetBankId;
    }

    wx.showLoading({ title: 'AI 正在出题中...', mask: true });
    const token = wx.getStorageSync('token');

    wx.request({
      url: 'http://127.0.0.1:8000/api/v1/student/ai/quiz/generate', 
      method: 'POST',
      header: {
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Authorization': `Bearer ${token}`
      },
      data: formData,
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200 && res.data.code === 200) {
          wx.showToast({ title: '生成成功！', icon: 'success' });
          setTimeout(() => {
            wx.navigateBack(); 
          }, 1500);
        } else {
          // 拦截 429 限流报错
          let errorMsg = res.data.message || '生成失败，请稍后重试';
          if (errorMsg.includes('429') || errorMsg.includes('too busy')) {
            errorMsg = 'AI 思考的人太多啦，系统有点拥挤，请稍后重试~';
          }
          wx.showToast({ 
            title: errorMsg, 
            icon: 'none', 
            duration: 3000 
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({ title: '网络请求超时或失败', icon: 'none' });
      }
    });
  }
});