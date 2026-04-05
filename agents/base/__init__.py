"""
agents/base 包

提供 Agent 基础抽象类和编排器
"""

from .base_agent import BaseAgent, AgentStatus
from .message_types import (
    Message,
    MessageType,
    TaskRequest,
    TaskResponse,
    ConfirmationRequest,
    ConfirmationResponse,
    StateUpdate,
    ErrorMessage,
    ProgressUpdate,
    ConfirmationType,
)
from .orchestrator import (
    AgentRegistry,
    MessageBus,
    Orchestrator,
    get_orchestrator,
    reset_orchestrator,
)

__all__ = [
    # Base Agent
    "BaseAgent",
    "AgentStatus",
    # Message Types
    "Message",
    "MessageType",
    "TaskRequest",
    "TaskResponse",
    "ConfirmationRequest",
    "ConfirmationResponse",
    "StateUpdate",
    "ErrorMessage",
    "ProgressUpdate",
    "ConfirmationType",
    # Orchestrator
    "AgentRegistry",
    "MessageBus",
    "Orchestrator",
    "get_orchestrator",
    "reset_orchestrator",
]
