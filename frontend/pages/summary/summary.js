const util = require('../../utils/util.js');
const app = getApp();
// ⚠️ 确保替换为真实后端地址
const BASE_URL = 'http://127.0.0.1:8000'; 

Page({
  data: {
    inputText: '',
    fileName: '',
    fileId: null,
    isLoading: false,
    messageList: [],
    userInfo: {},
    currentSessionId: null,
    scrollToId: '',
    isFavorited: false,  // 记录当前会话是否被收藏
    isLoadingFav: false  // 防止用户连续点击收藏按钮
  },

  onLoad(options) {
    this.setData({ userInfo: app.globalData.userInfo });
    
    // 从历史记录进入时恢复聊天
    if (options.sessionId) {
      this.setData({ currentSessionId: options.sessionId });
      this.fetchSessionHistory(options.sessionId);
      this.checkFavoriteStatus(options.sessionId); // 检查收藏状态
    }
  },

  onInput(e) {
    this.setData({ inputText: e.detail.value });
  },

  uploadDoc() {
    wx.chooseMessageFile({
      count: 1,
      type: 'all',
      success: (res) => {
        const file = res.tempFiles[0];
        this.setData({ fileName: file.name });
      }
    });
  },

  removeFile() {
    this.setData({ fileName: '', fileId: null });
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

  async fetchSessionHistory(sessionId) {
    wx.showLoading({ title: '恢复记忆中...' });
    try {
      const res = await util.request(`/api/v1/student/messages/session/${sessionId}`, 'GET');
      
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

  async generateSummary() {
    const text = this.data.inputText.trim();
    const fileName = this.data.fileName;
    
    if ((!text && !fileName) || this.data.isLoading) return;

    if (!this.data.currentSessionId) {
      wx.showLoading({ title: '准备工作台...' });
      try {
        const titleText = text ? text.substring(0, 10) : fileName;
        const sessionRes = await util.request('/api/v1/student/sessions/', 'POST', {
          title: titleText + '...', 
          task_type: 'summary' 
        });
        this.setData({ 
          currentSessionId: sessionRes.id,
          isFavorited: false // 新建会话默认未收藏
        });
        wx.hideLoading();
      } catch (err) {
        wx.hideLoading();
        wx.showToast({ title: '会话创建失败', icon: 'none' });
        return;
      }
    }

    let displayContent = text;
    if (fileName) {
      displayContent = `[附件: ${fileName}]\n${text}`;
    }

    const userMsg = { id: 'u_' + Date.now(), role: 'user', content: displayContent };
    const aiMsgId = 'ai_' + Date.now();
    const initialAiMsg = { id: aiMsgId, role: 'ai', content: '', htmlNodes: '' };

    this.setData({
      messageList: [...this.data.messageList, userMsg, initialAiMsg],
      inputText: '', 
      isLoading: true,
      scrollToId: `msg-${userMsg.id}`
    });

    this.startStreaming(text, aiMsgId);
  },

  startStreaming(userText, aiMsgId) {
    const token = wx.getStorageSync('token');
    let buffer = ''; 

    const requestTask = wx.request({
      url: `${BASE_URL}/api/v1/student/ai/summary/stream`, 
      method: 'POST', 
      enableChunked: true,
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: {
        session_id: this.data.currentSessionId,
        content: userText 
      },
      success: () => {
        this.setData({ isLoading: false });
      },
      fail: (err) => {
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
  },

  // 检查当前会话的收藏状态
  async checkFavoriteStatus(sessionId) {
    try {
      const res = await util.request('/api/v1/student/favorites/status', 'GET', {
        content_type: 'session', 
        content_id: sessionId
      });
      this.setData({ 
        isFavorited: res.data ? res.data.is_favorited : false 
      });
    } catch (error) {
      console.error('获取收藏状态失败', error);
    }
  },

  // 点击切换收藏状态
  async toggleFavorite() {
    if (!this.data.currentSessionId || this.data.isLoadingFav) return;
    this.setData({ isLoadingFav: true });

    try {
      const res = await util.request('/api/v1/student/favorites/toggle', 'POST', {
        content_type: 'session', 
        content_id: this.data.currentSessionId
      });

      const isFav = res.data.action === 'added';
      this.setData({ isFavorited: isFav });
      
      wx.showToast({ 
        title: isFav ? '已加入收藏' : '已取消收藏', 
        icon: 'success' 
      });
    } catch (error) {
      wx.showToast({ title: '操作失败', icon: 'none' });
    } finally {
      this.setData({ isLoadingFav: false });
    }
  }
})