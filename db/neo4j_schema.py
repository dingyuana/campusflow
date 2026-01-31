"""
Day 3: Neo4j 知识图谱 Schema 与数据导入
校园领域本体设计
"""

from neo4j import GraphDatabase
import os


class CampusGraph:
    """校园知识图谱管理类"""
    
    def __init__(self):
        """初始化图数据库连接"""
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """关闭连接"""
        self.driver.close()
    
    def init_schema(self):
        """初始化校园知识图谱 Schema 与模拟数据"""
        with self.driver.session() as session:
            # 清理现有数据（仅开发环境使用）
            session.run("MATCH (n) DETACH DELETE n")
            
            # 创建约束
            session.run("CREATE CONSTRAINT student_id IF NOT EXISTS FOR (s:Student) REQUIRE s.id IS UNIQUE")
            session.run("CREATE CONSTRAINT teacher_id IF NOT EXISTS FOR (t:Teacher) REQUIRE t.id IS UNIQUE")
            
            # 创建节点和关系（模拟数据）
            cypher_query = """
            // 创建教师
            CREATE (t1:Teacher {id: 'T001', name: '张教授', field: '人工智能', title: '教授'})
            CREATE (t2:Teacher {id: 'T002', name: '王副教授', field: '软件工程', title: '副教授'})
            
            // 创建实验室
            CREATE (l1:Lab {id: 'L001', name: '智能系统实验室', building: '科技楼'})
            CREATE (l2:Lab {id: 'L002', name: '软件工程实验室', building: '信息楼'})
            
            // 创建学生
            CREATE (s1:Student {id: '2024001', name: '李明', major: '计算机科学', grade: '2024'})
            CREATE (s2:Student {id: '2024002', name: '王芳', major: '软件工程', grade: '2024'})
            CREATE (s3:Student {id: '2024003', name: '张伟', major: '计算机科学', grade: '2024'})
            
            // 创建宿舍
            CREATE (d1:Dormitory {id: 'A1-301', building: 'A1', room: '301', type: '四人间'})
            CREATE (d2:Dormitory {id: 'A2-205', building: 'A2', room: '205', type: '六人间'})
            
            // 创建课程
            CREATE (c1:Course {id: 'C001', name: 'Python编程', credits: 3})
            CREATE (c2:Course {id: 'C002', name: '数据结构', credits: 4})
            
            // 建立关系
            CREATE (t1)-[:SUPERVISES]->(s1)
            CREATE (t1)-[:SUPERVISES]->(s3)
            CREATE (t2)-[:SUPERVISES]->(s2)
            
            CREATE (t1)-[:BELONGS_TO]->(l1)
            CREATE (t2)-[:BELONGS_TO]->(l2)
            CREATE (s1)-[:BELONGS_TO]->(l1)
            CREATE (s3)-[:BELONGS_TO]->(l1)
            
            CREATE (s1)-[:LIVES_IN]->(d1)
            CREATE (s2)-[:LIVES_IN]->(d2)
            CREATE (s3)-[:LIVES_IN]->(d1)
            
            CREATE (s1)-[:ENROLLED_IN {semester: '2024-1'}]->(c1)
            CREATE (s2)-[:ENROLLED_IN {semester: '2024-1'}]->(c1)
            CREATE (s3)-[:ENROLLED_IN {semester: '2024-1'}]->(c2)
            """
            session.run(cypher_query)
            print("✅ 知识图谱初始化完成")
    
    def test_connection(self):
        """测试数据库连接"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as num")
                record = result.single()
                return record["num"] == 1
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            return False


if __name__ == "__main__":
    graph = CampusGraph()
    
    # 测试连接
    if graph.test_connection():
        print("✅ Neo4j 连接成功")
        # 初始化数据
        graph.init_schema()
    else:
        print("❌ 无法连接到 Neo4j，请检查：")
        print("   1. Neo4j 数据库是否已启动")
        print("   2. 环境变量 NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD 是否设置正确")
    
    graph.close()
