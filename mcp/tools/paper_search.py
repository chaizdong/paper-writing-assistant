"""
MCP 工具集成 - 论文搜索服务

整合 arXiv 和 Semantic Scholar 的搜索能力
提供统一的论文搜索接口
"""

import logging
from typing import Optional

from mcp.tool_registry import get_registry
from mcp.clients.arxiv_client import ArXivClient
from mcp.clients.semantic_scholar_client import SemanticScholarClient

logger = logging.getLogger(__name__)


class PaperSearchService:
    """
    论文搜索服务

    整合多个数据源的搜索结果
    """

    def __init__(self):
        self.arxiv_client = ArXivClient(max_results=50)
        self.semantic_scholar_client = SemanticScholarClient(max_results=50)
        self._registry = get_registry()
        self._register_tools()

    def _register_tools(self):
        """注册工具到注册中心"""
        registry = self._registry

        # 注册 arXiv 搜索工具
        registry.register_tool(
            name="arxiv_search",
            description="搜索 arXiv 论文",
            handler=self.search_arxiv,
            parameters={
                "query": {"type": "string", "required": True, "description": "搜索关键词"},
                "categories": {
                    "type": "array",
                    "required": False,
                    "description": "arXiv 分类过滤",
                },
                "max_results": {
                    "type": "integer",
                    "required": False,
                    "description": "最大结果数",
                    "default": 50,
                },
            },
        )

        # 注册 Semantic Scholar 搜索工具
        registry.register_tool(
            name="semantic_scholar_search",
            description="搜索 Semantic Scholar 论文",
            handler=self.search_semantic_scholar,
            parameters={
                "query": {"type": "string", "required": True, "description": "搜索关键词"},
                "year_range": {
                    "type": "array",
                    "required": False,
                    "description": "年份范围 [start, end]",
                },
                "max_results": {
                    "type": "integer",
                    "required": False,
                    "description": "最大结果数",
                    "default": 50,
                },
            },
        )

        # 注册统一搜索工具
        registry.register_tool(
            name="search_papers",
            description="搜索论文（多数据源）",
            handler=self.search_all,
            parameters={
                "query": {"type": "string", "required": True, "description": "搜索关键词"},
                "sources": {
                    "type": "array",
                    "required": False,
                    "description": "数据源 [arxiv, semantic_scholar]",
                    "default": ["arxiv", "semantic_scholar"],
                },
                "max_results": {
                    "type": "integer",
                    "required": False,
                    "description": "最大结果数",
                    "default": 50,
                },
            },
        )

        logger.info("PaperSearchService 工具已注册")

    def search_arxiv(
        self,
        query: str,
        categories: list[str] = None,
        max_results: int = 50,
    ) -> list[dict]:
        """
        搜索 arXiv 论文

        Args:
            query: 搜索关键词
            categories: 分类过滤
            max_results: 最大结果数

        Returns:
            论文列表
        """
        logger.info(f"arXiv 搜索：{query}")
        return self.arxiv_client.search(query, categories, max_results)

    def search_semantic_scholar(
        self,
        query: str,
        year_range: tuple[int, int] = None,
        max_results: int = 50,
    ) -> list[dict]:
        """
        搜索 Semantic Scholar 论文

        Args:
            query: 搜索关键词
            year_range: 年份范围
            max_results: 最大结果数

        Returns:
            论文列表
        """
        logger.info(f"Semantic Scholar 搜索：{query}")
        return self.semantic_scholar_client.search(query, year_range=year_range, max_results=max_results)

    def search_all(
        self,
        query: str,
        sources: list[str] = None,
        max_results: int = 50,
    ) -> list[dict]:
        """
        多数据源搜索

        Args:
            query: 搜索关键词
            sources: 数据源列表
            max_results: 每个数据源的最大结果数

        Returns:
            合并后的论文列表（已去重）
        """
        if sources is None:
            sources = ["arxiv", "semantic_scholar"]

        all_papers = []

        # 搜索各数据源
        if "arxiv" in sources:
            arxiv_papers = self.search_arxiv(query, max_results=max_results)
            all_papers.extend(arxiv_papers)
            logger.info(f"arXiv 找到 {len(arxiv_papers)} 篇论文")

        if "semantic_scholar" in sources:
            ss_papers = self.search_semantic_scholar(query, max_results=max_results)
            all_papers.extend(ss_papers)
            logger.info(f"Semantic Scholar 找到 {len(ss_papers)} 篇论文")

        # 去重
        deduped_papers = self._deduplicate_papers(all_papers)
        logger.info(f"合并后共 {len(deduped_papers)} 篇论文")

        return deduped_papers

    def _deduplicate_papers(self, papers: list[dict]) -> list[dict]:
        """
        去重论文列表

        基于标题进行去重
        """
        seen_titles = set()
        unique_papers = []

        for paper in papers:
            # 标准化标题（小写、去除空格）
            title = paper.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)

        return unique_papers


# 全局服务实例
_service: Optional[PaperSearchService] = None


def get_service() -> PaperSearchService:
    """获取全局 PaperSearchService 实例"""
    global _service
    if _service is None:
        _service = PaperSearchService()
    return _service


def search_papers(query: str, max_results: int = 50) -> list[dict]:
    """
    便捷函数：搜索论文

    Args:
        query: 搜索关键词
        max_results: 最大结果数

    Returns:
        论文列表
    """
    service = get_service()
    return service.search_all(query, max_results=max_results)
