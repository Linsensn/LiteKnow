Page({
  data: {
    fileList: [], // 存放用户选择的文件列表
    isRecognizing: false // 控制按钮状态
  },

  // 1. 点击选择文件/图片
  chooseFiles() {
    wx.chooseMessageFile({
      count: 9, // 一次最多可选9个
      type: 'all', // 允许选择图片、文件(PDF/Word等)
      success: (res) => {
        // 将新选的文件追加到现有的列表中
        this.setData({
          fileList: this.data.fileList.concat(res.tempFiles)
        });
      }
    })
  },

  // 2. 移除列表中不想要的文件
  removeFile(e) {
    const index = e.currentTarget.dataset.index;
    let currentList = this.data.fileList;
    currentList.splice(index, 1);
    this.setData({ fileList: currentList });
  },

  // 3. 点击“AI识别”按钮
  startRecognize() {
    if (this.data.fileList.length === 0) {
      wx.showToast({ title: '请先上传文件', icon: 'none' });
      return;
    }

    this.setData({ isRecognizing: true });
    wx.showLoading({ title: 'AI整合去重中...', mask: true });

    // ⚠️ 模拟向后端发送文件并等待 AI 处理的时间 (2.5秒)
    setTimeout(() => {
      // 模拟 AI 处理完毕，生成了一个新的题库对象
      const newBank = {
        id: Date.now(), // 用时间戳做唯一ID
        title: 'AI 自动提取题库', 
        questionCount: Math.floor(Math.random() * 30) + 10 // 随机生成10-40道题
      };

      // ✨ 魔法：利用微信本地缓存临时充当数据库
      // 先把以前的题库取出来，把新的插到最前面，再存回去
      let myBanks = wx.getStorageSync('localBankList') || [];
      myBanks.unshift(newBank);
      wx.setStorageSync('localBankList', myBanks);

      wx.hideLoading();
      this.setData({ isRecognizing: false, fileList: [] }); // 清空上传列表
      
      wx.showToast({ title: '题库生成成功！', icon: 'success' });

      // 延迟1秒后，自动跳转到底部的“题库”Tab页，去查看成果
      setTimeout(() => {
        wx.switchTab({ url: '/pages/bankList/bankList' });
      }, 1000);

    }, 2500);
  }
})