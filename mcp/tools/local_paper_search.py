"""
本地论文搜索工具

从指定目录扫描和解析论文文件（PDF、TXT、MD 等）
支持：
- PDF 文件扫描
- 元数据提取
- 批量导入
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class LocalPaperSearcher:
    """
    本地论文搜索器

    从指定目录扫描和解析论文文件
    """

    # 支持的文件格式
    SUPPORTED_FORMATS = {'.pdf', '.txt', '.md', '.tex', '.epub'}

    def __init__(self, default_dirs: list[str] = None):
        """
        初始化本地搜索器

        Args:
            default_dirs: 默认搜索目录列表
        """
        self.default_dirs = default_dirs or []
        logger.info(f"LocalPaperSearcher 已初始化，默认目录：{self.default_dirs}")

    def scan_directory(self, directory: str, recursive: bool = True) -> list[dict]:
        """
        扫描目录中的论文文件

        Args:
            directory: 目录路径
            recursive: 是否递归搜索子目录

        Returns:
            论文文件列表
        """
        papers = []
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.warning(f"目录不存在：{directory}")
            return papers

        if not dir_path.is_dir():
            logger.warning(f"不是目录：{directory}")
            return papers

        # 遍历文件
        pattern = "**/*" if recursive else "*"
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                paper_info = self._parse_file(file_path)
                if paper_info:
                    papers.append(paper_info)

        logger.info(f"扫描目录 {directory}，找到 {len(papers)} 篇论文")
        return papers

    def _parse_file(self, file_path: Path) -> Optional[dict]:
        """
        解析文件，提取论文信息

        Args:
            file_path: 文件路径

        Returns:
            论文信息字典
        """
        try:
            # 从文件名提取信息
            filename = file_path.name
            title = self._extract_title_from_filename(filename)

            paper_info = {
                "id": f"local:{file_path}",
                "file_path": str(file_path),
                "filename": filename,
                "title": title,
                "authors": [],
                "abstract": "",
                "year": "",
                "venue": "本地文件",
                "url": "",
                "source": "local",
            }

            # 尝试读取文件内容提取元数据
            if file_path.suffix.lower() in {'.txt', '.md', '.tex'}:
                content = self._read_text_file(file_path)
                metadata = self._extract_metadata(content)
                paper_info.update(metadata)
            elif file_path.suffix.lower() == '.pdf':
                # PDF 文件尝试提取元数据
                metadata = self._extract_pdf_metadata(file_path)
                paper_info.update(metadata)

            return paper_info

        except Exception as e:
            logger.exception(f"解析文件失败：{file_path}, {e}")
            return None

    def _extract_title_from_filename(self, filename: str) -> str:
        """从文件名提取标题"""
        # 移除扩展名
        name = Path(filename).stem

        # 替换下划线和连字符为空格
        title = re.sub(r'[_-]', ' ', name)

        # 移除常见的论文编号前缀
        title = re.sub(r'^\d+[-_\.]?\s*', '', title)
        title = re.sub(r'^paper[-_]?', '', title, flags=re.IGNORECASE)

        # 首字母大写
        title = title.strip().title()

        return title

    def _read_text_file(self, file_path: Path, max_lines: int = 100) -> str:
        """读取文本文件的前若干行"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
                return ''.join(lines)
        except Exception as e:
            logger.warning(f"读取文件失败：{file_path}, {e}")
            return ""

    def _extract_metadata(self, content: str) -> dict:
        """
        从文件内容提取元数据

        Args:
            content: 文件内容

        Returns:
            元数据字典
        """
        metadata = {
            "authors": [],
            "abstract": "",
            "year": "",
        }

        if not content:
            return metadata

        lines = content.split('\n')

        # 尝试提取标题（通常在前几行）
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if line and not line.startswith('#'):
                if not metadata.get('title'):
                    metadata['title'] = line

        # 尝试提取作者
        author_patterns = [
            r'authors?[:：]\s*(.+)',
            r'by[:：]\s*(.+)',
            r'written by[:：]\s*(.+)',
        ]

        for line in lines[:20]:
            for pattern in author_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    authors_str = match.group(1)
                    # 分割作者列表
                    authors = re.split(r',|;', authors_str)
                    metadata['authors'] = [a.strip() for a in authors if a.strip()]
                    break

        # 尝试提取摘要
        abstract_start = False
        abstract_lines = []

        for line in lines:
            line_lower = line.lower().strip()
            if 'abstract' in line_lower or '摘要' in line_lower:
                abstract_start = True
                continue
            if abstract_start:
                if line.strip() and len(line) > 20:
                    abstract_lines.append(line.strip())
                elif abstract_lines and len(abstract_lines) > 0:
                    break

        if abstract_lines:
            metadata['abstract'] = ' '.join(abstract_lines[:5])

        # 尝试提取年份
        year_pattern = r'(19|20)\d{2}'
        year_matches = re.findall(year_pattern, content[:1000])
        if year_matches:
            metadata['year'] = year_matches[0]

        return metadata

    def _extract_pdf_metadata(self, file_path: Path) -> dict:
        """
        提取 PDF 元数据

        注意：需要 PyPDF2 或 pdfplumber 库
        这里提供一个基础实现
        """
        metadata = {
            "abstract": "",
            "year": "",
        }

        # 尝试使用 PyPDF2
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pdf_metadata = reader.metadata

                if pdf_metadata:
                    if pdf_metadata.title:
                        metadata['title'] = pdf_metadata.title
                    if pdf_metadata.author:
                        metadata['authors'] = [pdf_metadata.author]
                    if pdf_metadata.creation_date:
                        # 提取年份
                        year_match = re.search(r'(19|20)\d{2}', str(pdf_metadata.creation_date))
                        if year_match:
                            metadata['year'] = year_match.group()

                # 尝试读取第一页提取摘要
                if reader.pages:
                    first_page = reader.pages[0]
                    text = first_page.extract_text()
                    if text:
                        extracted = self._extract_metadata(text)
                        metadata.update(extracted)

        except ImportError:
            logger.warning("PyPDF2 未安装，无法解析 PDF 元数据")
        except Exception as e:
            logger.warning(f"解析 PDF 元数据失败：{e}")

        return metadata

    def search_by_keywords(self, directory: str, keywords: list[str]) -> list[dict]:
        """
        在目录中按关键词搜索论文

        Args:
            directory: 目录路径
            keywords: 关键词列表

        Returns:
            匹配的论文列表
        """
        papers = self.scan_directory(directory)
        matched_papers = []

        for paper in papers:
            # 检查标题、摘要是否包含关键词
            text_to_search = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()

            for keyword in keywords:
                if keyword.lower() in text_to_search:
                    matched_papers.append(paper)
                    break

        return matched_papers

    def list_all_papers(self, directories: list[str] = None) -> list[dict]:
        """
        列出所有目录中的论文

        Args:
            directories: 目录列表

        Returns:
            论文列表
        """
        dirs_to_scan = directories or self.default_dirs
        all_papers = []
        seen_paths = set()

        for directory in dirs_to_scan:
            papers = self.scan_directory(directory)
            for paper in papers:
                if paper['file_path'] not in seen_paths:
                    seen_paths.add(paper['file_path'])
                    all_papers.append(paper)

        return all_papers


# 全局实例
_searcher: Optional["LocalPaperSearcher"] = None


def get_searcher(default_dirs: list[str] = None) -> LocalPaperSearcher:
    """获取全局 LocalPaperSearcher 实例"""
    global _searcher
    if _searcher is None:
        _searcher = LocalPaperSearcher(default_dirs)
    return _searcher


def scan_local_papers(directory: str) -> list[dict]:
    """
    便捷函数：扫描本地目录的论文

    Args:
        directory: 目录路径

    Returns:
        论文列表
    """
    searcher = get_searcher()
    return searcher.scan_directory(directory)


def search_local_papers(directory: str, keywords: list[str]) -> list[dict]:
    """
    便捷函数：在本地目录搜索论文

    Args:
        directory: 目录路径
        keywords: 关键词列表

    Returns:
        匹配的论文列表
    """
    searcher = get_searcher()
    return searcher.search_by_keywords(directory, keywords)
