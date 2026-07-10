const util = require('../../utils/util.js');
const app = getApp();
// ⚠️ 请确保这里是您真实的后端地址
const BASE_URL = app.globalData.baseUrl || 'http://127.0.0.1:8000'; 

Page({
  data: {
    questionText: '',
    uploadedFiles: [],      // 存放文件显示信息
    parsedAttachmentIds: [], // 存放传给后端的附件 ID
    isLoading: false,
    messageList: [],
    userInfo: {},
    currentSessionId: null,
    scrollToId: '',
    isFavorited: false,     // 收藏状态
    isLoadingFav: false     // 防止防抖
  },

  onLoad(options) {
    this.setData({ userInfo: app.globalData.userInfo });
    if (options.sessionId) {
      this.setData({ currentSessionId: options.sessionId });
      this.fetchHistory(options.sessionId);
      this.checkFavoriteStatus(options.sessionId); // 初始化查状态
    }
  },

  onShow() {
    // 页面显示时同步状态
    if (this.data.currentSessionId) {
      this.checkFavoriteStatus(this.data.currentSessionId);
    }
  },

  // 获取收藏状态方法
  async checkFavoriteStatus(sessionId) {
    try {
      const res = await util.request('/api/v1/student/favorites/status', 'GET', {
        content_type: 'session', 
        content_id: sessionId
      });
      if (res && res.is_favorited !== undefined) {
        this.setData({ isFavorited: res.is_favorited });
      }
    } catch (e) {
      console.error('获取收藏状态失败', e);
    }
  },

  // 点击收藏/取消方法
  async toggleFavorite() {
    if (!this.data.currentSessionId || this.data.isLoadingFav) return;
    this.setData({ isLoadingFav: true });

    const endpoint = this.data.isFavorited ? '/api/v1/student/favorites/remove' : '/api/v1/student/favorites/add';

    try {
      await util.request(endpoint, 'POST', {
        content_type: 'session', 
        content_id: this.data.currentSessionId
      });
      this.setData({ isFavorited: !this.data.isFavorited });
      wx.showToast({ title: this.data.isFavorited ? '已收藏' : '已取消', icon: 'success' });
    } catch (e) {
      wx.showToast({ title: '操作失败', icon: 'none' });
    } finally {
      this.setData({ isLoadingFav: false });
    }
  },

  async fetchHistory(sessionId) {
    wx.showLoading({ title: '加载讲堂记录...' });
    try {
      const res = await util.request(`/api/v1/student/ai/explain/history?session_id=${sessionId}`, 'GET');
      const historyList = (res || []).map(msg => {
        let item = {
          id: msg.id || ('msg_' + Date.now() + Math.random()),
          role: msg.role === 'assistant' ? 'ai' : 'user', 
          content: msg.content
        };
        if (item.role === 'ai') item.htmlNodes = this.formatMarkdown(item.content);
        return item;
      });

      this.setData({ 
        messageList: historyList,
        scrollToId: historyList.length > 0 ? `msg-${historyList[historyList.length - 1].id}` : ''
      });
    } catch (e) {
      console.error('加载历史记录失败', e);
    } finally {
      wx.hideLoading();
    }
  },

  onInput(e) {
    this.setData({ questionText: e.detail.value });
  },

  // ================= 文件上传模块 =================
  uploadDoc() {
    wx.chooseMessageFile({
      count: 5, // 允许选择多个附件
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
          } else {
            wx.showToast({ title: data.message || '上传失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '服务器异常', icon: 'none' });
        }
      },
      fail() {
        wx.hideLoading();
        wx.showToast({ title: '网络错误', icon: 'none' });
      }
    });
  },

  removeFile(e) {
    const index = e.currentTarget.dataset.index;
    const files = [...this.data.uploadedFiles];
    const ids = [...this.data.parsedAttachmentIds];
    files.splice(index, 1);
    ids.splice(index, 1);
    this.setData({ uploadedFiles: files, parsedAttachmentIds: ids });
  },

  // ================= 工具方法 =================
  copyText(e) {
    const text = e.currentTarget.dataset.text;
    if (!text) return;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '已复制解答', icon: 'success' })
    });
  },

  formatMarkdown(text) {
    if (!text) return '';
    let html = text;
    html = html.replace(/```[a-z]*/gi, '');
    html = html.replace(/^### (.*$)/gim, '<div style="font-size: 30rpx; font-weight: bold; color: #333; margin-top: 24rpx; margin-bottom: 12rpx;">$1</div>');
    html = html.replace(/^## (.*$)/gim, '<div style="font-size: 32rpx; font-weight: bold; color: #2b85e4; margin-top: 28rpx; margin-bottom: 12rpx;">$1</div>');
    html = html.replace(/^# (.*$)/gim, '<div style="font-size: 36rpx; font-weight: bold; color: #333; margin-top: 32rpx; margin-bottom: 16rpx;">$1</div>');
    html = html.replace(/^\s*[-*_]{3,}\s*$/gim, '<hr style="border: none; border-top: 2rpx dashed #dcdcdc; margin: 30rpx 0;" />');
    html = html.replace(/^\>\s+(.*$)/gim, '<div style="border-left: 6rpx solid #a3e4b7; padding-left: 16rpx; color: #666; margin: 10rpx 0; background: #f0fdf4; padding: 10rpx 16rpx; border-radius: 4rpx;">$1</div>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #333; font-weight: bold;">$1</strong>');
    html = html.replace(/^(\d+\.)\s+(.*$)/gim, '<div style="margin-top: 12rpx; margin-bottom: 8rpx;"><strong style="color:#2b85e4; margin-right: 8rpx;">$1</strong> $2</div>');
    html = html.replace(/^[\-\*]\s+(.*$)/gim, '<div style="padding-left: 24rpx; position: relative; margin-top: 6rpx;"><span style="position: absolute; left: 0; color: #2b85e4;">•</span>$1</div>');
    html = html.replace(/\n/g, '<br/>');
    return html;
  },

  // ================= 核心提交流程 =================
  async submitQuestion() {
    const text = this.data.questionText.trim();
    const files = this.data.uploadedFiles;
    const attachmentIds = this.data.parsedAttachmentIds;

    if ((!text && files.length === 0) || this.data.isLoading) return;

    if (!this.data.currentSessionId) {
      wx.showLoading({ title: '初始化专属讲堂...' });
      try {
        const titleText = text ? text.substring(0, 10) : files[0].name;
        const sessionRes = await util.request('/api/v1/student/sessions/', 'POST', {
          title: titleText + '...', 
          task_type: 'explain' 
        });
        this.setData({ currentSessionId: sessionRes.id });
        wx.hideLoading();
      } catch (err) {
        wx.hideLoading();
        wx.showToast({ title: '会话创建失败', icon: 'none' });
        return;
      }
    }

    // 在用户气泡中展示包含了哪些附件
    let displayContent = text;
    if (files.length > 0) {
      const fileNames = files.map(f => f.name).join(', ');
      displayContent = `[附件: ${fileNames}]\n${text}`;
    }

    const userMsg = { id: 'u_' + Date.now(), role: 'user', content: displayContent };
    const aiMsgId = 'ai_' + Date.now();
    const initialAiMsg = { id: aiMsgId, role: 'ai', content: '', htmlNodes: '' };

    this.setData({
      messageList: [...this.data.messageList, userMsg, initialAiMsg],
      questionText: '', 
      uploadedFiles: [], // 发送后清空待发送队列
      parsedAttachmentIds: [],
      isLoading: true,
      scrollToId: `msg-${userMsg.id}`
    });

    this.startStreaming(text, attachmentIds, aiMsgId);
  },

  startStreaming(userText, attachmentIds, aiMsgId) {
    const token = wx.getStorageSync('token');
    let buffer = ''; 

    const requestTask = wx.request({
      url: `${BASE_URL}/api/v1/student/ai/explain/stream`, 
      method: 'POST', 
      enableChunked: true,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        session_id: this.data.currentSessionId,
        question: userText,
        // 👇 直接传递数组变量即可，去掉前一步骤加的 JSON.stringify()
        attachment_ids: attachmentIds 
      },
      success: () => {
        this.setData({ isLoading: false });
      },
      fail: (err) => {
        console.error('流式请求失败:', err);
        this.appendChunkToMessage(aiMsgId, '\n[网络连接中断，请重试]');
        this.setData({ isLoading: false });
      }
    });

    requestTask.onChunkReceived((response) => {
      const chunkText = new TextDecoder('utf-8').decode(response.data);
      buffer += chunkText;

      let parts = buffer.split('\n\n');
      buffer = parts.pop(); 

      for (let part of parts) {
        if (part.startsWith('data: ')) {
          let dataStr = part.substring(6).trim(); 
          if (dataStr === '[DONE]') {
            this.setData({ isLoading: false });
            return;
          }
          try {
            let dataObj = JSON.parse(dataStr);
            if (dataObj.content) {
              this.appendChunkToMessage(aiMsgId, dataObj.content);
            }
          } catch (err) {}
        }
      }
    });
  },

  appendChunkToMessage(msgId, chunk) {
    const messages = this.data.messageList;
    const targetIndex = messages.findIndex(m => m.id === msgId);
    
    if (targetIndex !== -1) {
      messages[targetIndex].content += chunk;
      if (messages[targetIndex].role === 'ai') {
        messages[targetIndex].htmlNodes = this.formatMarkdown(messages[targetIndex].content);
      }
      this.setData({ 
        messageList: messages,
        scrollToId: `msg-${msgId}` 
      });
    }
  }
})