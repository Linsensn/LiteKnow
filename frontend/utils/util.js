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

// 基础 API 地址 (请替换为您实际的后端接口地址)
const BASE_URL = 'https://your-api-domain.com/api';

/**
 * 封装微信请求
 * @param {string} url - 接口路径
 * @param {string} method - 请求方法 (GET, POST 等)
 * @param {object} data - 请求参数
 * @param {boolean} showLoading - 是否显示默认的 Loading 提示
 */
const request = (url, method = 'GET', data = {}, showLoading = true) => {
  if (showLoading) {
    wx.showLoading({ title: 'AI思考中...', mask: true });
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + url,
      method: method,
      data: data,
      header: {
        'Content-Type': 'application/json',
        // 如果后续需要登录 Token，可在此处统一添加
        // 'Authorization': 'Bearer ' + wx.getStorageSync('token')
      },
      success: (res) => {
        if (showLoading) wx.hideLoading();
        // 假设您的后端返回格式为 { code: 200, data: {...}, message: "..." }
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

module.exports = {
  formatTime,
  request
}