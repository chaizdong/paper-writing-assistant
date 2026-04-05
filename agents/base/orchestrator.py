"""
Agent 编排器

负责协调多个 Agent 之间的协作，支持：
- Agent 注册与发现
- 任务分发与路由
- 消息总线（发布/订阅模式）
- 工作流编排
"""

import logging
from typing import Any, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentStatus
from .message_types import (
    Message,
    TaskRequest,
    TaskResponse,
    ConfirmationRequest,
    ConfirmationResponse,
    StateUpdate,
    ErrorMessage,
    ProgressUpdate,
    MessageType,
)


logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Agent 注册中心

    管理所有已注册 Agent 的生命周期
    """

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """注册一个 Agent"""
        if agent.agent_id in self._agents:
            logger.warning(f"Agent {agent.agent_id} 已存在，将被覆盖")
        self._agents[agent.agent_id] = agent
        logger.info(f"已注册 Agent: {agent.agent_id} ({agent.name})")

    def unregister(self, agent_id: str):
        """注销一个 Agent"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            logger.info(f"已注销 Agent: {agent_id}")

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """根据 ID 获取 Agent"""
        return self._agents.get(agent_id)

    def get_by_name(self, name: str) -> Optional[BaseAgent]:
        """根据名称获取 Agent"""
        for agent in self._agents.values():
            if agent.name == name:
                return agent
        return None

    def list_agents(self) -> list[dict]:
        """列出所有已注册的 Agent"""
        return [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "status": agent.status.value,
                "capabilities": agent.get_capabilities(),
            }
            for agent in self._agents.values()
        ]

    def get_all(self) -> list[BaseAgent]:
        """获取所有 Agent"""
        return list(self._agents.values())


class MessageBus:
    """
    消息总线

    支持发布/订阅模式，用于 Agent 之间的通信
    """

    def __init__(self):
        self._subscribers: dict[MessageType, list[callable]] = {}
        self._message_history: list[Message] = []

    def subscribe(self, message_type: MessageType, callback: callable):
        """订阅某种类型的消息"""
        if message_type not in self._subscribers:
            self._subscribers[message_type] = []
        self._subscribers[message_type].append(callback)
        logger.info(f"已订阅消息类型：{message_type.value}")

    def unsubscribe(self, message_type: MessageType, callback: callable):
        """取消订阅"""
        if message_type in self._subscribers:
            self._subscribers[message_type].remove(callback)

    def publish(self, message: Message):
        """发布消息到所有订阅者"""
        # 记录历史
        self._message_history.append(message)

        # 通知订阅者
        subscribers = self._subscribers.get(message.type, [])
        for callback in subscribers:
            try:
                callback(message)
            except Exception as e:
                logger.exception(f"消息回调执行失败：{e}")

        # 广播到所有 Agent 的 handle_message
        logger.debug(f"消息已发布：{message.type.value} from {message.sender}")

    def get_history(self, limit: int = 100) -> list[Message]:
        """获取消息历史"""
        return self._message_history[-limit:]

    def clear_history(self):
        """清空消息历史"""
        self._message_history = []


class Orchestrator:
    """
    Agent 编排器

    核心职责：
    - 管理 Agent 注册中心
    - 管理消息总线
    - 协调任务执行流程
    - 处理用户确认
    """

    def __init__(self):
        self.registry = AgentRegistry()
        self.message_bus = MessageBus()
        self._confirmation_handlers: dict[str, callable] = {}
        self._running = False

        # 订阅消息类型
        self._setup_message_handlers()

    def _setup_message_handlers(self):
        """设置消息处理器"""
        self.message_bus.subscribe(MessageType.CONFIRMATION_RESPONSE, self._handle_confirmation_response)
        self.message_bus.subscribe(MessageType.STATE_UPDATE, self._handle_state_update)
        self.message_bus.subscribe(MessageType.PROGRESS_UPDATE, self._handle_progress_update)
        self.message_bus.subscribe(MessageType.ERROR, self._handle_error)

    def register_agent(self, agent: BaseAgent):
        """
        注册一个 Agent 并设置回调

        Args:
            agent: 要注册的 Agent
        """
        # 设置回调
        agent.on_message(self._on_agent_message)
        agent.on_confirmation(self._on_agent_confirmation)
        agent.on_progress(self._on_agent_progress)

        # 注册到注册中心
        self.registry.register(agent)

    def unregister_agent(self, agent_id: str):
        """注销一个 Agent"""
        self.registry.unregister(agent_id)

    def _on_agent_message(self, message: Message):
        """处理 Agent 发出的消息"""
        self.message_bus.publish(message)

    def _on_agent_confirmation(self, confirmation: ConfirmationRequest):
        """处理 Agent 发出的确认请求"""
        logger.info(f"收到确认请求：{confirmation.payload.get('confirmation_id')}")
        self.message_bus.publish(confirmation)

    def _on_agent_progress(self, progress: ProgressUpdate):
        """处理 Agent 发出的进度更新"""
        self.message_bus.publish(progress)

    def _handle_confirmation_response(self, message: Message):
        """处理确认响应"""
        # 子类可以重写此方法来处理用户确认后的逻辑
        pass

    def _handle_state_update(self, message: Message):
        """处理状态更新"""
        # 更新全局状态
        pass

    def _handle_progress_update(self, message: Message):
        """处理进度更新"""
        progress = ProgressUpdate(payload=message.payload)
        percent = progress.percent
        logger.info(f"进度：{percent:.1f}% - {progress.description}")

    def _handle_error(self, message: Message):
        """处理错误消息"""
        error = ErrorMessage(payload=message.payload)
        logger.error(f"错误 [{error.error_code}]: {error.error_message}")

    # ==================== 任务执行 ====================

    def execute_task(
        self,
        agent_id: str,
        task_type: str,
        input_data: Any,
        expected_output: str = "",
    ) -> TaskResponse:
        """
        执行单个任务

        Args:
            agent_id: 执行任务的 Agent ID
            task_type: 任务类型
            input_data: 输入数据
            expected_output: 期望输出格式

        Returns:
            TaskResponse: 任务执行结果
        """
        agent = self.registry.get(agent_id)
        if not agent:
            return TaskResponse(
                payload={
                    "success": False,
                    "error_message": f"Agent 不存在：{agent_id}",
                }
            )

        task_request = TaskRequest(
            sender="orchestrator",
            receiver=agent_id,
            payload={
                "task_type": task_type,
                "input_data": input_data,
                "expected_output": expected_output,
            },
        )

        logger.info(f"执行任务：{task_type} on {agent_id}")
        response = agent.handle_message(task_request)
        return response

    def execute_chain(
        self,
        chain: list[tuple[str, str, dict]],
    ) -> list[TaskResponse]:
        """
        执行任务链

        Args:
            chain: 任务链 [(agent_id, task_type, input_data), ...]

        Returns:
            每个任务的执行结果
        """
        results = []
        for agent_id, task_type, input_data in chain:
            response = self.execute_task(agent_id, task_type, input_data)
            results.append(response)

            # 如果失败且是阻塞式，停止执行
            if not response.success:
                logger.warning(f"任务链在 {agent_id} 处失败")
                break

        return results

    # ==================== 确认点管理 ====================

    def register_confirmation_handler(self, confirmation_id: str, handler: callable):
        """
        注册确认点处理器

        Args:
            confirmation_id: 确认点 ID
            handler: 处理函数 (confirmation_response) -> None
        """
        self._confirmation_handlers[confirmation_id] = handler
        logger.info(f"已注册确认点处理器：{confirmation_id}")

    def handle_user_confirmation(self, confirmation_response: ConfirmationResponse):
        """
        处理用户确认响应

        Args:
            confirmation_response: 用户确认响应
        """
        confirmation_id = confirmation_response.payload.get("confirmation_id", "")
        handler = self._confirmation_handlers.get(confirmation_id)

        if handler:
            handler(confirmation_response)
        else:
            logger.warning(f"未找到确认点处理器：{confirmation_id}")

        # 转发给消息总线
        self.message_bus.publish(confirmation_response)

    # ==================== 状态管理 ====================

    def get_status(self) -> dict:
        """获取编排器状态"""
        return {
            "running": self._running,
            "registered_agents": len(self._agents) if hasattr(self, "_agents") else len(self.registry._agents),
            "message_history_size": len(self.message_bus._message_history),
        }

    def start(self):
        """启动编排器"""
        self._running = True
        logger.info("编排器已启动")

    def stop(self):
        """停止编排器"""
        self._running = False
        logger.info("编排器已停止")

    # ==================== 上下文管理 ====================

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# 便捷的全局编排器实例
_global_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """获取全局编排器实例"""
    global _global_orchestrator
    if _global_orchestrator is None:
        _global_orchestrator = Orchestrator()
    return _global_orchestrator


def reset_orchestrator():
    """重置全局编排器"""
    global _global_orchestrator
    _global_orchestrator = Orchestrator()
