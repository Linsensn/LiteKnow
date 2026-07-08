const util = require('../../utils/util.js');
const app = getApp();
// ⚠️ 请替换为您的真实后端开发域名
const BASE_URL = 'http://127.0.0.1:8000'; 

Page({
  data: {
    sourceText: '',
    fileName: '',
    tempFilePath: '',
    questionCount: 5,
    difficulty: 'easy', // 'easy', 'medium', 'hard'
    bankList: [],       // 存放从后端拉取的真实题库列表
    selectedBankId: null,
    selectedBankName: '',
    isGenerating: false
  },

  onLoad() {
    // 页面加载时，立即获取用户的题库列表，用于填充下拉菜单
    this.fetchMyBanks();
  },

  // 获取真实的题库列表
  async fetchMyBanks() {
    try {
      // 对接之前的 /question-banks 接口
      const res = await util.request('/api/v1/student/question-banks', 'GET', { 
        page_size: 100, sort_by: 'desc' 
      });
      // 注意：根据之前的封装，真实数据在 res.list 里
      const banks = res.list || [];
      this.setData({ bankList: banks });
    } catch (e) {
      console.error('获取题库失败:', e);
    }
  },

  onInput(e) { this.setData({ sourceText: e.detail.value }); },
  onCountChange(e) { this.setData({ questionCount: e.detail.value }); },
  setDifficulty(e) { this.setData({ difficulty: e.currentTarget.dataset.level }); },

  // 用户选择了题库
  onBankChange(e) {
    const index = e.detail.value;
    const selectedBank = this.data.bankList[index];
    this.setData({
      selectedBankId: selectedBank.id,
      selectedBankName: selectedBank.name
    });
  },

  // 调用微信原生 API 选择文件
  uploadMaterial() {
    wx.showActionSheet({
      itemList: ['拍照或从相册选择', '从微信聊天选择文档(PDF)'],
      success: (res) => {
        if (res.tapIndex === 0) {
          wx.chooseMedia({
            count: 1, type: 'image', sizeType: ['compressed'],
            success: (mediaRes) => {
              this.setData({ 
                tempFilePath: mediaRes.tempFiles[0].tempFilePath, 
                fileName: '图片素材.jpg' 
              });
            }
          });
        } else {
          wx.chooseMessageFile({
            count: 1, type: 'file', extension: ['pdf'],
            success: (fileRes) => {
              this.setData({ 
                tempFilePath: fileRes.tempFiles[0].path, 
                fileName: fileRes.tempFiles[0].name 
              });
            }
          });
        }
      }
    });
  },

  // ✨ 核心：生成测验与练习会话
  async generateQuiz() {
    if (!this.data.sourceText && !this.data.tempFilePath) {
      return wx.showToast({ title: '请提供一段文字或上传素材', icon: 'none' });
    }
    if (!this.data.selectedBankId) {
      return wx.showToast({ title: '请选择要保存到的题库', icon: 'none' });
    }

    this.setData({ isGenerating: true });
    wx.showLoading({ title: 'AI 疯狂出题中...', mask: true });

    try {
      let attachmentId = null;

      // 步骤 1: 如果有文件，调用之前的真实附件上传接口
      if (this.data.tempFilePath) {
        const token = wx.getStorageSync('token');
        const uploadRes = await new Promise((resolve, reject) => {
          wx.uploadFile({
            url: `${BASE_URL}/api/v1/student/attachments/upload`,
            filePath: this.data.tempFilePath,
            name: 'file',
            header: { 'Authorization': `Bearer ${token}` },
            success: res => resolve(JSON.parse(res.data)),
            fail: err => reject(err)
          });
        });
        if (uploadRes.code === 200) {
          attachmentId = uploadRes.data.id;
        }
      }

      // 步骤 2: 呼叫 AI 引擎出题！
      // ⚠️ 这里需要后端提供一个大模型出题的接口。
      // 因为没看到 AI 生成相关的 router，所以这里用前端 setTimeout 模拟了 AI 的耗时
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 假设这是 AI 返回的 5 道新题目的 ID（已经自动被后端塞进了数据库）
      const generatedQuestionIds = [1001, 1002, 1003, 1004, 1005].slice(0, this.data.questionCount);

      // 步骤 3: 完美对接您刚才提供的 PracticeSessionCreate Schema！
      const practicePayload = {
        bank_id: this.data.selectedBankId,
        practice_mode: 'mock', // 模拟练习模式
        question_sequence: generatedQuestionIds
      };

      const sessionRes = await util.request('/api/v1/student/practice-sessions', 'POST', practicePayload);

      wx.hideLoading();
      wx.showToast({ title: '练习生成成功！', icon: 'success' });

      // 步骤 4: 拿着后端返回的真实 Practice Session ID，跳转到正式的刷题页面
      setTimeout(() => {
        // 跳转并带上会话 ID (页面待开发)
        wx.navigateTo({ url: `/pages/doPractice/doPractice?sessionId=${sessionRes.id}` });
        this.setData({ isGenerating: false });
      }, 1500);

    } catch (error) {
      console.error('出题流程失败:', error);
      wx.hideLoading();
      wx.showToast({ title: '生成失败，请重试', icon: 'none' });
      this.setData({ isGenerating: false });
    }
  }
})