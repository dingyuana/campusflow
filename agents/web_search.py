"""
Day 8: 网络搜索模块
集成 DuckDuckGo 搜索
"""

from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


class WebSearchTool:
    """网络搜索工具"""

    def __init__(self, max_results: int = 5):
        """
        初始化网络搜索工具

        Args:
            max_results: 最多返回的搜索结果数量
        """
        self.max_results = max_results
        self.search_client = DDGS()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        执行网络搜索

        Args:
            query: 搜索查询

        Returns:
            搜索结果列表
        """
        print(f"\n🌐 执行网络搜索: {query}")
        print("-" * 60)

        results = []

        try:
            # 执行搜索
            search_results = self.search_client.text(
                query,
                max_results=self.max_results
            )

            # 处理结果
            for i, result in enumerate(search_results, 1):
                title = result.get("title", "")
                url = result.get("href", "")
                body = result.get("body", "")

                results.append({
                    "rank": i,
                    "title": title,
                    "url": url,
                    "body": body[:200] if body else "",  # 截取前200字符
                    "source": url
                })

                print(f"  {i}. {title}")
                print(f"     {url}")
                print(f"     摘要: {body[:100]}...")
                print()

            print(f"✅ 搜索完成，找到 {len(results)} 个结果")

        except Exception as e:
            print(f"❌ 搜索失败: {e}")

        return results

    def get_detailed_content(self, url: str) -> str:
        """
        获取网页详细内容（简化实现）

        Args:
            url: 网页 URL

        Returns:
            网页内容
        """
        # 这里应该使用 requests 或类似库获取网页内容
        # 简化实现：返回 URL
        return f"网页内容: {url}"


# LangChain 工具包装
@tool
def search_web(query: str) -> str:
    """
    搜索网络（LangChain 工具函数）

    Args:
        query: 搜索查询

    Returns:
        搜索结果摘要
    """
    search_tool = WebSearchTool()
    results = search_tool.search(query)

    if not results:
        return "未找到相关结果"

    # 格式化结果
    summary = f"找到 {len(results)} 个相关结果:\n\n"
    for result in results:
        summary += f"{result['rank']}. {result['title']}\n"
        summary += f"   {result['url']}\n"
        summary += f"   {result['body']}\n\n"

    return summary


def test_web_search():
    """测试网络搜索功能"""
    print("=" * 60)
    print("🧪 测试网络搜索功能")
    print("=" * 60)
    print()

    # 创建搜索工具
    search_tool = WebSearchTool()

    # 测试查询
    test_queries = [
        "2025年高考政策",
        "Python 最新版本",
        "人工智能发展趋势"
    ]

    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"📝 查询: {query}")
        print(f"{'=' * 60}")
        print()

        # 执行搜索
        results = search_tool.search(query)

        # 显示结果
        if results:
            print("📋 搜索结果:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     来源: {result['url']}")
                print(f"     摘要: {result['body'][:80]}...")
                print()
        else:
            print("❌ 未找到结果")

    print()
    print("=" * 60)
    print("✅ 网络搜索测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_web_search()
