const util = require('../../utils/util.js');
const app = getApp();
// ⚠️ 确保替换为真实后端地址
const BASE_URL = app.globalData.baseUrl || 'http://127.0.0.1:8000'; 

Page({
  data: {
    inputText: '',
    uploadedFiles: [],      // 存放文件显示信息 [{ id: 1, name: 'abc.pdf' }]
    parsedAttachmentIds: [], // 存放传给后端的附件 ID 数组
    isLoading: false,
    messageList: [],
    userInfo: {},
    currentSessionId: null,
    scrollToId: '',
    isFavorited: false,     // 收藏状态
    isLoadingFav: false     // 防止重复点击收藏
  },

  onLoad(options) {
    this.setData({ userInfo: app.globalData.userInfo });
    
    // 从历史记录进入时恢复聊天
    if (options.sessionId) {
      this.setData({ currentSessionId: options.sessionId });
      this.fetchSessionHistory(options.sessionId);
    }
  },

  onShow() {
    // 每次进入页面时，实时同步收藏状态，确保星星准确
    if (this.data.currentSessionId) {
      this.checkFavoriteStatus(this.data.currentSessionId);
    }
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value });
  },

  // 选择并上传文档
  uploadDoc() {
    wx.chooseMessageFile({
      count: 1,
      type: 'all',
      success: (res) => {
        const file = res.tempFiles[0];
        if (file.size > 10 * 1024 * 1024) {
          return wx.showToast({ title: '文件不能超过10MB', icon: 'none' });
        }
        this.uploadToServer(file);
      }
    });
  },

  // 核心：上传至服务器并获取解析 ID
  uploadToServer(file) {
    const that = this;
    wx.showLoading({ title: '上传并解析中...', mask: true });
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
            wx.showToast({ title: '上传成功', icon: 'success' });
          } else {
            wx.showToast({ title: data.message || '上传失败', icon: 'none' });
          }
        } catch (e) {
          wx.showToast({ title: '服务器响应异常', icon: 'none' });
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

  copyText(e) {
    const text = e.currentTarget.dataset.text;
    if (!text) return;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '已复制摘要', icon: 'success' })
    });
  },

  formatMarkdown(text) {
    if (!text) return '';
    let html = text.replace(/```[a-z]*/gi, '');
    html = html.replace(/^### (.*$)/gim, '<div style="font-weight:bold; margin-top:20rpx;">$1</div>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color:#333;">$1</strong>');
    html = html.replace(/\n/g, '<br/>');
    return html;
  },

  async fetchSessionHistory(sessionId) {
    wx.showLoading({ title: '恢复记忆中...' });
    try {
      const res = await util.request(`/api/v1/student/messages/session/${sessionId}`, 'GET');
      const historyList = (res || []).map(msg => ({
        id: msg.id || ('msg_' + Date.now()),
        role: msg.role === 'assistant' ? 'ai' : 'user', 
        content: msg.content,
        htmlNodes: msg.role === 'assistant' ? this.formatMarkdown(msg.content) : ''
      }));
      this.setData({ messageList: historyList });
    } catch (e) {
      console.error('加载历史记录失败', e);
    } finally {
      wx.hideLoading();
    }
  },

  async generateSummary() {
    const text = this.data.inputText.trim();
    const attachmentIds = this.data.parsedAttachmentIds;
    
    if ((!text && attachmentIds.length === 0) || this.data.isLoading) return;

    if (!this.data.currentSessionId) {
      wx.showLoading({ title: '准备工作台...' });
      try {
        const sessionRes = await util.request('/api/v1/student/sessions/', 'POST', {
          title: text.substring(0, 10) + '...', 
          task_type: 'summary' 
        });
        this.setData({ currentSessionId: sessionRes.id });
        wx.hideLoading();
      } catch (err) {
        wx.hideLoading();
        wx.showToast({ title: '会话创建失败', icon: 'none' });
        return;
      }
    }

    const userMsg = { id: 'u_' + Date.now(), role: 'user', content: text };
    const aiMsgId = 'ai_' + Date.now();
    this.setData({
      messageList: [...this.data.messageList, userMsg, { id: aiMsgId, role: 'ai', content: '' }],
      inputText: '', 
      uploadedFiles: [],
      parsedAttachmentIds: [],
      isLoading: true
    });

    this.startStreaming(text, attachmentIds, aiMsgId);
  },

  startStreaming(userText, attachmentIds, aiMsgId) {
    const token = wx.getStorageSync('token');
    let buffer = ''; 
    const requestTask = wx.request({
      url: `${BASE_URL}/api/v1/student/ai/summary/stream`, 
      method: 'POST', 
      enableChunked: true,
      header: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      data: {
        session_id: this.data.currentSessionId,
        content: userText,
        attachment_ids: JSON.stringify(attachmentIds) 
      },
      success: () => { this.setData({ isLoading: false }); },
      fail: () => { this.setData({ isLoading: false }); }
    });

    requestTask.onChunkReceived((res) => {
      const chunkText = new TextDecoder('utf-8').decode(res.data);
      buffer += chunkText;
      let parts = buffer.split('\n\n');
      buffer = parts.pop(); 
      parts.forEach(part => {
        if (part.startsWith('data: ')) {
          let dataStr = part.substring(6).trim();
          if (dataStr === '[DONE]') return;
          try {
            let data = JSON.parse(dataStr);
            if (data.content) this.appendChunkToMessage(aiMsgId, data.content);
          } catch (e) {}
        }
      });
    });
  },

  appendChunkToMessage(msgId, chunk) {
    const messages = this.data.messageList;
    const idx = messages.findIndex(m => m.id === msgId);
    if (idx !== -1) {
      messages[idx].content += chunk;
      messages[idx].htmlNodes = this.formatMarkdown(messages[idx].content);
      this.setData({ messageList: messages });
    }
  },

  // 检查收藏状态
  async checkFavoriteStatus(sessionId) {
    try {
      const res = await util.request('/api/v1/student/favorites/status', 'GET', {
        content_type: 'session', 
        content_id: sessionId
      });
      // ✨ 在这里添加日志
      console.log('--- 收藏状态接口返回 ---');
      console.log('传入的 sessionId:', sessionId);
      console.log('后端返回的 res:', res);
      
      this.setData({ 
        isFavorited: res.data ? res.data.is_favorited : false 
      });
    } catch (error) {
      console.error('获取收藏状态失败', error);
    }
  },

  // 点击收藏/取消
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
  }
})