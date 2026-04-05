"""
测试 MCP 工具集成

测试 arXiv 和 Semantic Scholar 客户端
"""

import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from mcp.clients.arxiv_client import ArXivClient
from mcp.clients.semantic_scholar_client import SemanticScholarClient
from mcp.tools.paper_search import search_papers

def test_arxiv():
    """测试 arXiv 客户端"""
    print("\n" + "=" * 60)
    print("测试 arXiv 客户端")
    print("=" * 60)

    client = ArXivClient(max_results=5)

    # 测试搜索
    print("\n搜索：Transformer + Time Series")
    papers = client.search("Transformer Time Series forecasting", categories=["cs.LG", "cs.AI"])

    print(f"找到 {len(papers)} 篇论文\n")

    for i, paper in enumerate(papers[:3], 1):
        print(f"[{i}] {paper.get('title', 'N/A')}")
        print(f"    作者：{', '.join(paper.get('authors', [])[:3])}")
        print(f"    分类：{', '.join(paper.get('categories', []))}")
        print(f"    URL: {paper.get('url', 'N/A')}")
        print()

    return len(papers) > 0


def test_semantic_scholar():
    """测试 Semantic Scholar 客户端"""
    print("\n" + "=" * 60)
    print("测试 Semantic Scholar 客户端")
    print("=" * 60)

    client = SemanticScholarClient(max_results=5)

    # 测试搜索
    print("\n搜索：Deep Learning")
    papers = client.search("Deep Learning for NLP", year_range=(2020, 2025))

    print(f"找到 {len(papers)} 篇论文\n")

    for i, paper in enumerate(papers[:3], 1):
        print(f"[{i}] {paper.get('title', 'N/A')}")
        print(f"    作者：{', '.join(paper.get('authors', [])[:3])}")
        print(f"    年份：{paper.get('year', 'N/A')}")
        print(f"    引用：{paper.get('citation_count', 0)}")
        print(f"    URL: {paper.get('url', 'N/A')}")
        print()

    return len(papers) > 0


def test_unified_search():
    """测试统一搜索"""
    print("\n" + "=" * 60)
    print("测试统一搜索 (多数据源)")
    print("=" * 60)

    print("\n搜索：Few-shot Learning")
    papers = search_papers("Few-shot Learning", max_results=10)

    print(f"找到 {len(papers)} 篇论文\n")

    for i, paper in enumerate(papers[:5], 1):
        source = paper.get("source", "arXiv")
        print(f"[{i}] [{source}] {paper.get('title', 'N/A')}")
        print(f"    作者：{', '.join(paper.get('authors', [])[:3])}")
        print(f"    URL: {paper.get('url', 'N/A')}")
        print()

    return len(papers) > 0


def test_registry():
    """测试工具注册中心"""
    print("\n" + "=" * 60)
    print("测试工具注册中心")
    print("=" * 60)

    from mcp.tool_registry import get_registry

    registry = get_registry()
    tools = registry.list_tools()

    print(f"\n已注册工具：{len(tools)}")

    for tool in tools:
        print(f"\n  - {tool['name']}")
        print(f"    描述：{tool.get('description', 'N/A')}")

    return len(tools) > 0


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("MCP 工具集成测试")
    print("=" * 60)

    results = {
        "arxiv": False,
        "semantic_scholar": False,
        "unified_search": False,
        "registry": False,
    }

    try:
        results["arxiv"] = test_arxiv()
    except Exception as e:
        print(f"arXiv 测试失败：{e}")

    try:
        results["semantic_scholar"] = test_semantic_scholar()
    except Exception as e:
        print(f"Semantic Scholar 测试失败：{e}")

    try:
        results["unified_search"] = test_unified_search()
    except Exception as e:
        print(f"统一搜索测试失败：{e}")

    try:
        results["registry"] = test_registry()
    except Exception as e:
        print(f"注册中心测试失败：{e}")

    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")

    print(f"\n总计：{passed}/{total} 通过")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
