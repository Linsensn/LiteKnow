const app = getApp();
// ⚠️ 替换为您真实的后端开发地址
const BASE_URL = app.globalData.baseUrl || 'http://127.0.0.1:8000'; 

Page({
  data: {
    bankName: '',
    rawText: '',
    
    uploadedFiles: [],      // 存放文件显示信息 [{ id: 1, name: 'abc.pdf' }]
    parsedAttachmentIds: [], // 存放传给后端的附件 ID 数组
    
    isUploading: false
  },

  // 监听输入
  onBankNameInput(e) {
    this.setData({ bankName: e.detail.value });
  },
  
  onTextInput(e) {
    this.setData({ rawText: e.detail.value });
  },

  // 选择并上传文档/图片
  uploadDoc() {
    wx.chooseMessageFile({
      count: 9, // 允许多选
      type: 'all',
      success: (res) => {
        const files = res.tempFiles;
        files.forEach(file => {
          if (file.size > 10 * 1024 * 1024) {
            wx.showToast({ title: `文件 ${file.name} 超过10MB`, icon: 'none' });
          } else {
            this.uploadToServer(file);
          }
        });
      }
    });
  },

  // 上传至服务器并获取附件 ID
  uploadToServer(file) {
    const that = this;
    wx.showLoading({ title: '上传解析中...', mask: true });
    const token = wx.getStorageSync('token');

    wx.uploadFile({
      url: `${BASE_URL}/api/v1/student/attachments/upload`,
      filePath: file.path,
      name: 'file', 
      header: { 'Authorization': `Bearer ${token}` },
      success(res) {
        wx.hideLoading();
        try {
          const data = JSON.parse(res.data);
          if (data.code === 0 || data.code === 200) {
            const attachment = data.data;
            that.setData({
              uploadedFiles: [...that.data.uploadedFiles, { id: attachment.id, name: file.name }],
              parsedAttachmentIds: [...that.data.parsedAttachmentIds, attachment.id]
            });
            wx.showToast({ title: '添加成功', icon: 'success' });
          } else {
            wx.showToast({ title: data.message || '上传失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '服务器响应异常', icon: 'none' });
        }
      },
      fail(err) {
        wx.hideLoading();
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  // 移除附件
  removeFile(e) {
    const index = e.currentTarget.dataset.index;
    const files = [...this.data.uploadedFiles];
    const ids = [...this.data.parsedAttachmentIds];
    files.splice(index, 1);
    ids.splice(index, 1);
    this.setData({ uploadedFiles: files, parsedAttachmentIds: ids });
  },

  // ========================== 核心提交流程 ==========================
  submitRecognize() {
    const { bankName, rawText, parsedAttachmentIds } = this.data;
    
    if (!bankName.trim()) {
      return wx.showToast({ title: '请填写题库名称', icon: 'none' });
    }
    if (!rawText.trim() && parsedAttachmentIds.length === 0) {
      return wx.showToast({ title: '请粘贴文本或上传题目文件', icon: 'none' });
    }

    this.setData({ isUploading: true });
    wx.showLoading({ title: 'AI 题库生成中...', mask: true });
    const token = wx.getStorageSync('token');

    wx.request({
      url: `${BASE_URL}/api/v1/student/ai/bank/parse`, 
      method: 'POST',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        bank_name: bankName.trim(),
        content: rawText.trim(),
        // ⚠️ 假设你的 schema 需要 JSON 字符串，如果直接接收数组则去掉 JSON.stringify
        attachment_ids: JSON.stringify(parsedAttachmentIds) 
      },
      success: (res) => {
        wx.hideLoading();
        // 判断 HTTP 状态码以及是否返回了 data
        if (res.statusCode === 200 && res.data && res.data.code === 200) {
          wx.showToast({ title: '题库生成成功！', icon: 'success' });
          this.setData({ bankName: '', rawText: '', uploadedFiles: [], parsedAttachmentIds: [] });
          this.handleSuccess();
        } else {
          wx.showToast({ title: res.data.message || '解析失败，请检查格式', icon: 'none' });
        }
      },
      fail: () => {
        wx.hideLoading();
        wx.showToast({ title: '请求超时或失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ isUploading: false });
      }
    });
  },

  // 处理成功后的跳转逻辑
  handleSuccess() {
    setTimeout(() => {
      wx.navigateBack({
        delta: 1,
        fail: () => {
          wx.navigateTo({ url: '/pages/bankList/bankList' });
        }
      });
    }, 1500);
  }
})