# 使用轻量级 Python 基础镜像
FROM python:3.10-slim

# 设置容器内的工作目录
WORKDIR /app

RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下所有代码到容器内的工作目录
COPY . .

# 暴露 8000 端口
EXPOSE 8000

# 启动命令 (开启热重载 --reload，以便本地修改代码后容器自动重启)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]