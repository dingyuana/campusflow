# Neo4j 图数据库与知识图谱

## 📋 概述

Neo4j 是全球领先的图数据库（Graph Database），采用原生图存储和处理引擎，专门用于存储和查询高度连接的数据。在智慧校园系统中，Neo4j 用于构建知识图谱，实现复杂关系的存储和查询。

### 为什么选择 Neo4j？

| 特性 | 说明 |
|------|------|
| **原生图存储** | 数据以节点和关系形式存储，无需表连接 |
| **高性能查询** | 深度关联查询性能远超关系型数据库 |
| **灵活模式** | 无需预定义严格 Schema，支持动态添加属性 |
| **Cypher 查询语言** | 直观的图查询语法，类似 ASCII 艺术 |
| **可视化界面** | 内置 Browser 工具，可视化图结构 |

---

## 🏗️ 核心概念

### 1. 图数据模型

```
节点（Node）          关系（Relationship）        属性（Property）
     ┌───┐                ┌───┐                        
     │张三│ ──同学──→      │李四│  姓名: "张三"          
     └───┘                └───┘  年龄: 20             
       │                      │    专业: "CS"          
       │ 选修                 │                        
       ▼                      │                        
     ┌──────────┐            │                        
     │ 数据结构  │←───────────┘                        
     └──────────┘                                     
       课程名称: "数据结构"                             
       学分: 3                                        
```

### 2. 核心元素

```cypher
// 节点（Node）
(:Student {name: "张三", id: "2024001"})
//  ↑标签      ↑属性（键值对）

// 关系（Relationship）
-[:CLASSMATE {since: "2024-09-01"}]->
//  ↑类型           ↑关系属性

// 路径（Path）
(张三)-[:CLASSMATE]->(李四)-[:SELECTED]->(数据结构)
```

---

## 🚀 快速开始

### 1. 安装 Neo4j

#### Docker 安装（推荐）

```bash
# 拉取镜像
docker pull neo4j:latest

# 运行容器
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/logs:/logs \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest

# 访问地址
# Browser: http://localhost:7474
# Bolt: bolt://localhost:7687
```

#### 直接安装

```bash
# Ubuntu/Debian
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 5' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j

# 启动服务
sudo systemctl start neo4j
```

### 2. Python 驱动安装

```bash
# 安装 Python 驱动
pip install neo4j

# 国内镜像
pip install neo4j --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 第一个 Neo4j 程序

```python
from neo4j import GraphDatabase

# 连接配置
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

class Neo4jService:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def create_person(self, name, age):
        """创建人员节点"""
        with self.driver.session() as session:
            result = session.run("""
                CREATE (p:Person {name: $name, age: $age})
                RETURN p
            """, name=name, age=age)
            return result.single()[0]
    
    def create_friendship(self, name1, name2):
        """创建朋友关系"""
        with self.driver.session() as session:
            session.run("""
                MATCH (p1:Person {name: $name1})
                MATCH (p2:Person {name: $name2})
                CREATE (p1)-[:FRIEND]->(p2)
            """, name1=name1, name2=name2)
    
    def find_friends(self, name):
        """查找某人的朋友"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Person {name: $name})-[:FRIEND]->(friend)
                RETURN friend.name AS name, friend.age AS age
            """, name=name)
            return [record.data() for record in result]

# 使用示例
if __name__ == "__main__":
    service = Neo4jService(URI, AUTH)
    
    # 创建节点
    service.create_person("张三", 20)
    service.create_person("李四", 21)
    service.create_person("王五", 19)
    
    # 创建关系
    service.create_friendship("张三", "李四")
    service.create_friendship("张三", "王五")
    
    # 查询朋友
    friends = service.find_friends("张三")
    print(f"张三的朋友: {friends}")
    
    service.close()
```

---

## 💾 Cypher 查询语言

### 1. 创建（CREATE）

```cypher
// 创建单个节点
CREATE (s:Student {name: "张三", id: "2024001", major: "CS"})

// 创建多个节点
CREATE 
  (s1:Student {name: "李四", id: "2024002"}),
  (s2:Student {name: "王五", id: "2024003"})

// 创建节点和关系
CREATE 
  (s1:Student {name: "张三"})-[:CLASSMATE {since: "2024-09-01"}]->
  (s2:Student {name: "李四"})

// 创建完整路径
CREATE 
  (s:Student {name: "张三"})-[:SELECTED {grade: 90}]->
  (c:Course {name: "数据结构", credit: 3})<-[:TEACHES]-
  (t:Teacher {name: "李老师"})
```

### 2. 查询（MATCH）

```cypher
// 查询所有学生
MATCH (s:Student)
RETURN s.name, s.id, s.major

// 条件查询
MATCH (s:Student {major: "CS"})
WHERE s.age > 18
RETURN s.name, s.age
ORDER BY s.age DESC
LIMIT 10

// 查询关系
MATCH (s:Student)-[:CLASSMATE]->(friend)
WHERE s.name = "张三"
RETURN friend.name, friend.major

// 多跳查询（朋友的朋友）
MATCH (s:Student)-[:CLASSMATE]->()-[:CLASSMATE]->(friend_of_friend)
WHERE s.name = "张三"
RETURN DISTINCT friend_of_friend.name

// 查询路径
MATCH path = (s1:Student)-[:CLASSMATE*1..3]->(s2:Student)
WHERE s1.name = "张三" AND s2.name = "王五"
RETURN path, length(path) AS hops

// 聚合查询
MATCH (s:Student)-[:SELECTED]->(c:Course)
RETURN c.name, count(s) AS student_count, avg(s.grade) AS avg_grade
```

### 3. 更新（SET/REMOVE）

```cypher
// 更新属性
MATCH (s:Student {name: "张三"})
SET s.age = 21, s.email = "zhangsan@example.com"
RETURN s

// 添加标签
MATCH (s:Student {name: "张三"})
SET s:Monitor
RETURN s

// 删除属性
MATCH (s:Student {name: "张三"})
REMOVE s.email
RETURN s

// 删除标签
MATCH (s:Student:Monitor {name: "张三"})
REMOVE s:Monitor
RETURN s
```

### 4. 删除（DELETE/DETACH DELETE）

```cypher
// 删除关系
MATCH (:Student {name: "张三"})-[r:CLASSMATE]->()
DELETE r

// 删除节点（必须先删除关系）
MATCH (s:Student {name: "张三"})
DETACH DELETE s

// 删除所有节点和关系（慎用！）
MATCH (n)
DETACH DELETE n
```

### 5. 合并（MERGE）

```cypher
// 存在则返回，不存在则创建
MERGE (s:Student {id: "2024001"})
ON CREATE SET s.name = "张三", s.created = datetime()
ON MATCH SET s.last_seen = datetime()
RETURN s

// 合并关系
MATCH (s1:Student {name: "张三"}), (s2:Student {name: "李四"})
MERGE (s1)-[r:CLASSMATE]->(s2)
ON CREATE SET r.since = "2024-09-01"
RETURN r
```

---

## 🎯 校园知识图谱实战

### 1. 数据模型设计

```
节点类型：
- Student (学生): name, id, major, grade, gender
- Teacher (教师): name, id, department, title
- Course (课程): name, code, credit, category
- Class (班级): name, code, grade
- Major (专业): name, code, department
- Department (院系): name, code

关系类型：
- BELONGS_TO (学生→班级)
- CLASSMATE (学生↔学生)
- SELECTED (学生→课程) grade, semester
- TEACHES (教师→课程)
- BELONGS_TO (教师→院系)
- HAS_COURSE (专业→课程)
- BELONGS_TO (课程→院系)
- ADVISOR (教师→学生)
```

### 2. 创建完整知识图谱

```python
"""
CampusFlow Neo4j 知识图谱
构建校园完整的关系网络
"""

from neo4j import GraphDatabase
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class CampusKnowledgeGraph:
    """校园知识图谱服务"""
    
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """关闭连接"""
        self.driver.close()
    
    def clear_database(self):
        """清空数据库（慎用）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ 数据库已清空")
    
    def create_indexes(self):
        """创建索引以提高查询性能"""
        with self.driver.session() as session:
            # 为学生 ID 创建唯一约束
            session.run("""
                CREATE CONSTRAINT student_id IF NOT EXISTS
                FOR (s:Student) REQUIRE s.id IS UNIQUE
            """)
            
            # 为课程代码创建唯一约束
            session.run("""
                CREATE CONSTRAINT course_code IF NOT EXISTS
                FOR (c:Course) REQUIRE c.code IS UNIQUE
            """)
            
            # 创建索引
            session.run("""
                CREATE INDEX student_name IF NOT EXISTS
                FOR (s:Student) ON (s.name)
            """)
            
            print("✅ 索引创建完成")
    
    def create_student(self, student_data: Dict):
        """
        创建学生节点
        
        Args:
            student_data: {
                "id": "2024001",
                "name": "张三",
                "gender": "男",
                "major": "计算机科学",
                "grade": 2024,
                "class_name": "CS2401"
            }
        """
        with self.driver.session() as session:
            session.run("""
                MERGE (s:Student {
                    id: $id,
                    name: $name,
                    gender: $gender,
                    major: $major,
                    grade: $grade
                })
                MERGE (c:Class {name: $class_name, grade: $grade, major: $major})
                MERGE (s)-[:BELONGS_TO]->(c)
            """, **student_data)
    
    def create_course_selection(self, student_id: str, course_code: str, 
                                grade: float = None, semester: str = None):
        """
        创建选课关系
        
        Args:
            student_id: 学生 ID
            course_code: 课程代码
            grade: 成绩（可选）
            semester: 学期（可选）
        """
        with self.driver.session() as session:
            query = """
                MATCH (s:Student {id: $student_id})
                MATCH (c:Course {code: $course_code})
                MERGE (s)-[r:SELECTED]->(c)
            """
            
            # 动态添加属性
            if grade is not None:
                query += " SET r.grade = $grade"
            if semester:
                query += " SET r.semester = $semester"
            
            session.run(query, student_id=student_id, course_code=course_code,
                       grade=grade, semester=semester)
    
    def create_classmate_relationships(self, class_name: str):
        """
        为班级内所有学生创建同学关系
        
        Args:
            class_name: 班级名称
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Class {name: $class_name})<-[:BELONGS_TO]-(s:Student)
                WITH collect(s) AS students
                UNWIND students AS s1
                UNWIND students AS s2
                WITH s1, s2
                WHERE s1.id < s2.id
                MERGE (s1)-[:CLASSMATE]->(s2)
                MERGE (s2)-[:CLASSMATE]->(s1)
            """, class_name=class_name)
            
            print(f"✅ 已为 {class_name} 创建同学关系")
    
    def query_student_classmates(self, student_name: str) -> List[Dict]:
        """
        查询某学生的所有同学
        
        Args:
            student_name: 学生姓名
            
        Returns:
            同学列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {name: $name})-[:CLASSMATE]->(classmate)
                RETURN classmate.name AS name,
                       classmate.id AS id,
                       classmate.major AS major
            """, name=student_name)
            
            return [record.data() for record in result]
    
    def query_student_courses(self, student_name: str) -> List[Dict]:
        """
        查询某学生的所有课程
        
        Args:
            student_name: 学生姓名
            
        Returns:
            课程列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {name: $name})-[r:SELECTED]->(c:Course)
                RETURN c.name AS course_name,
                       c.code AS course_code,
                       c.credit AS credit,
                       r.grade AS grade,
                       r.semester AS semester
                ORDER BY r.semester
            """, name=student_name)
            
            return [record.data() for record in result]
    
    def query_course_mates(self, student_name: str, course_name: str) -> List[Dict]:
        """
        查询某学生某课程的所有同学（一起上课的人）
        
        Args:
            student_name: 学生姓名
            course_name: 课程名称
            
        Returns:
            同班同学列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {name: $student_name})-[:SELECTED]->(c:Course {name: $course_name})
                MATCH (mate:Student)-[:SELECTED]->(c)
                WHERE mate.name <> $student_name
                RETURN mate.name AS name,
                       mate.id AS id,
                       mate.major AS major
            """, student_name=student_name, course_name=course_name)
            
            return [record.data() for record in result]
    
    def find_connection_path(self, name1: str, name2: str, max_depth: int = 4):
        """
        查找两个人之间的关系路径
        
        Args:
            name1: 第一个人姓名
            name2: 第二个人姓名
            max_depth: 最大搜索深度
            
        Returns:
            关系路径
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (s1:Student {name: $name1})-[:CLASSMATE|SELECTED|BELONGS_TO*1..$max_depth]-(s2:Student {name: $name2})
                )
                RETURN path, length(path) AS depth
            """, name1=name1, name2=name2, max_depth=max_depth)
            
            record = result.single()
            if record:
                return {
                    "path": record["path"],
                    "depth": record["depth"]
                }
            return None


# 使用示例
if __name__ == "__main__":
    kg = CampusKnowledgeGraph()
    
    # 初始化
    kg.clear_database()
    kg.create_indexes()
    
    # 创建学生
    students = [
        {"id": "2024001", "name": "张三", "gender": "男", "major": "CS", "grade": 2024, "class_name": "CS2401"},
        {"id": "2024002", "name": "李四", "gender": "女", "major": "CS", "grade": 2024, "class_name": "CS2401"},
        {"id": "2024003", "name": "王五", "gender": "男", "major": "CS", "grade": 2024, "class_name": "CS2401"},
    ]
    
    for student in students:
        kg.create_student(student)
    
    # 创建同学关系
    kg.create_classmate_relationships("CS2401")
    
    # 查询张三的同学
    classmates = kg.query_student_classmates("张三")
    print(f"\n张三的同学: {classmates}")
    
    kg.close()
```

### 3. Text-to-Cypher：自然语言转查询

```python
"""
Text-to-Cypher 转换器
将自然语言查询转换为 Cypher 查询
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional

class TextToCypher:
    """自然语言到 Cypher 查询转换器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # 提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是 Neo4j 图数据库专家。

任务：将自然语言问题转换为 Cypher 查询。

图谱 Schema：
- 节点类型：
  - Student: id, name, gender, major, grade
  - Course: code, name, credit
  - Teacher: id, name, department

- 关系类型：
  - (Student)-[:CLASSMATE]->(Student)
  - (Student)-[:SELECTED {grade, semester}]->(Course)
  - (Teacher)-[:TEACHES]->(Course)

规则：
1. 只返回 Cypher 查询语句，不要有其他解释
2. 使用参数化查询（$参数名）
3. 确保语法正确
4. 合理使用 LIMIT 限制结果数量

示例：
问题：张三有哪些同学？
查询：MATCH (s:Student {name: $name})-[:CLASSMATE]->(mate) RETURN mate.name AS name, mate.id AS id

问题：选修数据结构的学生有哪些？
查询：MATCH (s:Student)-[:SELECTED]->(c:Course {name: $course_name}) RETURN s.name AS name, s.id AS id"""),
            ("human", "问题：{question}")
        ])
    
    def convert(self, question: str) -> Optional[str]:
        """
        将自然语言转换为 Cypher
        
        Args:
            question: 自然语言问题
            
        Returns:
            Cypher 查询语句
        """
        chain = self.prompt | self.llm
        result = chain.invoke({"question": question})
        
        # 清理结果
        cypher = result.content.strip()
        if cypher.startswith("```cypher"):
            cypher = cypher[9:-3].strip()
        elif cypher.startswith("```"):
            cypher = cypher[3:-3].strip()
        
        return cypher


# 使用示例
if __name__ == "__main__":
    converter = TextToCypher()
    
    questions = [
        "张三有哪些同班同学？",
        "选修了数据结构的学生都有谁？",
        "张三和李四之间是什么关系？",
        "计算机科学专业的学生都选了哪些课程？"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        cypher = converter.convert(question)
        print(f"Cypher: {cypher}")
```

---

## 📊 性能优化

### 1. 索引策略

```cypher
// 唯一约束（自动创建索引）
CREATE CONSTRAINT student_id FOR (s:Student) REQUIRE s.id IS UNIQUE

// 普通索引
CREATE INDEX student_name FOR (s:Student) ON (s.name)
CREATE INDEX course_code FOR (c:Course) ON (c.code)

// 复合索引
CREATE INDEX student_major_grade FOR (s:Student) ON (s.major, s.grade)
```

### 2. 查询优化

```python
# 批量操作（推荐）
def batch_create_students(self, students: List[Dict]):
    """批量创建学生"""
    with self.driver.session() as session:
        session.run("""
            UNWIND $students AS student
            CREATE (s:Student)
            SET s = student
        """, students=students)

# 避免深层查询（限制深度）
def find_friends_within_3_hops(self, name: str):
    """限制查询深度为3层"""
    with self.driver.session() as session:
        result = session.run("""
            MATCH (s:Student {name: $name})-[:FRIEND*1..3]-(friend)
            RETURN DISTINCT friend.name
        """, name=name)
        return [record["friend.name"] for record in result]
```

### 3. 连接池配置

```python
from neo4j import GraphDatabase

# 优化连接池配置
driver = GraphDatabase.driver(
    uri,
    auth=(user, password),
    max_connection_pool_size=50,
    connection_acquisition_timeout=60,
    connection_timeout=30,
    max_transaction_retry_time=30.0
)
```

---

## 📚 学习资源

### 官方资源
- Neo4j 官方文档：https://neo4j.com/docs/
- Cypher 查询手册：https://neo4j.com/docs/cypher-manual/
- Neo4j 浏览器指南：http://localhost:7474/browser/

### 推荐阅读
- 《图数据库实战》
- 《Neo4j 权威指南》
- 《知识图谱：方法、实践与应用》

### 实践项目
1. **社交网络分析**：好友推荐、关系挖掘
2. **推荐系统**：基于图的协同过滤
3. **欺诈检测**：异常模式识别

---

**文档创建时间**：2026-01-30
**文档维护者**：CampusFlow 项目组
