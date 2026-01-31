"""
Day 3: 知识图谱查询工具
封装为 LangChain Tool 供 Agent 使用
"""

from langchain.tools import tool
from db.neo4j_client import SecureGraphClient
from db.neo4j_schema import CampusGraph


# 初始化
graph = CampusGraph()
kg_client = SecureGraphClient(graph.driver)


@tool
def query_campus_kg(question: str) -> str:
    """
    查询校园知识图谱，获取学生、教师、实验室等关系信息。
    适用于：导师查询、实验室成员、宿舍分配、课程选修等关系型问题。
    
    Args:
        question: 自然语言问题，如"张教授的学生有哪些？"
        
    Returns:
        查询结果文本
    """
    result = kg_client.query(question)
    
    if "error" in result:
        return f"查询失败：{result['error']}"
    
    if result["count"] == 0:
        return "未找到相关信息。"
    
    # 格式化结果
    formatted = f"查询语句：{result['cypher']}\n\n查询结果（共{result['count']}条）：\n"
    for i, record in enumerate(result["results"][:5], 1):  # 最多显示5条
        formatted += f"{i}. {record}\n"
    
    return formatted


@tool
def get_student_social_network(student_name: str) -> str:
    """
    获取学生的社交关系网络（导师、室友、同实验室同学）
    
    Args:
        student_name: 学生姓名，如"李明"
        
    Returns:
        关系网络信息
    """
    results = kg_client.get_student_network(student_name)
    
    if not results:
        return f"未找到学生 {student_name} 的信息"
    
    info = results[0]
    return f"""
学生：{info['student']}
导师：{info['supervisor']}
所在实验室：{info['lab']}
室友：{', '.join(info['roommates']) if info['roommates'] else '无'}
实验室同学：{', '.join(info['lab_colleagues']) if info['lab_colleagues'] else '无'}
"""


if __name__ == "__main__":
    # 测试
    print("🧪 测试知识图谱工具")
    
    # 测试 1
    result1 = query_campus_kg("张教授的学生有哪些？")
    print(f"\n测试 1 - 导师查询:\n{result1}")
    
    # 测试 2
    result2 = get_student_social_network("李明")
    print(f"\n测试 2 - 学生关系网络:\n{result2}")
