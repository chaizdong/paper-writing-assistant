"""
arXiv MCP 客户端

用于搜索和下载 arXiv 论文
支持：
- 按关键词搜索
- 按分类筛选
- 获取摘要和全文链接
- 批量下载
"""

import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ArXivClient:
    """
    arXiv API 客户端

    使用 arXiv API: https://arxiv.org/help/api
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    # arXiv 分类
    CATEGORIES = {
        "cs": "Computer Science",
        "cs.AI": "Artificial Intelligence",
        "cs.CL": "Computation and Language",
        "cs.CV": "Computer Vision",
        "cs.LG": "Machine Learning",
        "cs.NE": "Neural and Evolutionary Computing",
        "stat": "Statistics",
        "stat.ML": "Machine Learning",
        "math": "Mathematics",
        "physics": "Physics",
    }

    def __init__(
        self,
        max_results: int = 50,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ):
        """
        初始化 arXiv 客户端

        Args:
            max_results: 最大返回结果数
            sort_by: 排序方式 (relevance, lastUpdatedDate, submittedDate)
            sort_order: 排序顺序 (ascending, descending)
        """
        self.max_results = max_results
        self.sort_by = sort_by
        self.sort_order = sort_order
        self._delay_seconds = 3  # arXiv 要求请求间隔至少 3 秒
        logger.info(f"ArXivClient 已初始化：max_results={max_results}")

    def search(
        self,
        query: str,
        categories: list[str] = None,
        max_results: int = None,
        start: int = 0,
    ) -> list[dict]:
        """
        搜索 arXiv 论文

        Args:
            query: 搜索关键词
            categories: 分类过滤（如 ["cs.AI", "cs.LG"]）
            max_results: 最大结果数
            start: 起始位置

        Returns:
            论文列表
        """
        max_results = max_results or self.max_results

        # 构建搜索查询
        search_query = self._build_query(query, categories)

        # 构建 URL
        params = {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": self.sort_by,
            "sortOrder": self.sort_order,
        }

        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

        logger.info(f"搜索 arXiv: {url}")

        try:
            # 发送请求
            with urllib.request.urlopen(url, timeout=30) as response:
                xml_data = response.read().decode("utf-8")

            # 解析 XML
            papers = self._parse_response(xml_data)
            logger.info(f"arXiv 搜索完成：找到 {len(papers)} 篇论文")

            return papers

        except Exception as e:
            logger.exception(f"arXiv 搜索失败：{e}")
            return []

    def _build_query(self, query: str, categories: list[str] = None) -> str:
        """
        构建 arXiv 搜索查询

        arXiv 搜索语法:
        - all: 在所有字段搜索
        - ti: 标题
        - au: 作者
        - abs: 摘要
        - AND, OR, ANDNOT: 布尔运算符
        """
        # 主要搜索字段：标题、摘要
        search_terms = []

        # 处理关键词
        keywords = query.split()
        for kw in keywords:
            # 转义特殊字符
            kw = urllib.parse.quote(kw, safe="")
            search_terms.append(f"(all:{kw})")

        base_query = " AND ".join(search_terms)

        # 添加分类过滤
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            base_query = f"({base_query}) AND ({cat_query})"

        return base_query

    def _parse_response(self, xml_data: str) -> list[dict]:
        """解析 arXiv XML 响应"""
        papers = []

        # 定义命名空间
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        root = ET.fromstring(xml_data)

        for entry in root.findall("atom:entry", ns):
            paper = self._parse_entry(entry, ns)
            if paper:
                papers.append(paper)

        return papers

    def _parse_entry(self, entry: ET.Element, ns: dict) -> Optional[dict]:
        """解析单篇论文条目"""
        try:
            # ID
            id_elem = entry.find("atom:id", ns)
            paper_id = id_elem.text if id_elem is not None else ""

            # 提取 arXiv ID
            arxiv_id = paper_id.split("/abs/")[-1] if "/abs/" in paper_id else ""

            # 标题
            title_elem = entry.find("atom:title", ns)
            title = title_elem.text.strip() if title_elem is not None else "N/A"

            # 作者
            authors = []
            for author_elem in entry.findall("atom:author", ns):
                name_elem = author_elem.find("atom:name", ns)
                if name_elem is not None:
                    authors.append(name_elem.text)

            # 摘要
            summary_elem = entry.find("atom:summary", ns)
            abstract = summary_elem.text.strip() if summary_elem is not None else ""

            # 分类
            categories = []
            for cat_elem in entry.findall("atom:category", ns):
                term = cat_elem.get("term")
                if term:
                    categories.append(term)

            # 发布日期
            published_elem = entry.find("atom:published", ns)
            published = published_elem.text if published_elem is not None else ""

            # PDF 链接
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    pdf_url = link.get("href", "")
                    break

            # 如果没有找到 PDF 链接，使用 arXiv ID 构建
            if not pdf_url and arxiv_id:
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

            return {
                "id": f"arxiv:{arxiv_id}",
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "categories": categories,
                "published": published,
                "year": published[:4] if published else "",
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": pdf_url,
                "venue": "arXiv",
            }

        except Exception as e:
            logger.exception(f"解析论文条目失败：{e}")
            return None

    def get_paper_details(self, arxiv_id: str) -> Optional[dict]:
        """
        获取单篇论文详情

        Args:
            arxiv_id: arXiv ID (如 "2301.12345")

        Returns:
            论文详情
        """
        results = self.search(f"id:{arxiv_id}", max_results=1)
        return results[0] if results else None

    def search_by_author(self, author: str, max_results: int = None) -> list[dict]:
        """
        按作者搜索

        Args:
            author: 作者姓名
            max_results: 最大结果数

        Returns:
            论文列表
        """
        query = f"au:\"{author}\""
        return self.search(query, max_results=max_results)

    def search_by_category(
        self,
        category: str,
        date_from: str = None,
        max_results: int = None,
    ) -> list[dict]:
        """
        按分类搜索

        Args:
            category: 分类（如 "cs.AI"）
            date_from: 起始日期（YYYYMMDD）
            max_results: 最大结果数

        Returns:
            论文列表
        """
        query = f"cat:{category}"

        if date_from:
            query += f" AND submittedDate:[{date_from} TO 99991231]"

        return self.search(query, max_results=max_results)

    def download_pdf(self, arxiv_id: str, save_path: str) -> bool:
        """
        下载 PDF 文件

        Args:
            arxiv_id: arXiv ID
            save_path: 保存路径

        Returns:
            是否成功
        """
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        try:
            logger.info(f"下载 PDF: {pdf_url} -> {save_path}")
            urllib.request.urlretrieve(pdf_url, save_path)
            return True
        except Exception as e:
            logger.exception(f"下载 PDF 失败：{e}")
            return False

    @classmethod
    def list_categories(cls) -> dict[str, str]:
        """列出所有可用分类"""
        return cls.CATEGORIES.copy()


# 全局客户端实例
_client: Optional[ArXivClient] = None


def get_client() -> ArXivClient:
    """获取全局 ArXiv 客户端实例"""
    global _client
    if _client is None:
        _client = ArXivClient()
    return _client


def search_papers(
    query: str,
    categories: list[str] = None,
    max_results: int = 50,
) -> list[dict]:
    """
    便捷函数：搜索 arXiv 论文

    Args:
        query: 搜索关键词
        categories: 分类过滤
        max_results: 最大结果数

    Returns:
        论文列表
    """
    client = get_client()
    client.max_results = max_results
    return client.search(query, categories, max_results)
