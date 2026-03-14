FROM modelscope-registry.cn-beijing.cr.aliyuncs.com/modelscope-repo/python:3.11

WORKDIR /home/user/app

# 复制项目文件
COPY ./ /home/user/app

# 安装 Node.js 并构建前端
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/* && \
    cd /home/user/app/frontend && \
    npm install && \
    npm run build && \
    rm -rf node_modules

# 强制重新安装依赖 (v2)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "from openjiuwen.agent.react_agent.react_agent import ReActAgent; print('OpenJiuwen OK')"

# 暴露端口
EXPOSE 7860

# 启动应用
ENTRYPOINT ["python", "-u", "app.py"]
