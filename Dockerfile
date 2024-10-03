# 使用官方的 Python base image
FROM python:3.9-slim

# 跳至workspace
WORKDIR /app

#  複製 requirements.txt 到容器中
COPY requirements.txt .

# 安装 Python dependency
RUN pip install --no-cache-dir -r requirements.txt

# 複製文件至容器
COPY . .

# 暴露 Prometheus 默认端口（如果需要）
# EXPOSE 8000

# 執行python code
CMD ["python", "main.py"]