"""
Semantic Scholar MCP 客户端

用于搜索和分析学术论文
支持：
- 论文搜索
- 引用分析
- 作者信息
- 相关推荐
"""

import logging
import urllib.parse
import urllib.request
import json
from typing import Optional

logger = logging.getLogger(__name__)


class SemanticScholarClient:
    """
    Semantic Scholar API 客户端

    使用 Semantic Scholar API: https://api.semantics.org/api-docs/
    免费层限制：100 请求/天
    """

    BASE_URL = "https://api.semantics.org/graph/v1"

    def __init__(
        self,
        api_key: str = None,
        max_results: int = 50,
    ):
        """
        初始化 Semantic Scholar 客户端

        Args:
            api_key: API 密钥（可选，免费层不需要）
            max_results: 最大返回结果数
        """
        self.api_key = api_key
        self.max_results = max_results
        self._base_headers = {"User-Agent": "PaperWritingAssistant/1.0"}

        if api_key:
            self._base_headers["x-api-key"] = api_key

        logger.info(f"SemanticScholarClient 已初始化：max_results={max_results}")

    def search(
        self,
        query: str,
        fields: list[str] = None,
        year_range: tuple[int, int] = None,
        max_results: int = None,
    ) -> list[dict]:
        """
        搜索论文

        Args:
            query: 搜索关键词
            fields: 返回字段（如 ["title", "abstract", "authors", "venue"]）
            year_range: 年份范围 (start, end)
            max_results: 最大结果数

        Returns:
            论文列表
        """
        max_results = max_results or self.max_results

        # 默认返回字段
        if fields is None:
            fields = [
                "title",
                "abstract",
                "authors",
                "venue",
                "year",
                "citationCount",
                "influentialCitationCount",
                "publicationDate",
                "url",
            ]

        # 构建 URL
        encoded_query = urllib.parse.quote(query, safe="")
        url = f"{self.BASE_URL}/paper/search?query={encoded_query}&limit={max_results}"

        # 添加字段参数
        fields_str = ",".join(fields)
        url += f"&fields={fields_str}"

        # 年份过滤
        if year_range:
            start, end = year_range
            url += f"&year={start}-{end}"

        logger.info(f"搜索 Semantic Scholar: {url}")

        try:
            # 发送请求
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            # 解析结果
            papers = self._parse_response(data.get("data", []))
            logger.info(f"Semantic Scholar 搜索完成：找到 {len(papers)} 篇论文")

            return papers

        except Exception as e:
            logger.exception(f"Semantic Scholar 搜索失败：{e}")
            return []

    def _parse_response(self, papers_data: list[dict]) -> list[dict]:
        """解析 API 响应"""
        papers = []

        for paper in papers_data:
            parsed = self._parse_paper(paper)
            if parsed:
                papers.append(parsed)

        return papers

    def _parse_paper(self, paper: dict) -> Optional[dict]:
        """解析单篇论文"""
        try:
            # 提取作者
            authors = []
            for author in paper.get("authors", []):
                if isinstance(author, dict):
                    authors.append(author.get("name", ""))
                else:
                    authors.append(str(author))

            # 构建 URL
            paper_id = paper.get("paperId", "")
            url = paper.get("url", f"https://www.semanticscholar.org/paper/{paper_id}")

            return {
                "id": f"semanticscholar:{paper_id}",
                "paper_id": paper_id,
                "title": paper.get("title", "N/A"),
                "authors": authors,
                "abstract": paper.get("abstract", ""),
                "venue": paper.get("venue", ""),
                "year": paper.get("year", ""),
                "citation_count": paper.get("citationCount", 0),
                "influential_citation_count": paper.get(
                    "influentialCitationCount", 0
                ),
                "publication_date": paper.get("publicationDate", ""),
                "url": url,
                "source": "Semantic Scholar",
            }

        except Exception as e:
            logger.exception(f"解析论文失败：{e}")
            return None

    def get_paper_by_id(self, paper_id: str, fields: list[str] = None) -> Optional[dict]:
        """
        按 ID 获取论文详情

        Args:
            paper_id: Semantic Scholar Paper ID
            fields: 返回字段

        Returns:
            论文详情
        """
        if fields is None:
            fields = [
                "title",
                "abstract",
                "authors",
                "venue",
                "year",
                "citationCount",
                "references",
                "tldr",
            ]

        url = f"{self.BASE_URL}/paper/{paper_id}"
        fields_str = ",".join(fields)
        url += f"?fields={fields_str}"

        try:
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            return self._parse_paper(data)

        except Exception as e:
            logger.exception(f"获取论文详情失败：{e}")
            return None

    def search_by_author(
        self,
        author_name: str,
        max_results: int = None,
    ) -> list[dict]:
        """
        按作者搜索

        Args:
            author_name: 作者姓名
            max_results: 最大结果数

        Returns:
            论文列表
        """
        # 首先搜索作者
        url = f"{self.BASE_URL}/author/search?query={urllib.parse.quote(author_name)}&limit=1"

        try:
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            if data.get("data"):
                author_id = data["data"][0]["authorId"]
                return self.get_author_papers(author_id, max_results)

        except Exception as e:
            logger.exception(f"搜索作者失败：{e}")

        return []

    def get_author_papers(
        self,
        author_id: str,
        max_results: int = None,
    ) -> list[dict]:
        """
        获取作者的论文列表

        Args:
            author_id: 作者 ID
            max_results: 最大结果数

        Returns:
            论文列表
        """
        max_results = max_results or self.max_results

        url = f"{self.BASE_URL}/author/{author_id}?fields=papers"

        try:
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            papers_data = data.get("papers", [])[:max_results]
            return self._parse_response(papers_data)

        except Exception as e:
            logger.exception(f"获取作者论文失败：{e}")
            return []

    def get_citations(
        self,
        paper_id: str,
        max_results: int = None,
    ) -> list[dict]:
        """
        获取引用该论文的文章

        Args:
            paper_id: 论文 ID
            max_results: 最大结果数

        Returns:
            引用论文列表
        """
        max_results = max_results or self.max_results

        url = f"{self.BASE_URL}/paper/{paper_id}/citations?limit={max_results}"

        try:
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            citations_data = data.get("citations", [])
            return self._parse_response(citations_data)

        except Exception as e:
            logger.exception(f"获取引用失败：{e}")
            return []

    def get_references(
        self,
        paper_id: str,
        max_results: int = None,
    ) -> list[dict]:
        """
        获取该论文引用的文章

        Args:
            paper_id: 论文 ID
            max_results: 最大结果数

        Returns:
            参考文献列表
        """
        max_results = max_results or self.max_results

        url = f"{self.BASE_URL}/paper/{paper_id}/references?limit={max_results}"

        try:
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            references_data = data.get("references", [])
            return self._parse_response(references_data)

        except Exception as e:
            logger.exception(f"获取参考文献失败：{e}")
            return []

    def get_recommendations(
        self,
        paper_id: str,
        max_results: int = None,
    ) -> list[dict]:
        """
        获取相关论文推荐

        Args:
            paper_id: 论文 ID
            max_results: 最大结果数

        Returns:
            推荐论文列表
        """
        max_results = max_results or self.max_results

        url = f"{self.BASE_URL}/paper/{paper_id}/recommendations?limit={max_results}"

        try:
            req = urllib.request.Request(url, headers=self._base_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            recommendations_data = data.get("recommendations", [])
            return self._parse_response(recommendations_data)

        except Exception as e:
            logger.exception(f"获取推荐失败：{e}")
            return []


# 全局客户端实例
_client: Optional[SemanticScholarClient] = None


def get_client(api_key: str = None) -> SemanticScholarClient:
    """获取全局 Semantic Scholar 客户端实例"""
    global _client
    if _client is None:
        _client = SemanticScholarClient(api_key=api_key)
    return _client


def search_papers(
    query: str,
    year_range: tuple[int, int] = None,
    max_results: int = 50,
) -> list[dict]:
    """
    便捷函数：搜索 Semantic Scholar 论文

    Args:
        query: 搜索关键词
        year_range: 年份范围
        max_results: 最大结果数

    Returns:
        论文列表
    """
    client = get_client()
    client.max_results = max_results
    return client.search(query, year_range=year_range, max_results=max_results)
