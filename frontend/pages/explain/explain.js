const util = require('../../utils/util.js');
const app = getApp();
// ⚠️ 请确保这里是您真实的后端地址
const BASE_URL = 'http://127.0.0.1:8000'; 

Page({
  data: {
    questionText: '',
    isLoading: false,
    messageList: [],
    userInfo: {},
    currentSessionId: null,
    scrollToId: '' // 用于让 scroll-view 自动滚动到特定气泡的 ID
  },

  onLoad(options) {
    this.setData({ userInfo: app.globalData.userInfo });
    
    // 如果是从历史记录点进来的，自动加载曾经的聊天内容
    if (options.sessionId) {
      this.setData({ currentSessionId: options.sessionId });
      this.fetchHistory(options.sessionId);
    }
  },

  // 拉取后端的历史记录接口
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
        // 如果是 AI 回复，顺便把它解析成精美的富文本
        if (item.role === 'ai') {
          item.htmlNodes = this.formatMarkdown(item.content);
        }
        return item;
      });

      this.setData({ 
        messageList: historyList,
        // 如果有历史记录，直接滚动到最后一条
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

  // 一键复制文本方法
  copyText(e) {
    const text = e.currentTarget.dataset.text;
    if (!text) return;
    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({ title: '已复制解答', icon: 'success' });
      }
    });
  },

  // 加强版 Markdown 转 HTML 解析器
  formatMarkdown(text) {
    if (!text) return '';
    let html = text;
    
    // 过滤代码块标记
    html = html.replace(/```[a-z]*/gi, '');

    // 解析标题
    html = html.replace(/^### (.*$)/gim, '<div style="font-size: 30rpx; font-weight: bold; color: #333; margin-top: 24rpx; margin-bottom: 12rpx;">$1</div>');
    html = html.replace(/^## (.*$)/gim, '<div style="font-size: 32rpx; font-weight: bold; color: #2b85e4; margin-top: 28rpx; margin-bottom: 12rpx;">$1</div>');
    html = html.replace(/^# (.*$)/gim, '<div style="font-size: 36rpx; font-weight: bold; color: #333; margin-top: 32rpx; margin-bottom: 16rpx;">$1</div>');

    // 完美解析 --- 分割线
    html = html.replace(/^\s*[-*_]{3,}\s*$/gim, '<hr style="border: none; border-top: 2rpx dashed #dcdcdc; margin: 30rpx 0;" />');

    // 解析块级引用 (>)
    html = html.replace(/^\>\s+(.*$)/gim, '<div style="border-left: 6rpx solid #a3e4b7; padding-left: 16rpx; color: #666; margin: 10rpx 0; background: #f0fdf4; padding: 10rpx 16rpx; border-radius: 4rpx;">$1</div>');

    // 解析加粗
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #333; font-weight: bold;">$1</strong>');

    // 优雅处理有序列表 (1. 2.)，突出数字
    html = html.replace(/^(\d+\.)\s+(.*$)/gim, '<div style="margin-top: 12rpx; margin-bottom: 8rpx;"><strong style="color:#2b85e4; margin-right: 8rpx;">$1</strong> $2</div>');

    // 无序列表的小圆点
    html = html.replace(/^[\-\*]\s+(.*$)/gim, '<div style="padding-left: 24rpx; position: relative; margin-top: 6rpx;"><span style="position: absolute; left: 0; color: #2b85e4;">•</span>$1</div>');

    // 换行符转换为 <br/>
    html = html.replace(/\n/g, '<br/>');
    return html;
  },

  async submitQuestion() {
    const text = this.data.questionText.trim();
    if (!text || this.data.isLoading) return;

    if (!this.data.currentSessionId) {
      wx.showLoading({ title: '初始化专属讲堂...' });
      try {
        const sessionRes = await util.request('/api/v1/student/sessions/', 'POST', {
          title: text.substring(0, 10) + '...', 
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

    const userMsg = { id: 'u_' + Date.now(), role: 'user', content: text };
    const aiMsgId = 'ai_' + Date.now();
    const initialAiMsg = { id: aiMsgId, role: 'ai', content: '', htmlNodes: '' };

    this.setData({
      messageList: [...this.data.messageList, userMsg, initialAiMsg],
      questionText: '', 
      isLoading: true,
      // 提问时立刻滚动到最新的用户气泡
      scrollToId: `msg-${userMsg.id}`
    });

    this.startStreaming(text, aiMsgId);
  },

  // 发起打字机流式请求
  startStreaming(userText, aiMsgId) {
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
        question: userText 
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
          } catch (err) {
            console.error('解析 JSON 失败:', err, dataStr);
          }
        }
      }
    });
  },

  // 渲染气泡并自动滚动
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
        // 将视图直接滚动到当前正在生成的 AI 气泡
        scrollToId: `msg-${msgId}` 
      });
    }
  }
})