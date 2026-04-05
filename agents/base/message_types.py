"""
消息类型定义

定义 Agent 之间通信的消息类型，支持：
- 任务请求/响应
- 用户确认请求/响应
- 状态更新
- 错误通知
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class MessageType(Enum):
    """消息类型枚举"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    CONFIRMATION_REQUEST = "confirmation_request"
    CONFIRMATION_RESPONSE = "confirmation_response"
    STATE_UPDATE = "state_update"
    ERROR = "error"
    PROGRESS_UPDATE = "progress_update"


class ConfirmationType(Enum):
    """确认类型"""
    QUESTION = "question"          # 问答式
    SELECTION = "selection"        # 选择式
    BLOCKING = "blocking"          # 阻塞式
    EDITING = "editing"            # 编辑式
    NON_BLOCKING = "non_blocking"  # 非阻塞式


@dataclass
class Message:
    """消息基类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.TASK_REQUEST
    sender: str = ""
    receiver: str = ""
    correlation_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    payload: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典格式（用于序列化）"""
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """从字典创建消息"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=MessageType(data.get("type", "task_request")),
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            correlation_id=data.get("correlation_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
        )


@dataclass
class TaskRequest(Message):
    """任务请求消息"""
    def __post_init__(self):
        self.type = MessageType.TASK_REQUEST

    @property
    def task_type(self) -> str:
        """任务类型"""
        return self.payload.get("task_type", "")

    @property
    def input_data(self) -> Any:
        """输入数据"""
        return self.payload.get("input_data")

    @property
    def expected_output(self) -> str:
        """期望输出格式"""
        return self.payload.get("expected_output", "")

    @property
    def deadline(self) -> Optional[datetime]:
        """截止时间"""
        deadline_str = self.payload.get("deadline")
        if deadline_str:
            return datetime.fromisoformat(deadline_str)
        return None


@dataclass
class TaskResponse(Message):
    """任务响应消息"""
    def __post_init__(self):
        self.type = MessageType.TASK_RESPONSE

    @property
    def success(self) -> bool:
        """是否成功"""
        return self.payload.get("success", False)

    @property
    def result(self) -> Any:
        """任务结果"""
        return self.payload.get("result")

    @property
    def error_message(self) -> str:
        """错误信息"""
        return self.payload.get("error_message", "")


@dataclass
class ConfirmationRequest(Message):
    """确认请求消息"""
    def __post_init__(self):
        self.type = MessageType.CONFIRMATION_REQUEST

    @property
    def confirmation_id(self) -> str:
        """确认点 ID"""
        return self.payload.get("confirmation_id", "")

    @property
    def question(self) -> str:
        """确认问题"""
        return self.payload.get("question", "")

    @property
    def options(self) -> list:
        """可选选项"""
        return self.payload.get("options", [])

    @property
    def default(self) -> Any:
        """默认选项"""
        return self.payload.get("default")

    @property
    def timeout(self) -> int:
        """超时秒数"""
        return self.payload.get("timeout", 300)

    @property
    def critical(self) -> bool:
        """是否关键确认（阻塞流程）"""
        return self.payload.get("critical", False)

    @property
    def confirmation_type(self) -> ConfirmationType:
        """确认类型"""
        type_str = self.payload.get("confirmation_type", "blocking")
        return ConfirmationType(type_str)


@dataclass
class ConfirmationResponse(Message):
    """确认响应消息"""
    def __post_init__(self):
        self.type = MessageType.CONFIRMATION_RESPONSE

    @property
    def confirmed(self) -> bool:
        """是否确认"""
        return self.payload.get("confirmed", False)

    @property
    def selected_option(self) -> Any:
        """选择的选项"""
        return self.payload.get("selected_option")

    @property
    def user_input(self) -> str:
        """用户输入（问答式）"""
        return self.payload.get("user_input", "")

    @property
    def edits(self) -> dict:
        """用户编辑内容（编辑式）"""
        return self.payload.get("edits", {})


@dataclass
class StateUpdate(Message):
    """状态更新消息"""
    def __post_init__(self):
        self.type = MessageType.STATE_UPDATE

    @property
    def stage(self) -> str:
        """当前阶段"""
        return self.payload.get("stage", "")

    @property
    def checkpoint(self) -> str:
        """检查点 ID"""
        return self.payload.get("checkpoint", "")

    @property
    def data(self) -> dict:
        """状态数据"""
        return self.payload.get("data", {})


@dataclass
class ErrorMessage(Message):
    """错误消息"""
    def __post_init__(self):
        self.type = MessageType.ERROR

    @property
    def error_code(self) -> str:
        """错误代码"""
        return self.payload.get("error_code", "UNKNOWN")

    @property
    def error_message(self) -> str:
        """错误信息"""
        return self.payload.get("error_message", "")

    @property
    def recoverable(self) -> bool:
        """是否可恢复"""
        return self.payload.get("recoverable", True)


@dataclass
class ProgressUpdate(Message):
    """进度更新消息"""
    def __post_init__(self):
        self.type = MessageType.PROGRESS_UPDATE

    @property
    def current_step(self) -> int:
        """当前步骤"""
        return self.payload.get("current_step", 0)

    @property
    def total_steps(self) -> int:
        """总步骤数"""
        return self.payload.get("total_steps", 0)

    @property
    def description(self) -> str:
        """进度描述"""
        return self.payload.get("description", "")

    @property
    def percent(self) -> float:
        """进度百分比"""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
