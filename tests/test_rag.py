"""
Day 2: RAG 检索效果评测
评估检索准确率
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.vector_store import hybrid_search, create_vector_db
from db.rag_loader import load_and_split_handbook


def evaluate_retrieval(vectordb, test_cases):
    """
    评测检索准确率
    
    Args:
        vectordb: 向量数据库实例
        test_cases: 测试用例列表
        
    Returns:
        平均召回率
    """
    scores = []
    
    for case in test_cases:
        results = hybrid_search(vectordb, case["query"], k=3)
        content = " ".join([doc.page_content for doc, _ in results])
        
        # 检查是否包含预期关键词
        hit_count = sum(1 for kw in case["expected_keywords"] if kw in content)
        score = hit_count / len(case["expected_keywords"])
        scores.append(score)
        
        print(f"{'✅' if score > 0.5 else '❌'} {case['description']}: {score:.0%}")
    
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"\n📊 平均召回率：{avg_score:.0%}")
    return avg_score


def run_rag_tests():
    """运行 RAG 系统测试"""
    print("="*60)
    print("🧪 RAG 系统检索效果测试")
    print("="*60)
    
    # 检查是否有 PDF 文件
    pdf_path = "data/新生报到手册.pdf"
    if not os.path.exists(pdf_path):
        print(f"⚠️  测试文件不存在：{pdf_path}")
        print("创建模拟数据用于测试...")
        # 创建模拟数据
        from langchain.schema import Document
        mock_chunks = [
            Document(page_content="档案转递需要通过EMS学生档案专递通道，由原高中或人才中心寄出。接收地址：XX大学档案馆。", metadata={"source": "报到手册", "page": 15}),
            Document(page_content="军训为期两周，从9月5日开始到9月18日结束。期间进行队列训练、内务整理、国防教育等。", metadata={"source": "报到手册", "page": 25}),
            Document(page_content="学费缴纳支持银行转账、支付宝、微信支付三种方式。截止日期为9月15日。", metadata={"source": "报到手册", "page": 10}),
        ]
        vectordb = create_vector_db(mock_chunks, persist_dir="./chroma_db_test")
    else:
        # 加载真实数据
        chunks = load_and_split_handbook(pdf_path)
        vectordb = create_vector_db(chunks)
    
    # 定义测试用例
    test_cases = [
        {
            "query": "档案怎么转过来？",
            "expected_keywords": ["档案", "转递"],
            "description": "档案转递相关问题"
        },
        {
            "query": "开学要军训多久？",
            "expected_keywords": ["军训", "两周"],
            "description": "军训时长问题"
        },
        {
            "query": "学费怎么交？",
            "expected_keywords": ["学费", "缴纳"],
            "description": "缴费方式问题"
        }
    ]
    
    # 运行评测
    avg_score = evaluate_retrieval(vectordb, test_cases)
    
    print("\n" + "="*60)
    if avg_score >= 0.8:
        print("✅ 测试通过！检索效果良好")
    elif avg_score >= 0.5:
        print("⚠️  测试通过，但检索效果有待提升")
    else:
        print("❌ 测试未通过，需要优化检索策略")
    print("="*60)
    
    return avg_score


if __name__ == "__main__":
    run_rag_tests()
