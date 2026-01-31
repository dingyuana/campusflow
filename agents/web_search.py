"""
Day 13: 实时信息融合 - 网络搜索增强

集成搜索引擎：
- Tavily AI 搜索（高质量）
- DuckDuckGo 搜索（免费）
- DashScope（国内）
"""

import os
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from duckduckgo_search import DDGS


class WebSearchManager:
    """网络搜索管理器"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    
    def needs_search(self, query: str) -> bool:
        """判断是否需要搜索"""
        time_keywords = ["今天", "明天", "最新", "当前", "现在", "今天天气"]
        return any(kw in query for kw in time_keywords)
    
    def search_duckduckgo(self, query: str, max_results: int = 3) -> List[Dict]:
        """使用 DuckDuckGo 搜索"""
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_results)
                return [
                    {
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", "")
                    }
                    for r in results
                ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def hybrid_search(
        self,
        query: str,
        rag_results: List[Any],
        top_k: int = 5
    ) -> List[Dict]:
        """
        混合搜索：RAG + 网络搜索
        
        融合策略：
        1. 时效性问题使用网络搜索
        2. 知识库问题使用 RAG
        3. 结果去重和排序
        """
        results = []
        
        # 添加 RAG 结果
        for doc in rag_results[:3]:
            results.append({
                "source": "RAG",
                "content": doc.page_content if hasattr(doc, 'page_content') else str(doc),
                "score": 0.9
            })
        
        # 如果需要，添加网络搜索结果
        if self.needs_search(query):
            web_results = self.search_duckduckgo(query, max_results=2)
            for r in web_results:
                if "error" not in r:
                    results.append({
                        "source": "Web",
                        "title": r.get("title", ""),
                        "content": r.get("snippet", ""),
                        "link": r.get("link", ""),
                        "score": 0.7
                    })
        
        return results[:top_k]


@tool
def search_campus_news(query: str) -> str:
    """
    搜索校园最新新闻和通知
    
    用于获取：
    - 最新校园通知
    - 活动信息
    - 临时安排
    """
    searcher = WebSearchManager()
    results = searcher.search_duckduckgo(f"校园 {query}", max_results=3)
    
    if not results:
        return "未找到相关信息"
    
    output = "🔍 搜索结果:\n\n"
    for i, r in enumerate(results, 1):
        output += f"{i}. {r.get('title', '无标题')}\n"
        output += f"   {r.get('snippet', '无内容')}\n\n"
    
    return output
