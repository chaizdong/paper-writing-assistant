"""
mcp/clients 包

MCP 客户端封装
"""

from .arxiv_client import (
    ArXivClient,
    get_client as get_arxiv_client,
    search_papers as search_arxiv_papers,
)
from .semantic_scholar_client import (
    SemanticScholarClient,
    get_client as get_semantic_scholar_client,
    search_papers as search_semantic_scholar_papers,
)

__all__ = [
    "ArXivClient",
    "SemanticScholarClient",
    "get_arxiv_client",
    "get_semantic_scholar_client",
    "search_arxiv_papers",
    "search_semantic_scholar_papers",
]
