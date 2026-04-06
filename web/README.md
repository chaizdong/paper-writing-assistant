# 论文写作辅助系统 - Web 版本

基于 FastAPI + Vue 3 的 Web 界面，提供友好的图形化操作界面。

## 快速开始

### 方式 1：直接启动（推荐）

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

然后在浏览器打开：`http://localhost:8000`

### 方式 2：手动启动

**1. 启动后端**
```bash
cd web/backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**2. 打开前端**
直接在浏览器打开 `web/frontend/index.html`

## 功能特性

### ✅ 已实现
- [x] 项目创建与管理
- [x] 工作流阶段可视化
- [x] 实时进度显示
- [x] 文献调研界面
- [x] WebSocket 实时通信
- [x] 日志控制台

### 🔄 开发中
- [ ] Gap 分析界面
- [ ] 方法设计界面
- [ ] 实验规划界面
- [ ] 论文撰写界面
- [ ] 结果导出功能

## 技术栈

**后端:**
- FastAPI - 高性能 Web 框架
- Uvicorn - ASGI 服务器
- WebSocket - 实时通信

**前端:**
- Vue 3 - 渐进式 JavaScript 框架
- Element Plus - Vue 3 组件库
- 原生 WebSocket API

## API 文档

启动后访问：`http://localhost:8000/docs`

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 列出所有项目 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/workflow/stages` | 列出所有阶段 |
| GET | `/api/workflow/status` | 获取当前状态 |
| POST | `/api/workflow/run` | 运行当前阶段 |
| POST | `/api/workflow/next` | 进入下一阶段 |
| POST | `/api/workflow/rollback/{id}` | 回滚到确认点 |
| WebSocket | `/ws/{client_id}/{project_id}` | 实时通信 |

## 界面预览

```
┌─────────────────────────────────────────────────────────┐
│  📝 论文写作辅助系统                                      │
│  基于 Agent 的智能论文写作工具                            │
├──────────────┬──────────────────────────────────────────┤
│ 工作流阶段    │  当前阶段：文献调研                        │
│              │  ████████████░░░░░░░░  60%               │
│ ● 文献调研    │                                          │
│ ○ Gap 分析     │  研究主题：[____________]                │
│ ○ 方法设计    │  本地目录：[____________]                │
│ ○ 实验规划    │  ☑ 启用网站爬取                          │
│ ○ 论文撰写    │                                          │
│              │  [运行当前阶段] [下一阶段]                 │
│              ├──────────────────────────────────────────┤
│              │  日志控制台：                              │
│              │  [10:30:45] 开始执行阶段：文献调研         │
│              │  [10:30:46] 正在搜索论文...               │
│              │  [10:30:50] 找到 15 篇论文                 │
└──────────────┴──────────────────────────────────────────┘
```

## 目录结构

```
web/
├── backend/
│   ├── main.py          # FastAPI 应用入口
│   ├── requirements.txt # Python 依赖
│   └── api/             # API 路由（待拆分）
├── frontend/
│   ├── index.html       # 单页面应用
│   └── assets/          # 静态资源（待添加）
├── start.sh             # Linux/Mac启动脚本
└── start.bat            # Windows 启动脚本
```

## 开发指南

### 添加新 API 路由

在 `backend/main.py` 添加：

```python
@app.get("/api/my-endpoint")
async def my_endpoint():
    return {"data": "example"}
```

### 前端调用 API

```javascript
const res = await fetch('http://localhost:8000/api/my-endpoint');
const data = await res.json();
```

### WebSocket 消息格式

**发送:**
```json
{ "type": "start", "data": {...} }
```

**接收:**
```json
{
  "type": "progress",
  "stage": "research",
  "progress": 50,
  "message": "正在搜索论文..."
}
```

## 部署

### 生产环境部署

**1. 构建前端**
```bash
cd frontend
# 使用 Vite 构建（待配置）
npm run build
```

**2. 配置 Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**3. 启动后端**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 常见问题

### Q: 无法访问后端 API？
A: 检查后端是否启动，访问 `http://localhost:8000/api/health`

### Q: WebSocket 连接失败？
A: 检查防火墙设置，确保 8000 端口开放

### Q: 如何修改端口？
A: 修改启动命令的 `--port 8000` 参数，并同步修改前端的 `API_BASE` 和 `WS_BASE`

## 后续计划

1. **完整工作流界面** - 所有 6 个阶段的完整 UI
2. **用户认证** - 多用户支持
3. **项目云存储** - SQLite/PostgreSQL
4. **导出功能** - PDF/Word/LaTeX
5. **MCP 配置界面** - 可视化工具配置
6. **实时协作** - 多人同时编辑

## 许可证

MIT
