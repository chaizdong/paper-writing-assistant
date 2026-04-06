"""
论文写作辅助系统 - Web API

基于 FastAPI 的 RESTful API 和 WebSocket 服务
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# 导入现有系统模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.state_manager import get_state_manager
from agents.base import get_orchestrator
from agents import (
    LiteratureAgent, GapAnalysisAgent, MethodAgent,
    ExperimentAgent, WritingAgent, ReviewAgent
)
from workflows.workflow_engine import WorkflowEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 数据模型 ====================

class ProjectCreate(BaseModel):
    """创建项目请求"""
    title: str = Field(..., description="研究主题")
    domain: str = Field(default="通用", description="研究领域")


class RunRequest(BaseModel):
    """运行请求"""
    query: Optional[str] = None
    keywords: Optional[list[str]] = None
    local_dirs: Optional[list[str]] = None
    use_crawler: bool = False


class ConfirmationResponse(BaseModel):
    """确认点响应"""
    confirmed: bool
    data: Optional[dict] = None


# ==================== WebSocket 连接管理 ====================

class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.project_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, project_id: str = None):
        """接受连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

        if project_id:
            if project_id not in self.project_connections:
                self.project_connections[project_id] = []
            self.project_connections[project_id].append(websocket)

        logger.info(f"WebSocket 连接：{client_id}")

    def disconnect(self, client_id: str, project_id: str = None):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if project_id and project_id in self.project_connections:
            connections = self.project_connections[project_id]
            if websocket := next((c for c in connections if True), None):
                connections.remove(websocket)

        logger.info(f"WebSocket 断开：{client_id}")

    async def broadcast_to_project(self, project_id: str, message: dict):
        """向项目所有连接广播消息"""
        if project_id in self.project_connections:
            disconnected = []
            for connection in self.project_connections[project_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # 清理断开的连接
            for conn in disconnected:
                self.project_connections[project_id].remove(conn)

    async def send_personal(self, client_id: str, message: dict):
        """发送个人消息"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except:
                pass


# 全局连接管理器
manager = ConnectionManager()


# ==================== 应用生命周期 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("初始化系统组件...")
    app.state.state_manager = get_state_manager()
    app.state.orchestrator = get_orchestrator()

    # 注册 Agents
    agents = [
        LiteratureAgent(agent_id="literature", max_papers=20),
        GapAnalysisAgent(agent_id="gap"),
        MethodAgent(agent_id="method"),
        ExperimentAgent(agent_id="experiment"),
        WritingAgent(agent_id="writing", output_format="markdown"),
        ReviewAgent(agent_id="review"),
    ]

    for agent in agents:
        app.state.orchestrator.register_agent(agent)

    app.state.workflow_engine = WorkflowEngine(
        app.state.state_manager,
        app.state.orchestrator
    )

    logger.info("系统初始化完成")

    yield

    # 关闭时清理
    logger.info("系统关闭")


# ==================== FastAPI 应用 ====================

app = FastAPI(
    title="论文写作辅助系统 API",
    description="基于 Agent 的论文写作辅助工具",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API 路由 ====================

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "论文写作辅助系统 API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# ----- 项目管理 -----

@app.get("/api/projects")
async def list_projects():
    """列出所有项目"""
    sm = app.state.state_manager
    # 读取所有项目
    projects = []

    # 简单实现：从状态管理器获取
    # 实际应该查询数据库
    return {"projects": projects}


@app.post("/api/projects")
async def create_project(req: ProjectCreate):
    """创建新项目"""
    sm = app.state.state_manager

    project = sm.create_project(title=req.title, domain=req.domain)

    return {
        "success": True,
        "project": {
            "id": project.project_id,
            "title": project.title,
            "domain": project.domain,
            "created_at": project.created_at,
        }
    }


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """获取项目详情"""
    sm = app.state.state_manager
    project = sm.load_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {
        "project": {
            "id": project.project_id,
            "title": project.title,
            "domain": project.domain,
            "current_stage": project.current_stage,
        }
    }


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    sm = app.state.state_manager
    # TODO: 实现删除逻辑
    return {"success": True}


# ----- 工作流控制 -----

@app.get("/api/workflow/stages")
async def list_stages():
    """列出所有工作流阶段"""
    engine = app.state.workflow_engine
    stages = engine.list_stages()
    return {"stages": stages}


@app.get("/api/workflow/status")
async def workflow_status(project_id: Optional[str] = None):
    """获取工作流状态"""
    engine = app.state.workflow_engine
    state_manager = app.state.state_manager

    current_stage = state_manager.get_current_stage()
    progress = engine.get_progress()

    return {
        "current_stage": current_stage,
        "progress": progress,
    }


@app.post("/api/workflow/run")
async def run_stage(req: RunRequest):
    """运行当前阶段"""
    # TODO: 实现异步执行
    engine = app.state.workflow_engine

    # 简单实现：直接执行
    # 完整实现应该使用后台任务
    current_stage = engine.state_manager.get_current_stage()

    return {
        "success": True,
        "stage": current_stage,
        "message": "阶段执行中...",
    }


@app.post("/api/workflow/next")
async def next_stage():
    """进入下一阶段"""
    engine = app.state.workflow_engine
    next_stage = engine.next_stage()

    return {
        "success": True,
        "next_stage": next_stage,
    }


@app.post("/api/workflow/rollback/{checkpoint_id}")
async def rollback(checkpoint_id: str):
    """回滚到确认点"""
    engine = app.state.workflow_engine
    success = engine.rollback_to_checkpoint(checkpoint_id)

    return {"success": success}


# ----- WebSocket -----

@app.websocket("/ws/{client_id}/{project_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, project_id: str):
    """WebSocket 连接"""
    await manager.connect(websocket, client_id, project_id)

    try:
        while True:
            # 接收客户端消息（可忽略）
            try:
                data = await websocket.receive_text()
                logger.debug(f"收到消息：{client_id}: {data}")
            except:
                pass

    except WebSocketDisconnect:
        manager.disconnect(client_id, project_id)


# ----- 实时通知 -----

async def send_progress_update(project_id: str, stage: str, progress: int, message: str):
    """发送进度更新"""
    await manager.broadcast_to_project(project_id, {
        "type": "progress",
        "stage": stage,
        "progress": progress,
        "message": message,
    })


async def send_stage_complete(project_id: str, stage: str, result: dict):
    """发送阶段完成通知"""
    await manager.broadcast_to_project(project_id, {
        "type": "stage_complete",
        "stage": stage,
        "result": result,
    })


# ==================== 静态文件（生产环境） ====================

# 前端构建输出目录
# FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
# if FRONTEND_DIST.exists():
#     app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")
