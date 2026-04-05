"""
方法设计 Agent

基于 Gap 分析结果，提出创新技术方案
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class MethodAgent(BaseAgent):
    """
    方法设计 Agent

    职责:
    - 基于 Gap 提出创新方法
    - 设计技术路线
    - 描述方法细节
    - 生成贡献点列表
    """

    def __init__(self, agent_id: str = "method_agent"):
        super().__init__(
            agent_id=agent_id,
            name="MethodAgent",
            description="方法设计 Agent - 基于 Gap 提出创新技术方案"
        )

    def get_capabilities(self) -> list[str]:
        return [
            "propose_method - 提出方法",
            "design_pipeline - 设计流程",
            "generate_contributions - 生成贡献点",
            "describe_architecture - 描述架构",
        ]

    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行方法设计任务

        Args:
            task_request: 任务请求，包含 gap_analysis 数据

        Returns:
            TaskResponse: 包含方法设计方案
        """
        try:
            # 解析输入
            input_data = task_request.input_data or {}
            gap_analysis = input_data.get("gap_analysis", {})
            research_gaps = gap_analysis.get("research_gaps", [])
            recommendation = gap_analysis.get("recommendation", "")

            logger.info("开始方法设计")

            # 发送进度更新
            self.send_progress(1, 5, "正在分析研究 Gap...")

            # 分析 Gap，确定设计方向
            design_direction = self._analyze_gaps(research_gaps, recommendation)

            self.send_progress(2, 5, "正在设计方法框架...")

            # 设计方法
            method = self._propose_method(design_direction)

            self.send_progress(3, 5, "正在设计技术路线...")

            # 设计技术路线
            technical_route = self._design_pipeline(method)

            self.send_progress(4, 5, "正在生成贡献点...")

            # 生成贡献点
            contributions = self._generate_contributions(method)

            self.send_progress(5, 5, "正在生成方法描述...")

            # 生成详细方法描述
            method_description = self._generate_method_description(
                method, technical_route, contributions
            )

            # 生成框架图描述
            framework_diagram = self._describe_framework(method, technical_route)

            logger.info(f"方法设计完成：{method.get('name', 'N/A')}")

            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": True,
                    "result": {
                        "method": method,
                        "technical_route": technical_route,
                        "contributions": contributions,
                        "method_description": method_description,
                        "framework_diagram": framework_diagram,
                    }
                }
            )

        except Exception as e:
            logger.exception(f"方法设计失败：{e}")
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                }
            )

    def _analyze_gaps(
        self,
        research_gaps: list[dict],
        recommendation: str
    ) -> dict:
        """
        分析研究 Gap，确定设计方向
        """
        if not research_gaps:
            return {
                "focus": "通用改进",
                "key_challenge": "未明确",
                "design_principle": "基于现有方法进行优化",
            }

        # 从 top gap 中提取设计方向
        top_gap = research_gaps[0]
        gap_text = top_gap.get("gap", "")
        opportunity = top_gap.get("opportunity", "")

        # 提取关键词
        keywords = []
        if "效率" in gap_text or "计算" in gap_text:
            keywords.append("高效")
            design_principle = "设计轻量级、高效率的方法"
        elif "数据" in gap_text or "标注" in gap_text:
            keywords.append("少样本")
            design_principle = "减少对标注数据的依赖"
        elif "泛化" in gap_text:
            keywords.append("泛化")
            design_principle = "提升跨领域泛化能力"
        else:
            keywords.append("改进")
            design_principle = "针对现有方法的局限性进行改进"

        return {
            "focus": gap_text[:50] + "..." if len(gap_text) > 50 else gap_text,
            "key_challenge": opportunity,
            "design_principle": design_principle,
            "keywords": keywords,
        }

    def _propose_method(self, design_direction: dict) -> dict:
        """
        提出具体方法
        """
        # 生成方法名称
        method_name = self._generate_method_name(design_direction)

        # 核心思想
        core_idea = f"""
针对 {design_direction['focus']} 这一核心问题，
{method_name} 的核心思想是：{design_direction['key_challenge']}。

具体来说，我们通过以下设计原则实现这一目标：
- {design_direction['design_principle']}
"""

        # 方法组件
        components = [
            {
                "name": "核心模块 A",
                "description": "负责处理输入特征，提取关键信息",
                "innovation": "引入新机制提升效率",
            },
            {
                "name": "核心模块 B",
                "description": "在模块 A 的基础上进行进一步处理",
                "innovation": "设计新颖的交互方式",
            },
            {
                "name": "输出模块",
                "description": "生成最终结果",
                "innovation": "优化输出质量",
            },
        ]

        return {
            "name": method_name,
            "core_idea": core_idea,
            "components": components,
            "design_principle": design_direction["design_principle"],
            "keywords": design_direction.get("keywords", []),
        }

    def _generate_method_name(self, design_direction: dict) -> str:
        """
        生成方法名称

        通常是缩写形式，如 "Transformer"、"BERT" 等
        """
        # 基于研究方向生成名称前缀
        keywords = design_direction.get("keywords", ["Method"])

        # 生成一些候选名称
        prefixes = {
            "高效": ["Efficient", "Fast", "Light", "Swift"],
            "少样本": ["FewShot", "LowResource", "DataEfficient"],
            "泛化": ["General", "Robust", "Adaptive", "Universal"],
            "改进": ["Improved", "Enhanced", "Advanced"],
        }

        # 选择一个前缀
        for kw in keywords:
            if kw in prefixes:
                prefix = prefixes[kw][0]
                break
        else:
            prefix = "Novel"

        # 生成名称（使用领域相关后缀）
        suffixes = [
            "Net", "Former", "LM", "CL", "RL",
            "Hub", "Mind", "Flow", "Core", "Pro",
        ]

        import random
        suffix = random.choice(suffixes)

        return f"{prefix}{suffix}"

    def _design_pipeline(self, method: dict) -> list[dict]:
        """
        设计技术路线/流程
        """
        return [
            {
                "step": 1,
                "name": "输入处理",
                "description": "对输入数据进行预处理和特征提取",
                "output": "特征表示",
            },
            {
                "step": 2,
                "name": f"{method['components'][0]['name']}处理",
                "description": method['components'][0]['description'],
                "output": "中间表示 A",
            },
            {
                "step": 3,
                "name": f"{method['components'][1]['name']}处理",
                "description": method['components'][1]['description'],
                "output": "中间表示 B",
            },
            {
                "step": 4,
                "name": "输出生成",
                "description": method['components'][2]['description'],
                "output": "最终结果",
            },
        ]

    def _generate_contributions(self, method: dict) -> list[str]:
        """
        生成贡献点列表

        通常 3 个贡献点
        """
        method_name = method.get("name", "Our Method")

        return [
            f"我们提出了{method_name}，一种针对现有方法局限性的新方法",
            f"我们设计了{method['components'][0]['name']}和{method['components'][1]['name']}，分别解决了 XX 和 YY 问题",
            f"我们在多个基准数据集上进行了实验，结果表明{method_name}优于现有 SOTA 方法",
        ]

    def _generate_method_description(
        self,
        method: dict,
        technical_route: list[dict],
        contributions: list[str]
    ) -> str:
        """
        生成详细的方法描述（用于论文）
        """
        description = f"""# {method['name']} 方法详解

## 核心思想

{method['core_idea']}

## 设计原则

{method['design_principle']}

## 方法框架

{method['name']} 包含以下核心组件：

"""
        for i, comp in enumerate(method['components'], 1):
            description += f"**{i}. {comp['name']}**\n"
            description += f"   - 功能：{comp['description']}\n"
            description += f"   - 创新点：{comp['innovation']}\n\n"

        description += "## 技术路线\n\n"
        description += f"{method['name']} 的处理流程如下：\n\n"

        for step in technical_route:
            description += f"**Step {step['step']}: {step['name']}**\n"
            description += f"{step['description']}\n"
            description += f"输出：{step['output']}\n\n"

        description += "## 本章小结\n\n"
        description += "本章详细介绍了我们提出的方法，包括核心思想、设计原则和具体实现。\n"
        description += "下一章将通过实验验证方法的有效性。"

        return description

    def _describe_framework(
        self,
        method: dict,
        technical_route: list[dict]
    ) -> str:
        """
        生成框架图描述（用于后续绘图）

        可以用 TikZ 或绘图工具生成
        """
        return f"""
框架图描述：

┌─────────────────────────────────────────────────────────┐
│                    {method['name']:^40}                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   输入 ──→ [Step 1: {technical_route[0]['name']:^15}] ──→│
│              ↓                                          │
│   [Step 2: {technical_route[1]['name']:^15}] ──→│
│              ↓                                          │
│   [Step 3: {technical_route[2]['name']:^15}] ──→│
│              ↓                                          │
│   [Step 4: {technical_route[3]['name']:^15}] ──→ 输出   │
│                                                         │
└─────────────────────────────────────────────────────────┘

建议使用 TikZ 绘制更专业的架构图，或用 draw.io 等工具
"""
