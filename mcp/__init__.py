"""
mcp 包

MCP 工具集成
"""

from .tool_registry import (
    MCPServer,
    ToolRegistry,
    ToolResult,
    get_registry,
    reset_registry,
)

from .clients import (
    ArXivClient,
    SemanticScholarClient,
    get_arxiv_client,
    get_semantic_scholar_client,
    search_arxiv_papers,
    search_semantic_scholar_papers,
)

from .tools.paper_search import (
    PaperSearchService,
    get_service,
    search_papers,
)

__all__ = [
    # Registry
    "MCPServer",
    "ToolRegistry",
    "ToolResult",
    "get_registry",
    "reset_registry",
    # Clients
    "ArXivClient",
    "SemanticScholarClient",
    "get_arxiv_client",
    "get_semantic_scholar_client",
    "search_arxiv_papers",
    "search_semantic_scholar_papers",
    # Services
    "PaperSearchService",
    "get_service",
    "search_papers",
]
