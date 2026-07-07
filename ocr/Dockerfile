# ocr/Dockerfile
FROM python:3.10-slim

# 1. 安装系统底层依赖 (OpenCV 图像处理需要这两个库)
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 2. 直接通过 pip 安装 RapidOCR 官方提供的 API 封装包
# 使用 headless 版本的 opencv 避免 GUI 依赖冲突
RUN pip install --no-cache-dir rapidocr_api opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 暴露官方默认的 9003 端口
EXPOSE 9003

# 4. 启动命令
CMD ["rapidocr_api", "-ip", "0.0.0.0", "-p", "9003"]