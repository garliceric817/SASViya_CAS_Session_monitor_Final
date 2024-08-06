# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器中
COPY . .

# 暴露 Prometheus 默认端口（如果需要）
# EXPOSE 8000

# 运行你的 Python 程序
CMD ["python", "main.py"]