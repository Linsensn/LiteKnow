// pages/adminUserDetail/adminUserDetail.js
const util = require('../../utils/util.js');

// --- 轻量级 Markdown 转 HTML 引擎 (专为微信 rich-text 优化) ---
function parseMarkdownToHtml(md) {
  if (!md) return '无内容';
  if (typeof md !== 'string') md = JSON.stringify(md);
  
  let html = md;
  // 1. 转义基本的HTML标签，防止错乱
  html = html.replace(/</g, '&lt;').replace(/>/g, '&gt;');
  
  // 2. 代码块 (带深色背景和滚动)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, function(match, lang, code) {
    return `<pre style="background:#282c34; color:#abb2bf; padding:20rpx; border-radius:12rpx; overflow-x:auto; margin:16rpx 0; font-size:24rpx; white-space:pre-wrap; word-wrap:break-word;"><code>${code}</code></pre>`;
  });
  
  // 3. 行内代码
  html = html.replace(/`([^`]+)`/g, '<code style="background:#f0f0f0; color:#e83e8c; padding:4rpx 8rpx; border-radius:8rpx; font-size:26rpx; margin:0 4rpx;">$1</code>');
  
  // 4. 标题 (H1-H4)
  html = html.replace(/^#### (.*$)/gim, '<h4 style="margin:24rpx 0 12rpx 0; font-size:30rpx; font-weight:bold; color:#333;">$1</h4>');
  html = html.replace(/^### (.*$)/gim, '<h3 style="margin:24rpx 0 12rpx 0; font-size:32rpx; font-weight:bold; color:#333;">$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2 style="margin:32rpx 0 16rpx 0; font-size:36rpx; font-weight:bold; color:#333; border-bottom:1px solid #eee; padding-bottom:8rpx;">$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1 style="margin:36rpx 0 18rpx 0; font-size:42rpx; font-weight:bold; color:#333;">$1</h1>');
  
  // 5. 加粗和斜体
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight:bold; color:#222;">$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em style="font-style:italic; color:#555;">$1</em>');
  
  // 6. 无序列表
  html = html.replace(/^[-*] (.*$)/gim, '<div style="margin-left:20rpx; padding-left:16rpx; margin-bottom:8rpx; border-left:4rpx solid #007aff;">$1</div>');
  
  // 7. 换行处理
  html = html.split('\n').join('<br/>');
  
  // 8. 修复代码块内部被替换成<br/>的换行
  html = html.replace(/(<pre.*?><code>)([\s\S]*?)(<\/code><\/pre>)/g, function(match, start, content, end) {
    return start + content.replace(/<br\/>/g, '\n') + end;
  });

  return `<div style="font-size:28rpx; line-height:1.7; color:#444; word-break:break-all;">${html}</div>`;
}
// -------------------------------------------------------------

Page({
  data: {
    userId: null,
    userInfo: null,
    activeTab: 0,
    sessions: [],
    favorites: [],
    banks: [],
    isLoading: false,
    
    showDetailModal: false,
    detailModalTitle: '',
    detailModalHtml: '' 
  },

  onLoad(options) {
    const userId = options.userId;
    if (userId) {
      this.setData({ userId: parseInt(userId) });
      this.fetchUserInfo();
    } else {
      wx.showToast({ title: '缺少用户参数', icon: 'none' });
    }
  },

  switchTab(e) {
    const index = parseInt(e.currentTarget.dataset.index);
    this.setData({ activeTab: index });
    if (index === 1 && this.data.sessions.length === 0) this.fetchSessions();
    else if (index === 2 && this.data.favorites.length === 0) this.fetchFavorites();
    else if (index === 3 && this.data.banks.length === 0) this.fetchUserBanks();
  },

  goToBankDetail(e) {
    const bankId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/adminBankDetail/adminBankDetail?bankId=${bankId}`
    });
  },

  fetchUserBanks() {
    this.setData({ isLoading: true });
    util.request(`/api/v1/admin/question-banks?user_id=${this.data.userId}&page=1&page_size=30`, 'GET')
      .then(res => {
        const list = res.data?.list || res.list || [];
        this.setData({ banks: list, isLoading: false });
      })
      .catch(() => this.setData({ isLoading: false }));
  },

  fetchUserInfo() {
    util.request(`/api/v1/admin/users/${this.data.userId}`, 'GET').then(res => {
        const info = res.data || res;
        if (info.created_at) info.short_date = info.created_at.substring(0, 10);
        this.setData({ userInfo: info });
    }).catch(() => {});
  },

  fetchSessions() {
    this.setData({ isLoading: true });
    util.request(`/api/v1/admin/sessions/?user_id=${this.data.userId}&page=1&page_size=30`, 'GET').then(res => {
        this.setData({ sessions: res.data?.list || res.list || [], isLoading: false });
    }).catch(() => this.setData({ isLoading: false }));
  },

  fetchFavorites() {
    this.setData({ isLoading: true });
    util.request(`/api/v1/admin/favorites?user_id=${this.data.userId}&page=1&page_size=30`, 'GET').then(res => {
        this.setData({ favorites: res.data?.list || res.list || [], isLoading: false });
    }).catch(() => this.setData({ isLoading: false }));
  },

  toggleUserStatus() {
    if (!this.data.userInfo || this.data.userInfo.role === 'admin') return;
    const newStatus = !this.data.userInfo.is_active;
    wx.showModal({
      title: '操作确认',
      content: `确定要${newStatus ? '解封' : '封禁'}该用户吗？`,
      success: (res) => {
        if (res.confirm) {
          util.request(`/api/v1/admin/users/batch/status`, 'PUT', {
            user_ids: [this.data.userId],
            status_data: { is_active: newStatus }
          }).then(() => {
            wx.showToast({ title: '操作成功', icon: 'success' });
            this.setData({ 'userInfo.is_active': newStatus });
          });
        }
      }
    });
  },

  // ============== 精美详情渲染逻辑 ==============

  goToSessionDetail(e) {
    const sessionId = e.currentTarget.dataset.id;
    wx.showLoading({ title: '拉取聊天记录...' });
    
    util.request(`/api/v1/admin/messages?session_id=${sessionId}&page=1&page_size=50`, 'GET')
      .then(res => {
        wx.hideLoading();
        const list = res.data?.list || res.list || [];
        if (list.length === 0) {
          wx.showToast({ title: '该会话无具体消息记录', icon: 'none' });
          return;
        }
        
        const chatHtml = list.map(m => {
          const isUser = m.role === 'user';
          const roleName = isUser ? '用户 (User)' : 'AI 助手 (Assistant)';
          const bgColor = isUser ? '#e8f4ff' : '#f4f5f9';
          const borderColor = isUser ? '#d0e8ff' : '#ebecee';
          const align = isUser ? 'right' : 'left';
          
          return `
            <div style="margin-bottom: 30rpx; text-align: ${align};">
              <div style="font-size:24rpx; color:#999; margin-bottom:8rpx;">${roleName}</div>
              <div style="display:inline-block; text-align:left; max-width:90%; background:${bgColor}; padding:20rpx 24rpx; border-radius:16rpx; border:1px solid ${borderColor};">
                ${parseMarkdownToHtml(m.content)}
              </div>
            </div>
          `;
        }).join('');
        
        this.setData({
          showDetailModal: true,
          detailModalTitle: `历史对话 (ID: ${sessionId})`,
          detailModalHtml: chatHtml
        });
      }).catch(() => wx.hideLoading());
  },

  async goToFavoriteDetail(e) {
    const favId = e.currentTarget.dataset.id;
    wx.showLoading({ title: '获取收藏内容...' });
    
    try {
      const res = await util.request(`/api/v1/admin/favorites/${favId}`, 'GET');
      const data = res.data || res;
      
      const contentType = data.content_type;
      let contentIds = data.content_ids;
      // 如果后端把数组转成了字符串，比如 "[12]"，我们需要先把它 parse 成真正的 JS 数组
      if (typeof contentIds === 'string' && contentIds.trim().startsWith('[')) {
        try {
          contentIds = JSON.parse(contentIds);
        } catch (parseErr) {
          console.warn("解析 content_ids 失败:", parseErr);
        }
      }

      // 提取主键ID：优先从数组取第一个，如果没有再降级使用老字段 content_id
      const primaryId = (Array.isArray(contentIds) && contentIds.length > 0) 
                        ? contentIds[0] 
                        : data.content_id;

      // 👇 【终极修复】：如果是会话，直接委托给渲染聊天记录的函数
      if (contentType === 'session' && primaryId) {
        wx.hideLoading();
        this.goToSessionDetail({ currentTarget: { dataset: { id: primaryId } } });
        return; // 结束执行，不再走下面的默认逻辑
      }

      let favHtml = `
        <div style="background:#f8f9fc; padding:24rpx; border-radius:12rpx; margin-bottom:30rpx; border-left: 8rpx solid #5856d6;">
          <div style="font-size:26rpx; color:#666; margin-bottom:10rpx;">内容类型: <strong style="color:#333;">${contentType || '未知'}</strong></div>
          <div style="font-size:26rpx; color:#666; margin-bottom:10rpx;">关联主键ID: <strong style="color:#333;">${primaryId || '无'}</strong></div>
          <div style="font-size:24rpx; color:#999;">收藏时间: ${data.created_at || '-'}</div>
        </div>
      `;

      if (primaryId) {
        let detailData = null;
        try {
          // 这里移除了 session 的分支，因为上面已经拦截了
          if (contentType === 'bank') {
             const bRes = await util.request(`/api/v1/admin/question-banks/${primaryId}`, 'GET');
             detailData = bRes.data || bRes;
          } else {
             // 兼容 'question' 以及 '英语考点' 这种旧的测试数据
             const qRes = await util.request(`/api/v1/admin/questions/${primaryId}`, 'GET');
             detailData = qRes.data || qRes;
          }
        } catch (e) {
          console.warn("二次请求未找到具体详情", e);
        }

        if (detailData) {
          favHtml += `<div style="font-weight:bold; margin-bottom:16rpx; font-size:30rpx;">详细内容：</div>`;
          
          const textContent = detailData.title || detailData.bank_name || detailData.content || detailData.question_text || detailData.text;
          
          if (textContent) {
             let fullText = textContent;
             if (detailData.description) fullText += `\n\n描述：${detailData.description}`;
             favHtml += parseMarkdownToHtml(fullText);
          } else {
             favHtml += `<pre style="background:#f0f0f0; padding:20rpx; border-radius:8rpx; font-size:24rpx; overflow-x:auto; margin:0;">${JSON.stringify(detailData, null, 2)}</pre>`;
          }

        } else {
          favHtml += `<div style="font-weight:bold; margin-bottom:16rpx; font-size:30rpx; color:#ff3b30;">无法关联到详情数据，原资源可能已被删除</div>`;
        }
      }

      this.setData({
        showDetailModal: true,
        detailModalTitle: `收藏详情 (ID: ${favId})`,
        detailModalHtml: favHtml
      });
      wx.hideLoading();

    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '拉取失败', icon: 'none' });
    }
  },

  closeDetailModal() {
    this.setData({ showDetailModal: false, detailModalHtml: '' });
  },

  stopBubble() {}
});