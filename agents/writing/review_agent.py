"""
审阅润色 Agent

检查语法、逻辑、引用完整性，生成修改建议
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


class ReviewAgent(BaseAgent):
    """
    审阅润色 Agent

    职责:
    - 检查语法和拼写
    - 检查逻辑连贯性
    - 检查引用完整性
    - 检查格式规范
    - 生成修改建议
    """

    def __init__(self, agent_id: str = "review_agent"):
        super().__init__(
            agent_id=agent_id,
            name="ReviewAgent",
            description="审阅润色 Agent - 检查语法、逻辑、引用完整性"
        )

    def get_capabilities(self) -> list[str]:
        return [
            "check_grammar - 语法检查",
            "check_logic - 逻辑检查",
            "check_citations - 引用检查",
            "check_format - 格式检查",
            "suggest_improvements - 修改建议",
        ]

    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行审阅任务

        Args:
            task_request: 任务请求，包含论文草稿

        Returns:
            TaskResponse: 包含审阅报告
        """
        try:
            # 解析输入
            input_data = task_request.input_data or {}
            paper = input_data.get("paper", {})
            sections = paper.get("sections", {})
            references = paper.get("references", [])
            target_venue = input_data.get("target_venue", "general")

            logger.info("开始论文审阅")

            # 发送进度更新
            self.send_progress(1, 5, "正在检查语法...")

            # 语法检查
            grammar_issues = self._check_grammar(sections)

            self.send_progress(2, 5, "正在检查逻辑...")

            # 逻辑检查
            logic_issues = self._check_logic(sections)

            self.send_progress(3, 5, "正在检查引用...")

            # 引用检查
            citation_issues = self._check_citations(sections, references)

            self.send_progress(4, 5, "正在检查格式...")

            # 格式检查
            format_issues = self._check_format(sections, target_venue)

            self.send_progress(5, 5, "正在生成建议...")

            # 生成修改建议
            suggestions = self._generate_suggestions(
                grammar_issues, logic_issues, citation_issues, format_issues
            )

            # 计算总体评分
            overall_score = self._calculate_score(
                grammar_issues, logic_issues, citation_issues, format_issues
            )

            # 生成审阅报告
            review_report = self._generate_review_report(
                grammar_issues=grammar_issues,
                logic_issues=logic_issues,
                citation_issues=citation_issues,
                format_issues=format_issues,
                suggestions=suggestions,
                overall_score=overall_score,
            )

            logger.info(f"审阅完成：总体评分={overall_score}")

            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": True,
                    "result": {
                        "grammar_issues": grammar_issues,
                        "logic_issues": logic_issues,
                        "citation_issues": citation_issues,
                        "format_issues": format_issues,
                        "suggestions": suggestions,
                        "overall_score": overall_score,
                        "review_report": review_report,
                        "ready_for_submission": overall_score >= 80,
                    }
                }
            )

        except Exception as e:
            logger.exception(f"审阅失败：{e}")
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                }
            )

    def _check_grammar(self, sections: dict) -> list[dict]:
        """
        语法检查

        检查拼写、语法、标点等
        """
        issues = []

        # 简单检查：过长句子
        for section_name, section_data in sections.items():
            content = section_data.get("content", "")
            lines = content.split("\n")

            for i, line in enumerate(lines):
                # 检查过长句子
                if len(line) > 200:
                    issues.append({
                        "type": "grammar",
                        "severity": "low",
                        "location": f"{section_name}, line {i+1}",
                        "description": "句子过长，建议拆分",
                        "suggestion": "将长句拆分为 2-3 个短句",
                    })

                # 检查空引用标记
                if "[]" in line or "[](" in line:
                    issues.append({
                        "type": "grammar",
                        "severity": "medium",
                        "location": f"{section_name}, line {i+1}",
                        "description": "发现空引用标记",
                        "suggestion": "添加引用内容或删除标记",
                    })

        # 添加一些示例问题（实际应该用 NLP 工具检查）
        issues.extend([
            {
                "type": "grammar",
                "severity": "low",
                "location": "Abstract",
                "description": "建议检查被动语态使用是否恰当",
                "suggestion": "适当改为主动语态可增强可读性",
            },
        ])

        return issues

    def _check_logic(self, sections: dict) -> list[dict]:
        """
        逻辑检查

        检查段落间过渡、论证连贯性等
        """
        issues = []

        # 检查是否有引言但没有相关工作
        has_introduction = "introduction" in sections
        has_related_work = "related_work" in sections
        has_method = "method" in sections
        has_experiments = "experiments" in sections

        if has_introduction and not has_related_work:
            issues.append({
                "type": "logic",
                "severity": "high",
                "location": "Structure",
                "description": "缺少相关工作章节",
                "suggestion": "添加 Related Work 章节讨论现有方法",
            })

        if has_method and not has_experiments:
            issues.append({
                "type": "logic",
                "severity": "high",
                "location": "Structure",
                "description": "缺少实验章节",
                "suggestion": "添加 Experiments 章节验证方法有效性",
            })

        # 检查章节长度比例
        for section_name, section_data in sections.items():
            content = section_data.get("content", "")
            word_count = len(content.split())

            if section_name == "introduction" and word_count < 500:
                issues.append({
                    "type": "logic",
                    "severity": "medium",
                    "location": "Introduction",
                    "description": "引言过短",
                    "suggestion": "建议扩展到 800-1000 字，充分阐述研究动机",
                })

            if section_name == "method" and word_count < 1000:
                issues.append({
                    "type": "logic",
                    "severity": "medium",
                    "location": "Method",
                    "description": "方法描述过短",
                    "suggestion": "建议扩展到 1500-2000 字，详细描述方法细节",
                })

        return issues

    def _check_citations(
        self,
        sections: dict,
        references: list[dict]
    ) -> list[dict]:
        """
        引用检查

        检查文中引用与参考文献列表的一致性
        """
        issues = []

        # 收集文中所有引用
        cited_ids = set()
        for section_data in sections.values():
            content = section_data.get("content", "")
            # 简单提取引用标记（LaTeX 风格）
            import re
            latex_cites = re.findall(r'\\cite\{(.*?)\}', content)
            for cite in latex_cites:
                cited_ids.update(c.split(','))

            # Markdown 风格
            md_cites = re.findall(r'\[(\d+)\]', content)
            for cite in md_cites:
                cited_ids.add(f"ref{cite}")

        # 检查未使用的参考文献
        ref_ids = {ref["id"] for ref in references}
        unused_refs = ref_ids - cited_ids
        if unused_refs:
            issues.append({
                "type": "citation",
                "severity": "low",
                "location": "References",
                "description": f"以下参考文献未在文中引用：{', '.join(unused_refs)}",
                "suggestion": "删除未引用的文献或在文中适当位置引用",
            })

        # 检查缺失的参考文献
        missing_refs = cited_ids - ref_ids
        if missing_refs:
            issues.append({
                "type": "citation",
                "severity": "high",
                "location": "References",
                "description": f"以下引用缺少对应参考文献：{', '.join(missing_refs)}",
                "suggestion": "在参考文献列表中添加对应条目",
            })

        # 检查参考文献数量
        if len(references) < 15:
            issues.append({
                "type": "citation",
                "severity": "medium",
                "location": "References",
                "description": f"参考文献数量偏少（{len(references)}篇）",
                "suggestion": "建议增加到 20-40 篇，充分覆盖相关工作",
            })

        return issues

    def _check_format(self, sections: dict, target_venue: str) -> list[dict]:
        """
        格式检查

        检查是否符合目标 venues 格式要求
        """
        issues = []

        # 通用格式检查
        for section_name, section_data in sections.items():
            content = section_data.get("content", "")

            # 检查公式标记
            if "$" in content and "$$" not in content:
                issues.append({
                    "type": "format",
                    "severity": "low",
                    "location": section_name,
                    "description": "可能存在行内公式格式问题",
                    "suggestion": "检查 LaTeX 公式标记是否正确",
                })

        # 根据目标 venue 检查
        venue_requirements = {
            "cvpr": {
                "max_pages": 8,
                "required_sections": ["abstract", "introduction", "method", "experiments", "conclusion"],
            },
            "icml": {
                "max_pages": 9,
                "required_sections": ["abstract", "introduction", "method", "experiments"],
            },
            "general": {
                "required_sections": ["abstract", "introduction", "conclusion"],
            },
        }

        reqs = venue_requirements.get(target_venue, venue_requirements["general"])

        # 检查必需章节
        section_names = set(sections.keys())
        for req_section in reqs.get("required_sections", []):
            if req_section not in section_names:
                issues.append({
                    "type": "format",
                    "severity": "high",
                    "location": "Structure",
                    "description": f"缺少必需章节：{req_section}",
                    "suggestion": f"添加 {req_section} 章节",
                })

        return issues

    def _generate_suggestions(
        self,
        grammar_issues: list[dict],
        logic_issues: list[dict],
        citation_issues: list[dict],
        format_issues: list[dict],
    ) -> list[str]:
        """
        生成修改建议
        """
        suggestions = []

        # 按严重程度排序
        all_issues = grammar_issues + logic_issues + citation_issues + format_issues
        high_severity = [i for i in all_issues if i.get("severity") == "high"]
        medium_severity = [i for i in all_issues if i.get("severity") == "medium"]

        # 高优先级建议
        for issue in high_severity[:5]:
            suggestions.append(f"[高优先级] {issue['location']}: {issue['description']} - {issue['suggestion']}")

        # 中优先级建议
        for issue in medium_severity[:5]:
            suggestions.append(f"[中优先级] {issue['location']}: {issue['description']} - {issue['suggestion']}")

        # 通用建议
        suggestions.extend([
            "[通用] 建议通读全文，检查语句流畅性",
            "[通用] 检查图表是否清晰、标注是否完整",
            "[通用] 确认所有公式符号都有定义",
            "[通用] 检查致谢和利益冲突声明",
        ])

        return suggestions

    def _calculate_score(
        self,
        grammar_issues: list[dict],
        logic_issues: list[dict],
        citation_issues: list[dict],
        format_issues: list[dict],
    ) -> int:
        """
        计算总体评分（0-100）
        """
        # 基础分
        score = 100

        # 扣分权重
        severity_weights = {
            "high": 10,
            "medium": 5,
            "low": 2,
        }

        all_issues = grammar_issues + logic_issues + citation_issues + format_issues
        for issue in all_issues:
            score -= severity_weights.get(issue.get("severity", "low"), 2)

        return max(0, min(100, score))

    def _generate_review_report(
        self,
        grammar_issues: list[dict],
        logic_issues: list[dict],
        citation_issues: list[dict],
        format_issues: list[dict],
        suggestions: list[str],
        overall_score: int,
    ) -> str:
        """
        生成审阅报告
        """
        report = f"""# 论文审阅报告

## 总体评分：{overall_score}/100

{'✓ 论文质量良好，可以提交' if overall_score >= 80 else '⚠ 建议修改后再提交' if overall_score >= 60 else '✗ 需要大幅修改'}

## 问题统计

| 类型 | 数量 |
|------|------|
| 语法 | {len(grammar_issues)} |
| 逻辑 | {len(logic_issues)} |
| 引用 | {len(citation_issues)} |
| 格式 | {len(format_issues)} |
| 总计 | {len(grammar_issues) + len(logic_issues) + len(citation_issues) + len(format_issues)} |

## 高优先级问题

"""
        all_issues = grammar_issues + logic_issues + citation_issues + format_issues
        high_priority = [i for i in all_issues if i.get("severity") == "high"]

        if high_priority:
            for i, issue in enumerate(high_priority, 1):
                report += f"{i}. **{issue['location']}**: {issue['description']}\n"
                report += f"   → {issue['suggestion']}\n\n"
        else:
            report += "无高优先级问题 ✓\n\n"

        report += "## 修改建议\n\n"
        for i, sug in enumerate(suggestions, 1):
            report += f"{i}. {sug}\n"

        return report
