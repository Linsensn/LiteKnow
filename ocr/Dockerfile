FROM python:3.10-slim

# 安装系统底层依赖（OpenCV 图像处理所需）
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 安装 OCR 服务及完整依赖（补充缺失的 onnxruntime）
RUN pip install --no-cache-dir \
    rapidocr_api \
    opencv-python-headless \
    onnxruntime \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露服务端口
EXPOSE 9003

# 启动命令
CMD ["rapidocr_api", "-ip", "0.0.0.0", "-p", "9003"]