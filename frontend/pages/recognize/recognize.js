const app = getApp();
// ⚠️ 替换为您真实的后端开发地址
const BASE_URL = 'http://127.0.0.1:8000'; 

Page({
  data: {
    activeTab: 'file',  // 当前模式: 'file' | 'text'
    
    // 文件模式状态
    tempFilePath: '',   
    fileName: '',       
    fileCategory: '',   
    
    // 文本模式状态
    bankName: '',
    rawText: '',

    isUploading: false
  },

  // 切换模式
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    if (this.data.isUploading) return; // 正在上传时禁止切换
    this.setData({ activeTab: tab });
  },

  // ========================== 文件上传逻辑 ==========================
  showFilePicker() {
    wx.showActionSheet({
      itemList: ['拍照或从相册选择图片', '从微信聊天选择 PDF 文件'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.pickImage();
        } else if (res.tapIndex === 1) {
          this.pickDocument();
        }
      }
    });
  },

  pickImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed'],
      success: (res) => {
        const file = res.tempFiles[0];
        if (this.checkFileSize(file.size)) {
          this.setData({
            tempFilePath: file.tempFilePath,
            fileCategory: 'image',
            fileName: '图片文件.jpg'
          });
        }
      }
    });
  },

  pickDocument() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf'], 
      success: (res) => {
        const file = res.tempFiles[0];
        if (this.checkFileSize(file.size)) {
          this.setData({
            tempFilePath: file.path,
            fileCategory: 'doc',
            fileName: file.name
          });
        }
      }
    });
  },

  checkFileSize(size) {
    if (size > 10 * 1024 * 1024) {
      wx.showToast({ title: '文件大小不能超过10MB', icon: 'none' });
      return false;
    }
    return true;
  },

  clearFile() {
    this.setData({ tempFilePath: '', fileName: '', fileCategory: '' });
  },

  // ========================== 核心提交流程 ==========================
  submitRecognize() {
    if (this.data.activeTab === 'file') {
      this.submitFileTask();
    } else {
      this.submitTextTask();
    }
  },

  // 分支 1：提交文件识别
  submitFileTask() {
    if (!this.data.tempFilePath) return;

    this.setData({ isUploading: true });
    wx.showLoading({ title: 'AI 识别中...', mask: true });
    const token = wx.getStorageSync('token');

    wx.uploadFile({
      url: `${BASE_URL}/api/v1/student/attachments/upload`,
      filePath: this.data.tempFilePath,
      name: 'file', 
      header: { 'Authorization': `Bearer ${token}` },
      success: (res) => {
        wx.hideLoading();
        try {
          const data = JSON.parse(res.data);
          if (data.code === 200) {
            wx.showToast({ title: '识别提取成功！', icon: 'success' });
            this.clearFile();
            this.handleSuccess(data.data);
          } else {
            wx.showToast({ title: data.message || '处理失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '服务器响应异常', icon: 'none' });
        }
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '网络超时', icon: 'none' });
      },
      complete: () => {
        this.setData({ isUploading: false });
      }
    });
  },

  // 分支 2：提交长文本识别
  submitTextTask() {
    const { bankName, rawText } = this.data;
    if (!bankName.trim() || !rawText.trim()) {
      wx.showToast({ title: '请填写题库名称和题目内容', icon: 'none' });
      return;
    }

    this.setData({ isUploading: true });
    wx.showLoading({ title: 'AI 解析中...', mask: true });
    const token = wx.getStorageSync('token');

    wx.request({
      // 🌟 修改点：这里加上了 /student 补全路由前缀
      url: `${BASE_URL}/api/v1/student/ai/bank/parse`, 
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        bank_name: bankName.trim(),
        content: rawText.trim()
      },
      success: (res) => {
        wx.hideLoading();
        // 🌟 修改点：不再判断 res.data.code，而是判断 res.statusCode 以及是否返回了 bank_id
        if (res.statusCode === 200 && res.data && res.data.bank_id) {
          wx.showToast({ title: '题库生成成功！', icon: 'success' });
          this.setData({ bankName: '', rawText: '' });
          this.handleSuccess(res.data);
        } else {
          wx.showToast({ title: res.data.message || '解析失败，请检查文本格式', icon: 'none' });
        }
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '请求失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ isUploading: false });
      }
    });
  },

  // 处理成功后的跳转逻辑
  handleSuccess(resultData) {
    // 延迟后返回，或者跳转到生成的题库页（此处跳转至题库列表）
    setTimeout(() => {
      wx.navigateBack({
        delta: 1,
        fail: () => {
          // 如果是Tabbar页面请使用 wx.switchTab 替代
          wx.navigateTo({ url: '/pages/bankList/bankList' });
        }
      });
    }, 1500);
  }
})