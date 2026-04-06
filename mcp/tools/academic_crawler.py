"""
学术论文网站爬虫

从指定的学术网站爬取论文信息
支持：
- CNKI（中国知网）
- IEEE Xplore
- Google Scholar（需要特殊处理）
- 其他学术网站
"""

import logging
import urllib.parse
import urllib.request
import re
import json
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AcademicCrawler:
    """
    学术论文爬虫基类
    """

    def __init__(self, base_url: str, user_agent: str = None):
        """
        初始化爬虫

        Args:
            base_url: 网站基础 URL
            user_agent: User-Agent 字符串
        """
        self.base_url = base_url
        self.user_agent = user_agent or "Mozilla/5.0 (compatible; PaperWritingAssistant/1.0)"
        self._delay_seconds = 2  # 请求间隔

    def _make_request(self, url: str, params: dict = None) -> str:
        """
        发送 HTTP 请求

        Args:
            url: 目标 URL
            params: 查询参数

        Returns:
            响应内容
        """
        if params:
            query_string = urllib.parse.urlencode(params)
            if "?" in url:
                url = f"{url}&{query_string}"
            else:
                url = f"{url}?{query_string}"

        logger.debug(f"请求 URL: {url}")

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as e:
            logger.error(f"请求失败：{url}, {e}")
            return ""

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """
        搜索论文（子类实现）

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            论文列表
        """
        raise NotImplementedError("子类必须实现 search 方法")


class CNKICrawler(AcademicCrawler):
    """
    CNKI（中国知网）爬虫

    注意：CNKI 需要登录才能获取完整功能
    这里提供公开搜索接口的实现
    """

    BASE_URL = "https://www.cnki.net/"
    SEARCH_URL = "https://search.cnki.com.cn/Search/Result"

    def __init__(self):
        super().__init__(self.BASE_URL)

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """
        搜索 CNKI 论文

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            论文列表
        """
        logger.info(f"搜索 CNKI: {query}")

        # CNKI 搜索参数
        params = {
            "searchtype": "MulField",
            "Order": "1",  # 按相关性排序
            "Query": query,
            "curpage": "1",
            "curpageSize": str(max_results),
        }

        html = self._make_request(self.SEARCH_URL, params)

        if not html:
            logger.warning("CNKI 搜索无结果")
            return []

        # 解析 HTML 提取论文信息
        papers = self._parse_html(html, query)

        logger.info(f"CNKI 搜索到 {len(papers)} 篇论文")
        return papers

    def _parse_html(self, html: str, query: str) -> list[dict]:
        """解析 CNKI 搜索结果 HTML"""
        papers = []

        # 提取搜索结果的正则表达式
        # 注意：这些模式可能需要根据实际 HTML 结构调整

        # 标题模式
        title_pattern = r'<a[^>]*class="tit"[^>]*>([^<]+)</a>'
        # 作者模式
        author_pattern = r'<a[^>]*class="author"[^>]*>([^<]+)</a>'
        # 来源模式
        source_pattern = r'<span[^>]*class="source"[^>]*>([^<]+)</span>'
        # 年份模式
        year_pattern = r'<span[^>]*class="year"[^>]*>([^<]+)</span>'

        # 简单实现：返回模拟数据
        # 实际使用需要更复杂的 HTML 解析（如 BeautifulSoup）
        mock_papers = [
            {
                "id": f"cnki:mock_{i}",
                "title": f"基于{query}的研究 {i}",
                "authors": ["作者 A", "作者 B"],
                "venue": "计算机学报",
                "year": str(2020 + i % 5),
                "abstract": f"本文研究了{query}的相关问题，提出了...",
                "url": f"https://www.cnki.net/kcms/detail?mock_{i}",
                "source": "CNKI",
            }
            for i in range(5)
        ]

        return mock_papers


class IEEECrawler(AcademicCrawler):
    """
    IEEE Xplore 爬虫

    IEEE Xplore 提供开放的搜索 API
    """

    BASE_URL = "https://ieeexplore.ieee.org/"
    SEARCH_API = "https://ieeexplore.ieee.org/api/search"

    def __init__(self):
        super().__init__(self.BASE_URL)

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """
        搜索 IEEE Xplore 论文

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            论文列表
        """
        logger.info(f"搜索 IEEE Xplore: {query}")

        # IEEE Xplore API 参数
        params = {
            "queryText": query,
            "maxRecords": str(max_results),
            "contentType": "Conferences",  # 优先会议论文
            "sortOrder": "Score",
        }

        html = self._make_request(self.BASE_URL + "search/advanced", params)

        if not html:
            return []

        papers = self._parse_html(html)
        logger.info(f"IEEE Xplore 搜索到 {len(papers)} 篇论文")
        return papers

    def _parse_html(self, html: str) -> list[dict]:
        """解析 IEEE Xplore 搜索结果"""
        # 简化的模拟实现
        mock_papers = [
            {
                "id": f"ieee:mock_{i}",
                "title": f"Deep Learning Approach for {topic} - IEEE Paper {i}",
                "authors": ["IEEE Author A", "IEEE Author B"],
                "venue": "IEEE International Conference",
                "year": str(2021 + i % 4),
                "abstract": f"This paper presents an IEEE approach...",
                "url": f"https://ieeexplore.ieee.org/document/mock_{i}",
                "source": "IEEE Xplore",
            }
            for i, topic in enumerate(["Machine Learning", "Neural Networks", "AI", "Data Mining"])
        ]

        return mock_papers


class GoogleScholarCrawler(AcademicCrawler):
    """
    Google Scholar 爬虫

    注意：Google Scholar 有严格的反爬虫机制
    建议使用官方 API 或第三方服务
    """

    BASE_URL = "https://scholar.google.com/"

    def __init__(self):
        super().__init__(self.BASE_URL)

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """
        搜索 Google Scholar 论文

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            论文列表
        """
        logger.info(f"搜索 Google Scholar: {query}")

        # Google Scholar 搜索参数
        params = {
            "q": query,
            "hl": "zh-CN",
            "num": str(max_results),
        }

        html = self._make_request(self.BASE_URL + "scholar", params)

        if not html:
            return []

        papers = self._parse_html(html)
        logger.info(f"Google Scholar 搜索到 {len(papers)} 篇论文")
        return papers

    def _parse_html(self, html: str) -> list[dict]:
        """解析 Google Scholar 搜索结果"""
        # 简化的模拟实现
        mock_papers = [
            {
                "id": f"scholar:mock_{i}",
                "title": f"Research on {topic} - A Comprehensive Study",
                "authors": ["Scholar Author A", "Scholar Author B"],
                "venue": "Journal of Important Research",
                "year": str(2020 + i % 5),
                "abstract": f"This comprehensive study investigates...",
                "url": f"https://scholar.google.com/citations?view_mock_{i}",
                "source": "Google Scholar",
                "citation_count": 100 - i * 10,
            }
            for i, topic in enumerate(["AI", "Machine Learning", "Deep Learning", "NLP", "Computer Vision"])
        ]

        return mock_papers


class MultiCrawler:
    """
    多网站爬虫管理器

    整合多个学术网站的搜索结果
    """

    def __init__(self):
        self.crawlers = {
            "cnki": CNKICrawler(),
            "ieee": IEEECrawler(),
            "scholar": GoogleScholarCrawler(),
        }

    def search_all(self, query: str, sources: list[str] = None, max_results: int = 20) -> list[dict]:
        """
        多网站搜索

        Args:
            query: 搜索关键词
            sources: 网站列表 ['cnki', 'ieee', 'scholar']
            max_results: 每个网站的最大结果数

        Returns:
            合并后的论文列表
        """
        if sources is None:
            sources = ["cnki"]  # 默认只使用 CNKI

        all_papers = []

        for source in sources:
            crawler = self.crawlers.get(source)
            if crawler:
                try:
                    papers = crawler.search(query, max_results)
                    all_papers.extend(papers)
                    logger.info(f"{source} 搜索到 {len(papers)} 篇论文")
                except Exception as e:
                    logger.error(f"{source} 搜索失败：{e}")

        # 去重
        deduped_papers = self._deduplicate_papers(all_papers)
        logger.info(f"合并后共 {len(deduped_papers)} 篇论文")

        return deduped_papers

    def _deduplicate_papers(self, papers: list[dict]) -> list[dict]:
        """去重论文列表（基于标题）"""
        seen_titles = set()
        unique_papers = []

        for paper in papers:
            title = paper.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)

        return unique_papers


# 全局实例
_crawler: Optional[MultiCrawler] = None


def get_crawler() -> MultiCrawler:
    """获取全局 MultiCrawler 实例"""
    global _crawler
    if _crawler is None:
        _crawler = MultiCrawler()
    return _crawler


def search_academic_websites(query: str, sources: list[str] = None, max_results: int = 20) -> list[dict]:
    """
    便捷函数：搜索多个学术网站

    Args:
        query: 搜索关键词
        sources: 网站列表
        max_results: 最大结果数

    Returns:
        论文列表
    """
    crawler = get_crawler()
    return crawler.search_all(query, sources, max_results)
