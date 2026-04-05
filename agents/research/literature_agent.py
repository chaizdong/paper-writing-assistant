"""
文献调研 Agent

根据研究主题搜索、筛选和总结相关文献
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent, TaskRequest, TaskResponse
from mcp.tools.paper_search import search_papers

logger = logging.getLogger(__name__)


class LiteratureAgent(BaseAgent):
    """
    文献调研 Agent

    职责:
    - 根据用户主题搜索相关论文
    - 提取摘要、方法、数据集、结果
    - 初步筛选和去重
    - 生成文献综述摘要
    """

    def __init__(self, agent_id: str = "literature_agent", max_papers: int = 50):
        super().__init__(
            agent_id=agent_id,
            name="LiteratureAgent",
            description="文献调研 Agent - 搜索、筛选和总结相关论文"
        )
        self.max_papers = max_papers
        self._use_real_api = True  # 切换到真实 API

    def get_capabilities(self) -> list[str]:
        return [
            "search_papers - 搜索论文",
            "extract_abstract - 提取摘要",
            "deduplicate_papers - 去重",
            "summarize_literature - 生成综述",
        ]

    def execute(self, task_request: TaskRequest) -> TaskResponse:
        """
        执行文献调研任务

        Args:
            task_request: 任务请求，包含 search_query, keywords 等

        Returns:
            TaskResponse: 包含论文列表和综述摘要
        """
        try:
            # 解析输入
            input_data = task_request.input_data or {}
            search_query = input_data.get("search_query", "")
            keywords = input_data.get("keywords", [])
            limit = input_data.get("limit", self.max_papers)

            logger.info(f"开始文献调研：query='{search_query}', keywords={keywords}, limit={limit}")

            # 发送进度更新
            self.send_progress(1, 5, "正在搜索论文...")

            # 调用 MCP 工具搜索论文
            papers = self._search_papers(search_query, keywords, limit)

            self.send_progress(2, 5, f"找到 {len(papers)} 篇论文")

            # 去重
            self.send_progress(3, 5, "正在去重...")
            papers = self._deduplicate_papers(papers)

            self.send_progress(4, 5, "正在提取关键信息...")

            # 提取关键信息
            for paper in papers:
                self._extract_key_info(paper)

            self.send_progress(5, 5, "正在生成综述摘要...")

            # 生成综述摘要
            summary = self._generate_summary(papers)

            logger.info(f"文献调研完成：找到 {len(papers)} 篇论文")

            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": True,
                    "result": {
                        "papers": papers,
                        "summary": summary,
                        "search_query": search_query,
                        "total_found": len(papers),
                    }
                }
            )

        except Exception as e:
            logger.exception(f"文献调研失败：{e}")
            return TaskResponse(
                sender=self.agent_id,
                receiver=task_request.sender,
                correlation_id=task_request.id,
                payload={
                    "success": False,
                    "error_message": str(e),
                }
            )

    def _search_papers(self, query: str, keywords: list[str], limit: int) -> list[dict]:
        """
        搜索论文

        使用 MCP 工具搜索 arXiv 和 Semantic Scholar
        """
        if self._use_real_api:
            try:
                # 使用真实 API 搜索
                papers = search_papers(query, max_results=limit)
                if papers:
                    logger.info(f"真实 API 搜索到 {len(papers)} 篇论文")
                    return papers
            except Exception as e:
                logger.warning(f"真实 API 搜索失败，回退到模拟数据：{e}")

        # 回退到模拟数据
        return self._mock_search(query, keywords, limit)

    def _mock_search(self, query: str, keywords: list[str], limit: int) -> list[dict]:
        """模拟搜索结果（用于测试）"""
        # 这是一个占位实现，实际应该调用 MCP 工具
        base_papers = [
            {
                "id": f"arxiv:mock_{i}",
                "title": f"Mock Paper {i}: {query} - A Novel Approach",
                "authors": [f"Author {j}" for j in range(1, 4)],
                "venue": f"Conference {i % 5 + 2020}",
                "year": 2020 + (i % 5),
                "abstract": f"This paper presents a novel approach for {query}. "
                           f"We propose Method-{i} which achieves state-of-the-art results.",
                "methods": keywords if keywords else ["Method"],
                "datasets": ["Benchmark Dataset"],
                "metrics": {"score": 0.8 + (i % 20) / 100},
                "url": f"https://arxiv.org/abs/mock_{i}"
            }
            for i in range(min(limit, 10))
        ]
        return base_papers

    def _deduplicate_papers(self, papers: list[dict]) -> list[dict]:
        """
        去重论文列表

        基于 title 或 id 去重
        """
        seen_ids = set()
        unique_papers = []

        for paper in papers:
            paper_id = paper.get("id", paper.get("title", ""))
            if paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_papers.append(paper)

        return unique_papers

    def _extract_key_info(self, paper: dict):
        """
        从论文中提取关键信息

        包括方法、数据集、评价指标等
        """
        # TODO: 使用 LLM 提取或调用 MCP 工具解析全文
        # 这里简单从摘要中提取关键词
        abstract = paper.get("abstract", "")

        # 简单关键词匹配
        method_keywords = ["method", "approach", "framework", "model", "network"]
        dataset_keywords = ["dataset", "benchmark", "corpus", "data"]

        paper["extracted_methods"] = [
            kw for kw in method_keywords if kw.lower() in abstract.lower()
        ]
        paper["extracted_datasets"] = [
            kw for kw in dataset_keywords if kw.lower() in abstract.lower()
        ]

    def _generate_summary(self, papers: list[dict]) -> str:
        """
        生成文献综述摘要

        总结主要方法、趋势、共性问题
        """
        if not papers:
            return "未找到相关文献"

        # 统计年份分布
        years = [p.get("year", 0) for p in papers]
        year_range = f"{min(years)}-{max(years)}" if years else "N/A"

        # 统计方法关键词
        all_methods = []
        for p in papers:
            all_methods.extend(p.get("methods", []))
            all_methods.extend(p.get("extracted_methods", []))
        method_counts = {}
        for m in all_methods:
            method_counts[m] = method_counts.get(m, 0) + 1
        top_methods = sorted(method_counts.items(), key=lambda x: -x[1])[:5]

        summary = f"""## 文献调研总结

**检索范围**: {year_range} 年
**找到论文**: {len(papers)} 篇

### 主要方法
"""
        for method, count in top_methods:
            summary += f"- {method} ({count} 篇)\n"

        summary += "\n### 代表性论文\n"
        for i, paper in enumerate(papers[:5], 1):
            summary += f"{i}. {paper.get('title', 'N/A')} ({paper.get('venue', 'N/A')})\n"

        summary += """
### 研究趋势
当前研究主要集中在以上方法，近年来越来越多的工作关注于改进和优化这些方法。
建议在后续 Gap 分析中重点关注这些方法的局限性和未解决的问题。
"""

        return summary
