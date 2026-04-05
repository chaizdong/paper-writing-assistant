"""
Agent 基类

定义所有 Agent 的通用接口和基础功能：
- 状态管理
- 消息处理
- 任务执行生命周期
- 日志记录
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional
from datetime import datetime

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


class AgentStatus(Enum):
    """Agent 状态"""
    IDLE = "idle"
    RUNNING = "running"
    WAITING_CONFIRMATION = "waiting_confirmation"
    COMPLETED = "completed"
    ERROR = "error"


class BaseAgent(ABC):
    """
    Agent 基类

    所有专业 Agent 必须继承此类并实现核心方法
    """

    def __init__(self, agent_id: str, name: str, description: str = ""):
        """
        初始化 Agent

        Args:
            agent_id: Agent 唯一标识
            name: Agent 名称
            description: Agent 描述
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.current_task: Optional[TaskRequest] = None
        self.created_at = datetime.now()
        self._state: dict = {}

        # 回调函数
        self._on_message_callback: Optional[callable] = None
        self._on_confirm_callback: Optional[callable] = None
        self._on_progress_callback: Optional[callable] = None

    @property
    def state(self) -> dict:
        """获取内部状态"""
        return self._state

    @state.setter
    def state(self, value: dict):
        """设置内部状态"""
        self._state = value

    def update_state(self, key: str, value: Any):
        """更新状态的某个字段"""
        self._state[key] = value

    def clear_state(self):
        """清空内部状态"""
        self._state = {}

    # ==================== 抽象方法 ====================

    @abstractmethod
    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行任务（核心方法）

        子类必须实现此方法来定义具体的任务逻辑

        Args:
            task_request: 任务请求

        Returns:
            TaskResponse: 任务执行结果
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        获取 Agent 能力列表

        Returns:
            能力描述列表
        """
        pass

    # ==================== 消息处理 ====================

    def handle_message(self, message: Message) -> Optional[Message]:
        """
        处理接收到的消息

        Args:
            message: 接收到的消息

        Returns:
            响应消息（如果需要）
        """
        logger.info(f"[{self.name}] 收到消息：{message.type.value}")

        if message.type == MessageType.TASK_REQUEST:
            return self._handle_task_request(message)
        elif message.type == MessageType.CONFIRMATION_RESPONSE:
            return self._handle_confirmation_response(message)
        elif message.type == MessageType.STATE_UPDATE:
            return self._handle_state_update(message)
        else:
            logger.warning(f"[{self.name}] 未处理的消息类型：{message.type}")
            return None

    def _handle_task_request(self, message: Message) -> TaskResponse:
        """处理任务请求"""
        task_request = TaskRequest(
            id=message.id,
            sender=message.receiver,
            receiver=self.agent_id,
            correlation_id=message.id,
            payload=message.payload,
        )

        self.status = AgentStatus.RUNNING
        self.current_task = task_request

        try:
            response = self.execute(task_request)
            self.status = AgentStatus.IDLE
            return response
        except Exception as e:
            logger.exception(f"[{self.name}] 任务执行失败：{e}")
            self.status = AgentStatus.ERROR
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                },
            )

    def _handle_confirmation_response(self, message: Message) -> Optional[Message]:
        """处理确认响应"""
        # 子类可以重写此方法来处理确认后的逻辑
        logger.info(f"[{self.name}] 收到确认响应")
        return None

    def _handle_state_update(self, message: Message) -> Optional[Message]:
        """处理状态更新"""
        state_update = StateUpdate(
            payload=message.payload,
        )
        self._state.update(state_update.data)
        return None

    # ==================== 确认请求 ====================

    def request_confirmation(
        self,
        confirmation_id: str,
        question: str,
        options: list = None,
        default: Any = None,
        timeout: int = 300,
        critical: bool = True,
        confirmation_type: str = "blocking",
    ) -> ConfirmationRequest:
        """
        发送确认请求给用户

        Args:
            confirmation_id: 确认点唯一标识
            question: 确认问题
            options: 可选选项列表
            default: 默认选项
            timeout: 超时秒数
            critical: 是否关键确认（阻塞流程）
            confirmation_type: 确认类型 (question/selection/blocking/editing/non_blocking)

        Returns:
            ConfirmationRequest: 确认请求消息
        """
        self.status = AgentStatus.WAITING_CONFIRMATION

        payload = {
            "confirmation_id": confirmation_id,
            "question": question,
            "options": options or [],
            "default": default,
            "timeout": timeout,
            "critical": critical,
            "confirmation_type": confirmation_type,
        }

        confirmation = ConfirmationRequest(
            sender=self.agent_id,
            receiver="user",
            payload=payload,
        )

        # 触发回调
        if self._on_confirm_callback:
            self._on_confirm_callback(confirmation)

        return confirmation

    # ==================== 进度更新 ====================

    def send_progress(
        self,
        current_step: int,
        total_steps: int,
        description: str,
    ) -> ProgressUpdate:
        """
        发送进度更新

        Args:
            current_step: 当前步骤
            total_steps: 总步骤数
            description: 进度描述

        Returns:
            ProgressUpdate: 进度更新消息
        """
        progress = ProgressUpdate(
            sender=self.agent_id,
            payload={
                "current_step": current_step,
                "total_steps": total_steps,
                "description": description,
            },
        )

        # 触发回调
        if self._on_progress_callback:
            self._on_progress_callback(progress)

        return progress

    # ==================== 状态管理 ====================

    def save_checkpoint(self, checkpoint_id: str, data: dict) -> StateUpdate:
        """
        保存检查点

        Args:
            checkpoint_id: 检查点 ID
            data: 要保存的数据

        Returns:
            StateUpdate: 状态更新消息
        """
        state_update = StateUpdate(
            sender=self.agent_id,
            payload={
                "checkpoint": checkpoint_id,
                "data": data,
            },
        )

        if self._on_message_callback:
            self._on_message_callback(state_update)

        return state_update

    def restore_checkpoint(self, data: dict):
        """
        恢复检查点状态

        Args:
            data: 要恢复的数据
        """
        self._state.update(data)
        logger.info(f"[{self.name}] 已恢复检查点状态")

    # ==================== 回调注册 ====================

    def on_message(self, callback: callable):
        """注册消息发送回调"""
        self._on_message_callback = callback

    def on_confirmation(self, callback: callable):
        """注册确认请求回调"""
        self._on_confirm_callback = callback

    def on_progress(self, callback: callable):
        """注册进度更新回调"""
        self._on_progress_callback = callback

    # ==================== 工具方法 ====================

    def __str__(self) -> str:
        return f"{self.name}({self.agent_id}) - {self.status.value}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id} name={self.name}>"
