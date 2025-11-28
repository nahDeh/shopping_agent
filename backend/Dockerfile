# 使用官方 Python 基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制依赖文件到容器
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码到容器
COPY . .

# 创建一个非 root 用户 (Hugging Face 的安全要求)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 暴露端口 (Hugging Face 默认强制使用 7860 端口)
EXPOSE 7860

# 启动命令 (注意 host 是 0.0.0.0，port 是 7860)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]