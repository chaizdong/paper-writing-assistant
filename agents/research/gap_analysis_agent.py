"""
Gap 分析 Agent

分析现有方法的局限性，识别研究机会
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class GapAnalysisAgent(BaseAgent):
    """
    Gap 分析 Agent

    职责:
    - 分析现有方法的共性和差异
    - 识别 limitations 和未解决问题
    - 总结研究机会
    """

    def __init__(self, agent_id: str = "gap_analysis_agent"):
        super().__init__(
            agent_id=agent_id,
            name="GapAnalysisAgent",
            description="Gap 分析 Agent - 分析现有方法局限性，识别研究机会"
        )

    def get_capabilities(self) -> list[str]:
        return [
            "analyze_methods - 分析方法对比",
            "extract_limitations - 提取局限性",
            "identify_gaps - 识别研究空白",
            "generate_recommendations - 生成建议",
        ]

    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行 Gap 分析任务

        Args:
            task_request: 任务请求，包含 literature_review 数据

        Returns:
            TaskResponse: 包含 Gap 分析报告
        """
        try:
            # 解析输入
            input_data = task_request.input_data or {}
            papers = input_data.get("papers", [])
            literature_summary = input_data.get("summary", "")

            logger.info(f"开始 Gap 分析：分析 {len(papers)} 篇论文")

            if not papers:
                return TaskResponse(
                    sender=self.agent_id,
                    receiver=task_request.sender,
                    correlation_id=task_request.id,
                    payload={
                        "success": False,
                        "error_message": "没有提供论文数据，无法进行 Gap 分析"
                    }
                )

            # 发送进度更新
            self.send_progress(1, 5, "正在解析论文数据...")

            # 分析方法
            existing_methods = self._analyze_methods(papers)

            self.send_progress(2, 5, "正在提取局限性...")

            # 提取局限性
            limitations = self._extract_limitations(papers, existing_methods)

            self.send_progress(3, 5, "正在识别研究空白...")

            # 识别研究空白
            research_gaps = self._identify_gaps(limitations, papers)

            self.send_progress(4, 5, "正在生成建议...")

            # 生成推荐方向
            recommendation = self._generate_recommendation(research_gaps, existing_methods)

            self.send_progress(5, 5, "Gap 分析完成")

            # 生成报告
            report = self._generate_report(
                existing_methods=existing_methods,
                limitations=limitations,
                research_gaps=research_gaps,
                recommendation=recommendation
            )

            logger.info(f"Gap 分析完成：识别 {len(research_gaps)} 个研究空白")

            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": True,
                    "result": {
                        "existing_methods": existing_methods,
                        "limitations": limitations,
                        "research_gaps": research_gaps,
                        "recommendation": recommendation,
                        "report": report,
                    }
                }
            )

        except Exception as e:
            logger.exception(f"Gap 分析失败：{e}")
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                }
            )

    def _analyze_methods(self, papers: list[dict]) -> list[dict]:
        """
        分析现有方法

        将论文按方法分类，总结每类方法的特点
        """
        method_groups = {}

        for paper in papers:
            methods = paper.get("methods", [])
            extracted_methods = paper.get("extracted_methods", [])
            all_methods = methods + extracted_methods

            for method in all_methods:
                method_name = method.strip().lower()
                if not method_name:
                    continue

                if method_name not in method_groups:
                    method_groups[method_name] = {
                        "name": method,
                        "description": "",
                        "papers": [],
                        "characteristics": [],
                        "limitations": [],
                    }

                method_groups[method_name]["papers"].append(paper.get("title", ""))

        # 为每个方法生成描述
        result = []
        for method_name, data in method_groups.items():
            data["description"] = f"基于 {data['name']} 的方法"
            data["characteristics"] = [
                f"被 {len(data['papers'])} 篇论文使用",
                "在多个基准数据集上验证",
            ]
            result.append(data)

        # 按论文数量排序
        result.sort(key=lambda x: len(x["papers"]), reverse=True)

        return result[:10]  # 返回 top 10 方法

    def _extract_limitations(
        self,
        papers: list[dict],
        existing_methods: list[dict]
    ) -> list[str]:
        """
        从论文中提取局限性

        分析摘要和结论中的限制性陈述
        """
        limitations = set()

        # 常见的局限性模式
        limitation_patterns = [
            "however", "but", "although", "despite",
            "limitation", "challenge", "difficult", "expensive",
            "requires", "depend", "sensitive",
            "only", "limited", "restricted",
        ]

        for paper in papers:
            abstract = paper.get("abstract", "").lower()

            # 简单检测包含限制性的句子
            sentences = abstract.split(".")
            for sentence in sentences:
                if any(pattern in sentence for pattern in limitation_patterns):
                    # 提取为局限性（简化处理）
                    limitations.add(sentence.strip())

        # 如果没有从文本中提取到，生成通用局限性
        if not limitations:
            limitations = {
                "现有方法在复杂场景下性能下降",
                "大多数方法需要大量标注数据",
                "计算复杂度较高，难以部署到资源受限环境",
                "对小样本/零样本场景支持不足",
                "模型的泛化能力有待提高",
                "缺乏对可解释性的关注",
            }

        return list(limitations)[:10]

    def _identify_gaps(
        self,
        limitations: list[str],
        papers: list[dict]
    ) -> list[dict]:
        """
        识别研究空白

        基于局限性推导未解决的问题
        """
        gaps = []

        # 将局限性映射到研究空白
        gap_mapping = {
            "性能下降": {
                "gap": "现有方法在 XX 场景下性能不足",
                "opportunity": "设计更鲁棒的方法处理 XX 场景",
            },
            "标注数据": {
                "gap": "现有方法依赖大量标注数据",
                "opportunity": "探索少样本/无监督学习方法",
            },
            "计算复杂度": {
                "gap": "现有方法计算开销大，难以实时应用",
                "opportunity": "设计轻量级/高效的方法",
            },
            "泛化能力": {
                "gap": "现有方法泛化能力有限",
                "opportunity": "提升模型跨领域/跨任务泛化能力",
            },
            "可解释性": {
                "gap": "现有方法缺乏可解释性",
                "opportunity": "设计可解释/透明的模型",
            },
        }

        for limitation in limitations:
            for key, gap_info in gap_mapping.items():
                if key in limitation:
                    gaps.append(gap_info)
                    break
            else:
                # 未匹配到预定义模式，生成通用 gap
                gaps.append({
                    "gap": f"针对问题：{limitation[:50]}...",
                    "opportunity": "探索新的方法解决上述问题",
                })

        # 去重
        seen = set()
        unique_gaps = []
        for gap in gaps:
            gap_key = gap["gap"][:30]
            if gap_key not in seen:
                seen.add(gap_key)
                unique_gaps.append(gap)

        return unique_gaps[:5]

    def _generate_recommendation(
        self,
        research_gaps: list[dict],
        existing_methods: list[dict]
    ) -> str:
        """
        生成推荐研究方向
        """
        if not research_gaps:
            return "建议进一步调研文献，明确研究方向"

        # 选择最有前景的 gap
        top_gap = research_gaps[0]

        recommendation = f"""基于以上分析，建议重点关注以下研究方向：

**推荐方向**: {top_gap['opportunity']}

**理由**:
1. 该方向针对现有方法的明确局限性
2. 具有实际应用价值
3. 适合在短期内产出成果

**建议方法**:
- 在现有方法基础上进行改进
- 结合其他领域的成熟技术
- 针对特定应用场景优化

**验证思路**:
- 选择标准基准数据集进行验证
- 与 SOTA 方法进行公平对比
- 进行充分的消融实验验证各模块有效性
"""
        return recommendation

    def _generate_report(
        self,
        existing_methods: list[dict],
        limitations: list[str],
        research_gaps: list[dict],
        recommendation: str
    ) -> str:
        """
        生成 Gap 分析报告
        """
        report = "# Gap 分析报告\n\n"

        report += "## 一、现有方法总结\n\n"
        for i, method in enumerate(existing_methods[:5], 1):
            report += f"**{i}. {method['name']}**\n"
            report += f"- 描述：{method['description']}\n"
            report += f"- 相关论文：{len(method['papers'])} 篇\n\n"

        report += "## 二、现有方法局限性\n\n"
        for i, lim in enumerate(limitations, 1):
            report += f"{i}. {lim}\n"

        report += "\n## 三、研究空白\n\n"
        for i, gap in enumerate(research_gaps, 1):
            report += f"**{i}. {gap['gap']}**\n"
            report += f"   → 机会：{gap['opportunity']}\n\n"

        report += "## 四、推荐方向\n\n"
        report += recommendation

        return report
