"""
工作流引擎

定义和编排论文写作的工作流程
支持：
- 阶段定义与跳转
- 工作流执行
- 暂停/恢复
- 回滚到任意阶段
"""

import logging
from typing import Any, Callable, Optional

from core.state_manager import StateManager, WorkflowStage, CHECKPOINTS
from agents.base import (
    Orchestrator,
    TaskRequest,
    TaskResponse,
    ConfirmationRequest,
    ConfirmationResponse,
)

logger = logging.getLogger(__name__)


class WorkflowStageDefinition:
    """工作流阶段定义"""

    def __init__(
        self,
        stage_id: str,
        name: str,
        description: str = "",
        agents: list[str] = None,
        confirmations: list[str] = None,
        entry_action: Callable = None,
        exit_action: Callable = None,
    ):
        self.stage_id = stage_id
        self.name = name
        self.description = description
        self.agents = agents or []
        self.confirmations = confirmations or []
        self.entry_action = entry_action
        self.exit_action = exit_action


# 预定义的工作流阶段
LITERATURE_RESEARCH_STAGE = WorkflowStageDefinition(
    stage_id="research",
    name="文献调研",
    description="搜索、筛选和总结相关文献",
    agents=["literature_agent", "summary_agent"],
    confirmations=["cp1", "cp2"],
)

GAP_ANALYSIS_STAGE = WorkflowStageDefinition(
    stage_id="gap_analysis",
    name="Gap 分析",
    description="分析现有方法的局限性，识别研究机会",
    agents=["gap_analysis_agent"],
    confirmations=["cp3"],
)

METHOD_DESIGN_STAGE = WorkflowStageDefinition(
    stage_id="method_design",
    name="方法设计",
    description="基于 Gap 提出创新方法",
    agents=["method_agent", "novelty_agent"],
    confirmations=["cp4", "cp5"],
)

EXPERIMENT_STAGE = WorkflowStageDefinition(
    stage_id="experiment",
    name="实验规划",
    description="设计实验方案、选择数据集和评价指标",
    agents=["experiment_agent", "metrics_agent"],
    confirmations=["cp6", "cp7"],
)

WRITING_STAGE = WorkflowStageDefinition(
    stage_id="writing",
    name="论文撰写",
    description="撰写论文各章节",
    agents=["writing_agent", "structure_agent", "review_agent"],
    confirmations=["cp8", "cp9", "cp10"],
)


class WorkflowEngine:
    """
    工作流引擎

    负责执行和管理工作流
    """

    def __init__(self, state_manager: StateManager, orchestrator: Orchestrator):
        """
        初始化工作流引擎

        Args:
            state_manager: 状态管理器
            orchestrator: Agent 编排器
        """
        self.state_manager = state_manager
        self.orchestrator = orchestrator
        self.current_stage: Optional[WorkflowStageDefinition] = None
        self._paused = False
        self._current_step = 0
        self._total_steps = 0

        # 阶段映射
        self._stages: dict[str, WorkflowStageDefinition] = {
            WorkflowStage.RESEARCH: LITERATURE_RESEARCH_STAGE,
            WorkflowStage.GAP_ANALYSIS: GAP_ANALYSIS_STAGE,
            WorkflowStage.METHOD_DESIGN: METHOD_DESIGN_STAGE,
            WorkflowStage.EXPERIMENT: EXPERIMENT_STAGE,
            WorkflowStage.WRITING: WRITING_STAGE,
        }

    def get_stage(self, stage_id: str) -> Optional[WorkflowStageDefinition]:
        """获取阶段定义"""
        return self._stages.get(stage_id)

    def list_stages(self) -> list[dict]:
        """列出所有阶段"""
        return [
            {
                "stage_id": s.stage_id,
                "name": s.name,
                "description": s.description,
                "agents": s.agents,
                "confirmations": s.confirmations,
            }
            for s in self._stages.values()
        ]

    # ==================== 工作流执行 ====================

    def execute_stage(
        self,
        stage_id: str,
        input_data: dict = None,
    ) -> dict:
        """
        执行单个阶段

        Args:
            stage_id: 阶段 ID
            input_data: 输入数据

        Returns:
            阶段执行结果
        """
        stage = self.get_stage(stage_id)
        if not stage:
            logger.error(f"未知阶段：{stage_id}")
            return {"success": False, "error": f"未知阶段：{stage_id}"}

        logger.info(f"开始执行阶段：{stage.name}")
        self.current_stage = stage
        self._current_step = 0
        self._total_steps = len(stage.agents) + len(stage.confirmations)

        # 入口动作
        if stage.entry_action:
            stage.entry_action()

        results = []

        # 执行该阶段的 Agent 任务
        for agent_id in stage.agents:
            if self._paused:
                logger.info("工作流已暂停")
                break

            self._current_step += 1
            logger.info(f"执行 Agent: {agent_id}")

            # 检查 Agent 是否存在
            agent = self.orchestrator.registry.get(agent_id)
            if not agent:
                logger.warning(f"Agent 不存在：{agent_id}, 跳过")
                continue

            # 执行任务
            response = self.orchestrator.execute_task(
                agent_id=agent_id,
                task_type=stage_id,
                input_data=input_data,
            )
            results.append({"agent": agent_id, "response": response})

            if not response.success:
                logger.error(f"Agent 执行失败：{agent_id}")
                break

        # 处理确认点
        for cp_id in stage.confirmations:
            if self._paused:
                break

            self._current_step += 1
            logger.info(f"等待确认点：{cp_id}")

            # 保存检查点
            checkpoint_data = self._gather_stage_data(stage_id, results)
            self.state_manager.save_checkpoint(cp_id, checkpoint_data)

        # 出口动作
        if stage.exit_action:
            stage.exit_action()

        return {
            "success": True,
            "stage": stage_id,
            "results": results,
        }

    def _gather_stage_data(self, stage_id: str, results: list) -> dict:
        """收集阶段数据用于保存检查点"""
        data = {}
        for result in results:
            agent_id = result["agent"]
            response = result["response"]
            if response.success:
                data[agent_id] = response.payload.get("result", {})
        return data

    def execute_all(self, start_stage: str = None) -> dict:
        """
        执行所有阶段

        Args:
            start_stage: 起始阶段 ID

        Returns:
            执行结果
        """
        stages_order = [
            WorkflowStage.RESEARCH,
            WorkflowStage.GAP_ANALYSIS,
            WorkflowStage.METHOD_DESIGN,
            WorkflowStage.EXPERIMENT,
            WorkflowStage.WRITING,
        ]

        # 确定起始阶段
        start_index = 0
        if start_stage:
            try:
                start_index = stages_order.index(start_stage)
            except ValueError:
                logger.warning(f"未知起始阶段：{start_stage}, 从第一阶段开始")

        results = {}
        for stage_id in stages_order[start_index:]:
            if self._paused:
                break

            result = self.execute_stage(stage_id)
            results[stage_id] = result

            if not result.get("success"):
                logger.error(f"阶段执行失败：{stage_id}")
                break

        return {
            "success": not self._paused,
            "results": results,
        }

    # ==================== 阶段跳转 ====================

    def goto_stage(self, stage_id: str) -> bool:
        """
        跳转到指定阶段

        Args:
            stage_id: 目标阶段 ID

        Returns:
            是否成功
        """
        stage = self.get_stage(stage_id)
        if not stage:
            logger.error(f"未知阶段：{stage_id}")
            return False

        self.state_manager.set_stage(stage_id)
        logger.info(f"已跳转到阶段：{stage.name}")
        return True

    def next_stage(self) -> Optional[str]:
        """
        进入下一阶段

        Returns:
            下一阶段 ID，如果没有下一阶段则返回 None
        """
        stages_order = list(self._stages.keys())
        current = self.state_manager.get_current_stage()

        try:
            current_index = stages_order.index(current)
            if current_index < len(stages_order) - 1:
                next_stage_id = stages_order[current_index + 1]
                self.goto_stage(next_stage_id)
                return next_stage_id
        except ValueError:
            pass

        return None

    def previous_stage(self) -> Optional[str]:
        """
        返回上一阶段

        Returns:
            上一阶段 ID，如果没有上一阶段则返回 None
        """
        stages_order = list(self._stages.keys())
        current = self.state_manager.get_current_stage()

        try:
            current_index = stages_order.index(current)
            if current_index > 0:
                prev_stage_id = stages_order[current_index - 1]
                self.goto_stage(prev_stage_id)
                return prev_stage_id
        except ValueError:
            pass

        return None

    # ==================== 暂停/恢复 ====================

    def pause(self):
        """暂停工作流"""
        self._paused = True
        logger.info("工作流已暂停")

    def resume(self):
        """恢复工作流"""
        self._paused = False
        logger.info("工作流已恢复")

    def is_paused(self) -> bool:
        """检查是否暂停"""
        return self._paused

    # ==================== 回滚 ====================

    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        回滚到指定检查点

        Args:
            checkpoint_id: 检查点 ID

        Returns:
            是否成功
        """
        return self.state_manager.rollback_to_checkpoint(checkpoint_id)

    def rollback_to_stage(self, stage_id: str) -> bool:
        """
        回滚到指定阶段

        Args:
            stage_id: 阶段 ID

        Returns:
            是否成功
        """
        # 找到该阶段的第一个检查点
        stage = self.get_stage(stage_id)
        if not stage or not stage.confirmations:
            logger.error(f"阶段没有检查点：{stage_id}")
            return False

        first_cp = stage.confirmations[0]
        return self.rollback_to_checkpoint(first_cp)

    # ==================== 进度查询 ====================

    def get_progress(self) -> dict:
        """获取当前进度"""
        current_stage = self.state_manager.get_current_stage()
        stages_order = list(self._stages.keys())

        try:
            current_index = stages_order.index(current_stage)
            percent = ((current_index + 1) / len(stages_order)) * 100
        except ValueError:
            percent = 0.0

        return {
            "current_stage": current_stage,
            "percent": percent,
            "completed_stages": stages_order[:current_index + 1] if current_index >= 0 else [],
            "remaining_stages": stages_order[current_index + 1:] if current_index >= 0 else stages_order,
        }

    def get_status(self) -> dict:
        """获取引擎状态"""
        return {
            "current_stage": self.current_stage.name if self.current_stage else None,
            "paused": self._paused,
            "step": self._current_step,
            "total_steps": self._total_steps,
        }
