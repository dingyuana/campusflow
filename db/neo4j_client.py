"""
Day 3: 安全的 Neo4j 查询客户端
Text-to-Cypher 与注入防护
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import re
import os


class SecureGraphClient:
    """安全的图数据库客户端"""
    
    def __init__(self, neo4j_driver):
        """
        初始化安全客户端
        
        Args:
            neo4j_driver: Neo4j 驱动实例
        """
        self.driver = neo4j_driver
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 危险操作黑名单
        self.dangerous_keywords = [
            r'\bdrop\b', r'\bdelete\b', r'\bremove\b', 
            r'\bset\b', r'\bcreate\b', r'\bmerge\b',
            r'\bdetach\b', r'\bforeach\b', r'\bload\b',
            r';.*drop', r';.*delete'  # 防止多语句注入
        ]
    
    def is_safe_query(self, cypher: str) -> bool:
        """
        验证 Cypher 查询安全性
        
        Args:
            cypher: Cypher 查询语句
            
        Returns:
            是否安全
        """
        lower_cypher = cypher.lower()
        for pattern in self.dangerous_keywords:
            if re.search(pattern, lower_cypher):
                return False
        
        # 只允许以 MATCH 开头（只读）
        if not lower_cypher.strip().startswith('match'):
            return False
            
        return True
    
    def text_to_cypher(self, question: str) -> str:
        """
        将自然语言转为 Cypher（带安全防护）
        
        Args:
            question: 自然语言问题
            
        Returns:
            Cypher 查询语句
        """
        
        schema_desc = """
        节点类型：
        - Student: id, name, major, grade
        - Teacher: id, name, field, title
        - Lab: id, name, building
        - Dormitory: id, building, room, type
        - Course: id, name, credits
        
        关系类型：
        - (Teacher)-[:SUPERVISES]->(Student): 导师指导
        - (Teacher|Student)-[:BELONGS_TO]->(Lab): 所属实验室
        - (Student)-[:LIVES_IN]->(Dormitory): 住宿
        - (Student)-[:ENROLLED_IN]->(Course): 选课
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是一个 Neo4j Cypher 查询生成助手。
严格遵循以下规则：
1. 只生成 MATCH 查询语句（只读），禁止生成 CREATE/DELETE/DROP/SET/REMOVE/MERGE
2. 使用参数化查询（$parameter）防止注入
3. 查询必须基于以下 Schema：{schema_desc}
4. 如果问题涉及修改数据，拒绝生成并返回：UNSAFE_QUERY
5. 只返回 Cypher 代码，不要解释"""),
            ("human", "问题：{question}\n生成 Cypher 查询：")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"question": question})
        cypher = response.content.strip()
        
        # 清理代码块标记
        cypher = re.sub(r'```cypher|```', '', cypher).strip()
        
        return cypher
    
    def query(self, question: str):
        """
        安全的自然语言查询接口
        
        Args:
            question: 用户问题
            
        Returns:
            查询结果字典
        """
        try:
            # 1. 生成 Cypher
            cypher = self.text_to_cypher(question)
            print(f"🤖 生成的 Cypher：{cypher}")
            
            # 2. 安全检查
            if cypher == "UNSAFE_QUERY" or not self.is_safe_query(cypher):
                return {"error": "查询包含危险操作，已拦截", "cypher": cypher}
            
            # 3. 执行查询（只读模式）
            with self.driver.session() as session:
                result = session.run(cypher)
                records = [dict(record) for record in result]
                return {
                    "cypher": cypher,
                    "results": records,
                    "count": len(records)
                }
                
        except Exception as e:
            return {"error": str(e), "cypher": cypher if 'cypher' in locals() else None}
    
    def get_student_network(self, student_name: str):
        """
        特定查询：获取学生的关系网络（导师、室友、同实验室同学）
        
        Args:
            student_name: 学生姓名
            
        Returns:
            关系网络信息
        """
        query = """
        MATCH (s:Student {name: $name})-[:SUPERVISES*0..1]-(t:Teacher)
        OPTIONAL MATCH (s)-[:LIVES_IN]->(d:Dormitory)<-[:LIVES_IN]-(roommate:Student)
        OPTIONAL MATCH (s)-[:BELONGS_TO]->(l:Lab)<-[:BELONGS_TO]-(colleague:Student)
        RETURN s.name as student, 
               t.name as supervisor, 
               collect(DISTINCT roommate.name) as roommates,
               collect(DISTINCT colleague.name) as lab_colleagues,
               l.name as lab
        """
        with self.driver.session() as session:
            result = session.run(query, name=student_name)
            return [dict(record) for record in result]
