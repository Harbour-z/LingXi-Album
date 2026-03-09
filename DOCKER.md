# 智慧相册 Docker 使用指南

## 快速开始

### 1. 前置要求
- 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- 准备阿里云 API Keys（Embedding + Agent + Vision）

### 2. 配置 API Keys
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑 .env 文件，填入你的 API Keys
vim .env  # 或使用任何文本编辑器
```

需要配置的变量：
```bash
ALIYUN_EMBEDDING_API_KEY="sk-xxx"  # 用于图片向量化
OPENAI_API_KEY="sk-xxx"            # 用于智能对话
VISION_MODEL_API_KEY="sk-xxx"     # 用于视觉理解
```

### 3. 启动服务

**方法一：使用启动脚本（推荐）**
```bash
# macOS/Linux
chmod +x start-docker.sh
./start-docker.sh

# Windows
start-docker.bat
```

**方法二：手动启动**
```bash
# 构建前端
cd frontend && npm run build && cd ..

# 启动 Docker
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 访问应用
- 主页: http://localhost:7860
- API文档: http://localhost:7860/docs

---

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 完全清理（删除数据）
docker-compose down -v
```

---

## 数据持久化

以下目录会自动挂载到本地，数据不会丢失：
- `./storage` - 上传的图片
- `./qdrant_data` - 向量数据库

---

## 故障排查

### 服务启动失败
```bash
# 查看详细日志
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

### 端口冲突
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8080:7860"  # 改为 8080 或其他端口
```

### API Key 错误
检查 `.env` 文件中的 API Keys 是否正确填写。

---

## 与本地开发的区别

| 项目        | 本地开发         | Docker         |
| ----------- | ---------------- | -------------- |
| Python 环境 | 需要安装         | 自动包含       |
| 依赖安装    | 手动 pip install | 自动安装       |
| 前端构建    | 手动 npm build   | 需提前构建     |
| 端口        | 7860             | 7860（可修改） |
| 数据持久化  | 本地目录         | 挂载卷         |

---

## 生产部署建议

1. **使用预构建镜像**（避免每次构建）
```bash
docker build -t smart-album:v1.0 -f Dockerfile.user .
docker save smart-album:v1.0 | gzip > smart-album-v1.0.tar.gz
```

2. **资源限制**
```yaml
services:
  smart-album:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

3. **使用 Nginx 反向代理**（生产环境推荐）
