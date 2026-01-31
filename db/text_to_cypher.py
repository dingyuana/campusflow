"""
Text-to-Cypher 自然语言查询模块
Day 3: 知识图谱智能查询

功能：
1. 将自然语言转换为 Cypher 查询语句
2. 安全防护（禁止危险操作）
3. 错误重试机制
4. 结果格式化

教学计划 Day 3 要求：
- Text-to-Cypher 安全实现（Cypher 注入防护）
- 语句校验（禁止 DELETE/DROP）
- 错误重试（3 次容错）
- 跨库关联（Chroma + Neo4j）
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

from db.neo4j_utils import Neo4jUtils

load_dotenv()


# 危险操作模式（用于安全过滤）
DANGEROUS_PATTERNS = [
    r'\bDELETE\b',
    r'\bDETACH\s+DELETE\b',
    r'\bDROP\b',
    r'\bREMOVE\b',
    r'\bSET\b.*=.*NULL',  # 设置为空
    r'\bCALL\b.*\bapoc\.\b',  # APOC 过程调用
    r'\bLOAD\s+CSV\b',  # 加载外部 CSV
    r'\bCREATE\s+USER\b',  # 创建用户
    r'\bALTER\b',  # 修改结构
    r';.*DROP',  # 多条语句包含 DROP
    r';.*DELETE',  # 多条语句包含 DELETE
]

# 允许的只读操作模式
SAFE_READ_PATTERNS = [
    r'\bMATCH\b',
    r'\bRETURN\b',
    r'\bWHERE\b',
    r'\bWITH\b',
    r'\bORDER\s+BY\b',
    r'\bLIMIT\b',
    r'\bSKIP\b',
    r'\bUNION\b',
    r'\bCOUNT\b',
    r'\bCOLLECT\b',
    r'\bDISTINCT\b',
]


class TextToCypherConverter:
    """
    Text-to-Cypher 转换器
    
    功能：
    - 自然语言 → Cypher 查询
    - 安全验证
    - 错误重试
    - 结果格式化
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_retries: int = 3
    ):
        """
        初始化转换器
        
        Args:
            model_name: LLM 模型名称
            temperature: 生成温度（建议 0.0 以保证确定性）
            max_retries: 最大重试次数
        """
        self.max_retries = max_retries
        
        # 初始化 LLM
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        
        if not api_key:
            raise ValueError("❌ 环境变量 OPENAI_API_KEY 未设置")
        
        llm_kwargs = {
            "model": model_name,
            "temperature": temperature,
            "api_key": api_key,
        }
        
        if base_url:
            llm_kwargs["base_url"] = base_url
        
        self.llm = ChatOpenAI(**llm_kwargs)
        self.parser = StrOutputParser()
        
        # 系统提示词
        self.system_prompt = """你是一个 Neo4j Cypher 查询生成专家。

任务：将用户的中文自然语言查询转换为正确的 Cypher 查询语句。

## 知识图谱 Schema

### 节点类型
- Student: 学生 {student_id, name, department}
- Teacher: 教师 {teacher_id, name, department}
- Department: 院系 {code, name}
- Course: 课程 {course_id, name, credit}

### 关系类型
- (Student)-[:BELONGS_TO]->(Department): 学生属于院系
- (Teacher)-[:WORKS_AT]->(Department): 教师在院系工作
- (Student)-[:ENROLLED_IN]->(Course): 学生选修课程
- (Teacher)-[:TEACHES]->(Course): 教师教授课程

## 生成规则

1. **只生成只读查询**：只能使用 MATCH、RETURN、WHERE、WITH、ORDER BY、LIMIT、COUNT、COLLECT 等
2. **禁止危险操作**：绝对不能生成 DELETE、DROP、REMOVE、SET、CREATE、MERGE 等修改操作
3. **参数化查询**：使用 $ 符号表示参数，如 $student_id
4. **返回格式**：只返回 Cypher 查询字符串，不要任何解释
5. **友好性**：如果查询无法生成，返回 "抱歉，我无法回答这个问题"

## 示例

用户：计算机学院有哪些学生？
Cypher: MATCH (s:Student)-[:BELONGS_TO]->(d:Department {code: "CS"}) RETURN s.name, s.student_id

用户：张三选了哪些课？
Cypher: MATCH (s:Student {name: "张三"})-[:ENROLLED_IN]->(c:Course) RETURN c.name, c.course_id, c.credit

用户：数据结构这门课的老师是谁？
Cypher: MATCH (t:Teacher)-[:TEACHES]->(c:Course {name: "数据结构"}) RETURN t.name, t.teacher_id

用户：和张三选修相同课程的同学有哪些？
Cypher: MATCH (s1:Student {name: "张三"})-[:ENROLLED_IN]->(c:Course)<-[:ENROLLED_IN]-(s2:Student) WHERE s1 <> s2 RETURN DISTINCT s2.name, s2.student_id

记住：只返回 Cypher 查询语句，不要任何其他文字！"""

    def validate_cypher(self, cypher: str) -> Tuple[bool, str]:
        """
        验证 Cypher 语句安全性
        
        检查：
        1. 是否包含危险操作（DELETE、DROP 等）
        2. 是否包含多条语句（分号分隔）
        3. 是否是合法的只读查询
        
        Args:
            cypher: Cypher 查询语句
            
        Returns:
            (是否安全, 错误信息)
        """
        cypher_upper = cypher.upper().strip()
        
        # 1. 检查危险模式
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, cypher_upper, re.IGNORECASE):
                return False, f"⚠️ 检测到危险操作模式: {pattern}"
        
        # 2. 检查多条语句（简单的分号检查）
        if cypher.count(';') > 0:
            # 检查每条语句
            statements = [s.strip() for s in cypher.split(';') if s.strip()]
            for stmt in statements:
                for pattern in DANGEROUS_PATTERNS:
                    if re.search(pattern, stmt, re.IGNORECASE):
                        return False, f"⚠️ 多条语句中包含危险操作"
        
        # 3. 检查是否至少有一个安全操作
        has_safe = any(
            re.search(pattern, cypher_upper)
            for pattern in SAFE_READ_PATTERNS
        )
        
        if not has_safe:
            return False, "⚠️ 未检测到合法的只读操作"
        
        return True, "✅ Cypher 语句安全"
    
    def convert(self, natural_query: str) -> Tuple[str, bool]:
        """
        将自然语言转换为 Cypher 查询
        
        Args:
            natural_query: 自然语言查询
            
        Returns:
            (Cypher 查询, 是否成功)
        """
        print(f"📝 转换查询: '{natural_query}'")
        
        for attempt in range(self.max_retries):
            try:
                # 调用 LLM 生成 Cypher
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=natural_query)
                ]
                
                response = self.llm.invoke(messages)
                cypher = self.parser.invoke(response).strip()
                
                print(f"   生成 Cypher (尝试 {attempt + 1}/{self.max_retries}): {cypher[:100]}...")
                
                # 安全验证
                is_safe, message = self.validate_cypher(cypher)
                
                if is_safe:
                    print(f"   ✅ 验证通过")
                    return cypher, True
                else:
                    print(f"   ❌ 验证失败: {message}")
                    
                    # 如果不是最后一次尝试，继续重试
                    if attempt < self.max_retries - 1:
                        print(f"   🔄 准备重试...")
                        continue
                    else:
                        return f"抱歉，无法生成安全的查询: {message}", False
                
            except Exception as e:
                print(f"   ❌ 生成失败: {e}")
                if attempt < self.max_retries - 1:
                    print(f"   🔄 准备重试...")
                    continue
                else:
                    return f"抱歉，查询生成失败: {e}", False
        
        return "抱歉，多次尝试后仍无法生成查询", False


class Neo4jQueryAgent:
    """
    Neo4j 查询智能体
    
    整合 Text-to-Cypher 和 Neo4j 查询执行
    """
    
    def __init__(self):
        """初始化查询智能体"""
        self.converter = TextToCypherConverter()
        self.neo4j = Neo4jUtils()
        
        # 连接到 Neo4j
        if not self.neo4j.connect():
            raise ConnectionError("❌ 无法连接到 Neo4j 数据库")
    
    def query(self, natural_query: str) -> Dict[str, Any]:
        """
        执行自然语言查询
        
        Args:
            natural_query: 自然语言查询
            
        Returns:
            查询结果字典
        """
        result = {
            "query": natural_query,
            "cypher": None,
            "success": False,
            "data": None,
            "error": None
        }
        
        try:
            # 1. 转换为 Cypher
            cypher, success = self.converter.convert(natural_query)
            result["cypher"] = cypher
            
            if not success:
                result["error"] = cypher
                return result
            
            # 2. 执行 Cypher 查询
            print(f"🔍 执行 Cypher 查询...")
            
            with self.neo4j.driver.session() as session:
                query_result = session.run(cypher)
                data = [record.data() for record in query_result]
                
                result["success"] = True
                result["data"] = data
                
                print(f"   ✅ 查询成功，返回 {len(data)} 条数据")
        
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ 查询执行失败: {e}")
        
        return result
    
    def close(self):
        """关闭连接"""
        self.neo4j.close()


def test_text_to_cypher():
    """
    测试 Text-to-Cypher 功能
    """
    print("=" * 70)
    print("🧪 Text-to-Cypher 功能测试")
    print("=" * 70)
    print()
    
    # 创建转换器
    try:
        converter = TextToCypherConverter()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 测试用例
    test_cases = [
        "计算机学院有哪些学生？",
        "张三选了哪些课程？",
        "Python程序设计这门课的老师是谁？",
        "和张三选修相同课程的同学有哪些？",
        "计算机学院开设了哪些课程？",
    ]
    
    # 攻击测试用例（应该被拒绝）
    attack_cases = [
        "DELETE all students",
        "DROP all nodes",
        "MATCH (n) DELETE n",
        "CREATE (n:Test {name: 'hack'})",
    ]
    
    print("【正常查询测试】")
    print("-" * 70)
    
    for query in test_cases:
        print(f"\n📝 查询: {query}")
        cypher, success = converter.convert(query)
        
        if success:
            print(f"   ✅ 生成 Cypher: {cypher}")
        else:
            print(f"   ❌ 失败: {cypher}")
    
    print()
    print("【安全防护测试】")
    print("-" * 70)
    
    for attack in attack_cases:
        print(f"\n⚠️  攻击测试: {attack}")
        is_safe, message = converter.validate_cypher(attack)
        
        if is_safe:
            print(f"   ❌ 危险！未能拦截: {attack}")
        else:
            print(f"   ✅ 成功拦截: {message}")
    
    print()
    print("=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)


def test_neo4j_agent():
    """
    测试 Neo4j 查询智能体（端到端测试）
    """
    print("\n")
    print("=" * 70)
    print("🧪 Neo4j 查询智能体测试（端到端）")
    print("=" * 70)
    print()
    
    try:
        agent = Neo4jQueryAgent()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("   请确保 Neo4j 数据库已启动并配置正确")
        return
    
    test_queries = [
        "计算机学院有哪些学生？",
        "张三选了哪些课程？",
    ]
    
    for query in test_queries:
        print("=" * 70)
        print(f"📝 自然语言查询: {query}")
        print("-" * 70)
        
        result = agent.query(query)
        
        print(f"\n🗣️  生成的 Cypher:")
        print(f"   {result['cypher']}")
        
        if result['success']:
            print(f"\n📊 查询结果 ({len(result['data'])} 条):")
            for i, record in enumerate(result['data'], 1):
                print(f"   {i}. {record}")
        else:
            print(f"\n❌ 错误: {result['error']}")
        
        print()
    
    agent.close()
    
    print("=" * 70)
    print("✅ 端到端测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    # 运行 Text-to-Cypher 测试（不需要 Neo4j 连接）
    test_text_to_cypher()
    
    # 运行端到端测试（需要 Neo4j 连接）
    # 如果 Neo4j 未配置，可以注释掉下面这行
    # test_neo4j_agent()
