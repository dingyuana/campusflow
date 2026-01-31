"""
知识图谱工具模块
Day 3: Neo4j 知识图谱构建与查询
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

from neo4j import GraphDatabase

load_dotenv()


class Neo4jUtils:
    """Neo4j 知识图谱工具类"""

    def __init__(self):
        """
        初始化 Neo4j 连接
        """
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")

        self.driver = None

    def connect(self) -> bool:
        """
        连接 Neo4j 数据库

        Returns:
            连接是否成功
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            print(f"✅ Neo4j 连接成功！")
            print(f"   URI: {self.uri}")
            print(f"   User: {self.user}")
            return True
        except Exception as e:
            print(f"❌ Neo4j 连接失败: {e}")
            return False

    def close(self):
        """
        关闭 Neo4j 连接
        """
        if self.driver:
            self.driver.close()
            print("✅ Neo4j 连接已关闭")

    def clear_database(self):
        """
        清空数据库中的所有节点和关系

        注意：此操作不可逆，谨慎使用！
        """
        with self.driver.session() as session:
            result = session.run("MATCH (n) DETACH DELETE n")
            count = result.consume().counters.nodes_deleted
            print(f"✅ 已清空数据库，删除 {count} 个节点")

    def create_student(self, name: str, student_id: str, department: str = None) -> Dict[str, Any]:
        """
        创建学生节点

        Args:
            name: 学生姓名
            student_id: 学号
            department: 所属院系

        Returns:
            创建的学生信息
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (s:Student {student_id: $student_id})
                SET s.name = $name, s.department = $department
                RETURN s
            """, name=name, student_id=student_id, department=department)

            student = result.single()
            return student["s"] if student else None

    def create_teacher(self, name: str, teacher_id: str, department: str = None) -> Dict[str, Any]:
        """
        创建教师节点

        Args:
            name: 教师姓名
            teacher_id: 教师工号
            department: 所属院系

        Returns:
            创建的教师信息
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (t:Teacher {teacher_id: $teacher_id})
                SET t.name = $name, t.department = $department
                RETURN t
            """, name=name, teacher_id=teacher_id, department=department)

            teacher = result.single()
            return teacher["t"] if teacher else None

    def create_department(self, name: str, code: str) -> Dict[str, Any]:
        """
        创建院系节点

        Args:
            name: 院系名称
            code: 院系代码

        Returns:
            创建的院系信息
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (d:Department {code: $code})
                SET d.name = $name
                RETURN d
            """, name=name, code=code)

            department = result.single()
            return department["d"] if department else None

    def create_course(self, name: str, course_id: str, credit: int = 3) -> Dict[str, Any]:
        """
        创建课程节点

        Args:
            name: 课程名称
            course_id: 课程代码
            credit: 学分

        Returns:
            创建的课程信息
        """
        with self.driver.session() as session:
            result = session.run("""
                MERGE (c:Course {course_id: $course_id})
                SET c.name = $name, c.credit = $credit
                RETURN c
            """, name=name, course_id=course_id, credit=credit)

            course = result.single()
            return course["c"] if course else None

    def add_belong_to(self, student_id: str, department_code: str):
        """
        添加学生-院系归属关系

        Args:
            student_id: 学号
            department_code: 院系代码
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (s:Student {student_id: $student_id})
                MATCH (d:Department {code: $department_code})
                MERGE (s)-[:BELONGS_TO]->(d)
            """, student_id=student_id, department_code=department_code)
            print(f"✅ 添加学生 {student_id} - 院系 {department_code} 关系")

    def add_works_at(self, teacher_id: str, department_code: str):
        """
        添加教师-院系工作关系

        Args:
            teacher_id: 教师工号
            department_code: 院系代码
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (t:Teacher {teacher_id: $teacher_id})
                MATCH (d:Department {code: $department_code})
                MERGE (t)-[:WORKS_AT]->(d)
            """, teacher_id=teacher_id, department_code=department_code)
            print(f"✅ 添加教师 {teacher_id} - 院系 {department_code} 关系")

    def add_enrolled_in(self, student_id: str, course_id: str, semester: str = None):
        """
        添加学生-课程选课关系

        Args:
            student_id: 学号
            course_id: 课程代码
            semester: 学期
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (s:Student {student_id: $student_id})
                MATCH (c:Course {course_id: $course_id})
                MERGE (s)-[r:ENROLLED_IN]->(c)
                SET r.semester = $semester
            """, student_id=student_id, course_id=course_id, semester=semester)
            print(f"✅ 添加学生 {student_id} - 课程 {course_id} 选课关系")

    def add_teaches(self, teacher_id: str, course_id: str):
        """
        添加教师-课程任教关系

        Args:
            teacher_id: 教师工号
            course_id: 课程代码
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (t:Teacher {teacher_id: $teacher_id})
                MATCH (c:Course {course_id: $course_id})
                MERGE (t)-[:TEACHES]->(c)
            """, teacher_id=teacher_id, course_id=course_id)
            print(f"✅ 添加教师 {teacher_id} - 课程 {course_id} 任教关系")

    def find_students_by_department(self, department_code: str) -> List[Dict[str, Any]]:
        """
        查找某院系的所有学生

        Args:
            department_code: 院系代码

        Returns:
            学生列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student)-[:BELONGS_TO]->(d:Department {code: $code})
                RETURN s.name AS name, s.student_id AS student_id
            """, code=department_code)

            return [record.data() for record in result]

    def find_courses_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """
        查找某学生选修的所有课程

        Args:
            student_id: 学号

        Returns:
            课程列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {student_id: $student_id})-[:ENROLLED_IN]->(c:Course)
                RETURN c.name AS name, c.course_id AS course_id, c.credit AS credit
            """, student_id=student_id)

            return [record.data() for record in result]

    def find_students_by_course(self, course_id: str) -> List[Dict[str, Any]]:
        """
        查找选修某课程的所有学生

        Args:
            course_id: 课程代码

        Returns:
            学生列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student)-[:ENROLLED_IN]->(c:Course {course_id: $course_id})
                RETURN s.name AS name, s.student_id AS student_id
            """, course_id=course_id)

            return [record.data() for record in result]

    def find_teacher_by_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        查找某课程的任课教师

        Args:
            course_id: 课程代码

        Returns:
            教师信息
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Teacher)-[:TEACHES]->(c:Course {course_id: $course_id})
                RETURN t.name AS name, t.teacher_id AS teacher_id, t.department AS department
            """, course_id=course_id)

            record = result.single()
            return record.data() if record else None

    def multi_hop_query(self, student_id: str, course_id: str) -> List[Dict[str, Any]]:
        """
        多跳查询：查找学生的同学（选修相同课程的其他学生）

        Args:
            student_id: 学号
            course_id: 课程代码

        Returns:
            同学列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s1:Student {student_id: $student_id})-[:ENROLLED_IN]->(c:Course {course_id: $course_id})<-[:ENROLLED_IN]-(s2:Student)
                WHERE s1 <> s2
                RETURN s2.name AS name, s2.student_id AS student_id, c.name AS course_name
            """, student_id=student_id, course_id=course_id)

            return [record.data() for record in result]

    def find_classmates(self, student_id: str) -> List[Dict[str, Any]]:
        """
        查找某学生的所有同学（选修相同课程的所有学生）

        Args:
            student_id: 学号

        Returns:
            同学列表
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s1:Student {student_id: $student_id})-[:ENROLLED_IN]->(c:Course)<-[:ENROLLED_IN]-(s2:Student)
                WHERE s1 <> s2
                RETURN DISTINCT s2.name AS name, s2.student_id AS student_id
            """, student_id=student_id)

            return [record.data() for record in result]

    def find_path(self, student_id: str, teacher_name: str) -> List[Dict[str, Any]]:
        """
        查找学生到教师的最短路径

        Args:
            student_id: 学号
            teacher_name: 教师姓名

        Returns:
            路径信息
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH p=shortestPath(
                    (s:Student {student_id: $student_id})-[*]-(t:Teacher {name: $teacher_name})
                )
                RETURN [node in nodes(p) | {
                    type: labels(node)[0],
                    name: coalesce(node.name, node.student_id, node.teacher_id, node.course_id),
                    id: coalesce(node.student_id, node.teacher_id, node.course_id)
                }] AS path
            """, student_id=student_id, teacher_name=teacher_name)

            record = result.single()
            return record.data()["path"] if record else None

    def get_statistics(self) -> Dict[str, int]:
        """
        获取知识图谱统计信息

        Returns:
            统计信息字典
        """
        with self.driver.session() as session:
            stats = {}

            # 节点统计
            for label in ["Student", "Teacher", "Department", "Course"]:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) AS count")
                stats[f"{label.lower()}_count"] = result.single()["count"]

            # 关系统计
            for rel_type in ["BELONGS_TO", "WORKS_AT", "ENROLLED_IN", "TEACHES"]:
                result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) AS count")
                stats[f"{rel_type.lower()}_count"] = result.single()["count"]

            return stats


def build_sample_knowledge_graph():
    """
    构建示例智慧校园知识图谱
    """
    print("=" * 60)
    print("🚀 构建智慧校园知识图谱")
    print("=" * 60)
    print()

    # 创建 Neo4j 工具实例
    neo4j = Neo4jUtils()

    # 连接数据库
    if not neo4j.connect():
        print("❌ 无法连接到 Neo4j，程序退出")
        return

    # 清空数据库
    print("\n清空数据库...")
    neo4j.clear_database()

    # 创建院系
    print("\n创建院系...")
    neo4j.create_department("计算机学院", "CS")
    neo4j.create_department("数学学院", "MATH")
    neo4j.create_department("物理学院", "PHYS")

    # 创建教师
    print("\n创建教师...")
    neo4j.create_teacher("张教授", "T001", "CS")
    neo4j.create_teacher("李教授", "T002", "MATH")
    neo4j.create_teacher("王教授", "T003", "CS")

    # 创建学生
    print("\n创建学生...")
    neo4j.create_student("张三", "S001", "CS")
    neo4j.create_student("李四", "S002", "CS")
    neo4j.create_student("王五", "S003", "MATH")
    neo4j.create_student("赵六", "S004", "PHYS")

    # 创建课程
    print("\n创建课程...")
    neo4j.create_course("Python 程序设计", "C001", 3)
    neo4j.create_course("数据结构", "C002", 4)
    neo4j.create_course("高等数学", "C003", 5)
    neo4j.create_course("机器学习", "C004", 3)

    # 添加归属关系
    print("\n添加归属关系...")
    neo4j.add_belong_to("S001", "CS")
    neo4j.add_belong_to("S002", "CS")
    neo4j.add_belong_to("S003", "MATH")
    neo4j.add_belong_to("S004", "PHYS")

    # 添加工作关系
    print("\n添加工作关系...")
    neo4j.add_works_at("T001", "CS")
    neo4j.add_works_at("T002", "MATH")
    neo4j.add_works_at("T003", "CS")

    # 添加任教关系
    print("\n添加任教关系...")
    neo4j.add_teaches("T001", "C001")
    neo4j.add_teaches("T001", "C004")
    neo4j.add_teaches("T002", "C003")
    neo4j.add_teaches("T003", "C002")

    # 添加选课关系
    print("\n添加选课关系...")
    neo4j.add_enrolled_in("S001", "C001", "2024春")
    neo4j.add_enrolled_in("S001", "C002", "2024春")
    neo4j.add_enrolled_in("S002", "C001", "2024春")
    neo4j.add_enrolled_in("S002", "C004", "2024春")
    neo4j.add_enrolled_in("S003", "C003", "2024春")
    neo4j.add_enrolled_in("S004", "C002", "2024春")

    # 显示统计信息
    print("\n知识图谱统计：")
    print("-" * 60)
    stats = neo4j.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print()
    print("=" * 60)
    print("🎉 知识图谱构建完成！")
    print("=" * 60)

    # 关闭连接
    neo4j.close()

    return neo4j


def test_queries():
    """
    测试各种查询功能
    """
    print("\n")
    print("=" * 60)
    print("🔍 测试查询功能")
    print("=" * 60)
    print()

    # 创建 Neo4j 工具实例
    neo4j = Neo4jUtils()
    neo4j.connect()

    # 查询 1：查找计算机学院的学生
    print("查询 1：查找计算机学院的学生")
    print("-" * 60)
    students = neo4j.find_students_by_department("CS")
    for student in students:
        print(f"  {student['name']} ({student['student_id']})")
    print()

    # 查询 2：查找张三选修的课程
    print("查询 2：查找张三选修的课程")
    print("-" * 60)
    courses = neo4j.find_courses_by_student("S001")
    for course in courses:
        print(f"  {course['name']} ({course['course_id']}) - {course['credit']} 学分")
    print()

    # 查询 3：查找选修 Python 程序设计的学生
    print("查询 3：查找选修 Python 程序设计的学生")
    print("-" * 60)
    students = neo4j.find_students_by_course("C001")
    for student in students:
        print(f"  {student['name']} ({student['student_id']})")
    print()

    # 查询 4：查找 Python 程序设计的任课教师
    print("查询 4：查找 Python 程序设计的任课教师")
    print("-" * 60)
    teacher = neo4j.find_teacher_by_course("C001")
    if teacher:
        print(f"  {teacher['name']} ({teacher['teacher_id']}) - {teacher['department']}")
    print()

    # 查询 5：查找张三的选修同一课程的同学
    print("查询 5：查找张三的选修同一课程的同学")
    print("-" * 60)
    classmates = neo4j.find_classmates("S001")
    for classmate in classmates:
        print(f"  {classmate['name']} ({classmate['student_id']})")
    print()

    # 查询 6：查找张三到张教授的最短路径
    print("查询 6：查找张三到张教授的最短路径")
    print("-" * 60)
    path = neo4j.find_path("S001", "张教授")
    if path:
        for i, node in enumerate(path, 1):
            print(f"  {i}. {node['type']}: {node['name']}")
    print()

    print("=" * 60)
    print("✅ 查询测试完成！")
    print("=" * 60)

    # 关闭连接
    neo4j.close()


if __name__ == "__main__":
    # 构建示例知识图谱
    build_sample_knowledge_graph()

    # 测试查询功能
    test_queries()
