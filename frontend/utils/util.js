const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()
  return `${[year, month, day].map(formatNumber).join('/')} ${[hour, minute, second].map(formatNumber).join(':')}`
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : `0${n}`
}

// 基础 API 地址 (这里统一改为我们本地 Docker 后端的调试地址)
const BASE_URL = 'http://127.0.0.1:8080';

/**
 * 1. 标准 HTTP 请求 (适用于获取题库列表、提交测验结果等结构化 JSON 数据)
 * @param {string} url - 接口路径
 * @param {string} method - 请求方法 (GET, POST 等)
 * @param {object} data - 请求参数
 * @param {boolean} showLoading - 是否显示默认的 Loading 提示
 */
const request = (url, method = 'GET', data = {}, showLoading = true) => {
  if (showLoading) {
    wx.showLoading({ title: '加载中...', mask: true });
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + url,
      method: method,
      data: data,
      header: {
        'Content-Type': 'application/json',
        // 'Authorization': 'Bearer ' + wx.getStorageSync('token') // 预留 Token 位置
      },
      success: (res) => {
        if (showLoading) wx.hideLoading();
        // 假设您的后端标准返回格式为 { code: 200, data: {...}, message: "..." }
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data);
        } else {
          wx.showToast({
            title: res.data.message || '服务器繁忙',
            icon: 'none',
            duration: 2000
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        if (showLoading) wx.hideLoading();
        wx.showToast({
          title: '网络连接失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
}

/**
 * 2. 流式(SSE)网络请求 (专用于 AI 大模型打字机效果)
 * @param {string} url - 接口路径
 * @param {object} data - 请求参数
 * @param {function} onMessage - 接收到新文字时的回调函数
 * @param {function} onDone - 传输彻底结束时的回调函数
 * @param {function} onError - 发生错误时的回调函数
 */
const streamRequest = (url, data = {}, onMessage, onDone, onError) => {
  const requestTask = wx.request({
    url: BASE_URL + url,
    method: 'POST', // 大模型对话一般都是 POST
    data: data,
    enableChunked: true, // 开启分块传输
    header: {
      'Content-Type': 'application/json',
      // 'Authorization': 'Bearer ' + wx.getStorageSync('token')
    },
    success: (res) => {
      if (onDone) onDone(res);
    },
    fail: (err) => {
      if (onError) onError(err);
    }
  });

  // 监听数据流
  requestTask.onChunkReceived((response) => {
    const uint8Array = new Uint8Array(response.data);
    let textChunk = '';
    
    try {
      const decoder = new TextDecoder('utf-8');
      textChunk = decoder.decode(uint8Array);
    } catch (e) {
      textChunk = String.fromCharCode.apply(null, uint8Array);
      textChunk = decodeURIComponent(escape(textChunk));
    }

    // 清洗掉后端的 SSE 修饰符，提取干净的文本
    let cleanText = textChunk.replace(/data: /g, '').replace(/\n/g, '');

    // 只要有干净的文本，就抛给页面的回调函数去更新 UI
    if (cleanText && typeof onMessage === 'function') {
      onMessage(cleanText);
    }
  });

  // 返回 task 对象，方便页面在需要时（比如用户突然退出页面）调用 requestTask.abort() 强行中断水管
  return requestTask;
}

module.exports = {
  formatTime,
  request,
  streamRequest // 别忘了把新函数导出去
}