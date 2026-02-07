FROM modelscope-registry.cn-beijing.cr.aliyuncs.com/modelscope-repo/python:3.11

WORKDIR /home/user/app

# 复制项目文件
COPY ./ /home/user/app

# 强制重新安装依赖 (v2)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "from openjiuwen.agent.react_agent.react_agent import ReActAgent; print('OpenJiuwen OK')"

# 暴露端口
EXPOSE 7860

# 启动应用
ENTRYPOINT ["python", "-u", "app.py"]
