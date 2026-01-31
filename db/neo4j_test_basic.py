"""
Neo4j 数据库连接测试
Day 3: Neo4j 知识图谱基础功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("=" * 50)
print("🧪 Neo4j 基础功能测试")
print("=" * 50)
print()

all_passed = True

# 测试 1：文件结构检查
print("1. 测试文件结构...")
print("-" * 50)

files_to_check = [
    "db/neo4j_utils.py",
    "docs/教学文件/neo4j知识图谱.md",
    ".env"
]

for file_path in files_to_check:
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {file_path} {'存在' if exists else '不存在'}")
    if not exists:
        all_passed = False

print()

# 测试 2：环境变量配置
print("2. 测试环境变量配置...")
print("-" * 50)

from dotenv import load_dotenv
import os

load_dotenv()

required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]

for var_name in required_vars:
    value = os.getenv(var_name)
    if value:
        print(f"✅ {var_name} 已配置")
    else:
        print(f"❌ {var_name} 未配置")
        all_passed = False

print()

# 测试 3：Python 导入
print("3. 测试 Python 导入...")
print("-" * 50)

try:
    from neo4j import GraphDatabase
    print("✅ neo4j 导入成功")
except ImportError as e:
    print(f"❌ neo4j 导入失败: {e}")
    all_passed = False

try:
    from db.neo4j_utils import Neo4jUtils
    print("✅ db.neo4j_utils 导入成功")
except ImportError as e:
    print(f"❌ db.neo4j_utils 导入失败: {e}")
    all_passed = False

print()

# 测试 4：Neo4j 连接测试
print("4. 测试 Neo4j 连接...")
print("-" * 50)

try:
    from db.neo4j_utils import Neo4jUtils

    neo4j = Neo4jUtils()
    if neo4j.connect():
        print("✅ Neo4j 连接成功")

        # 测试查询
        with neo4j.driver.session() as session:
            result = session.run("RETURN 1 AS num")
            count = result.single()["num"]
            print(f"✅ 查询测试成功: {count}")

        neo4j.close()
    else:
        print("❌ Neo4j 连接失败")
        all_passed = False

except Exception as e:
    print(f"❌ Neo4j 测试失败: {e}")
    all_passed = False

print()

# 测试 5：创建简单节点
print("5. 测试创建节点...")
print("-" * 50)

try:
    from db.neo4j_utils import Neo4jUtils

    neo4j = Neo4jUtils()
    neo4j.connect()

    # 创建测试节点
    student = neo4j.create_student("测试学生", "TEST001", "CS")
    if student:
        print("✅ 学生节点创建成功")
        print(f"   姓名: {student.get('name')}")
        print(f"   学号: {student.get('student_id')}")
    else:
        print("❌ 学生节点创建失败")
        all_passed = False

    # 清理测试节点
    with neo4j.driver.session() as session:
        result = session.run("""
            MATCH (s:Student {student_id: 'TEST001'})
            DELETE s
        """)
        print("✅ 测试节点清理完成")

    neo4j.close()

except Exception as e:
    print(f"❌ 节点创建测试失败: {e}")
    all_passed = False

print()

# 测试 6：Cypher 查询语法
print("6. 测试 Cypher 查询语法...")
print("-" * 50)

try:
    from db.neo4j_utils import Neo4jUtils

    neo4j = Neo4jUtils()
    neo4j.connect()

    # 测试 MATCH 查询
    with neo4j.driver.session() as session:
        result = session.run("""
            MATCH (n)
            RETURN count(n) AS count
        """)
        count = result.single()["count"]
        print(f"✅ MATCH 查询成功，当前节点数: {count}")

    # 测试 CREATE 查询
    with neo4j.driver.session() as session:
        result = session.run("""
            CREATE (t:TestNode {name: 'test'})
            RETURN t.name AS name
        """)
        name = result.single()["name"]
        print(f"✅ CREATE 查询成功，节点名称: {name}")

    # 清理测试节点
    with neo4j.driver.session() as session:
        session.run("MATCH (t:TestNode) DELETE t")
        print("✅ 测试节点清理完成")

    neo4j.close()

except Exception as e:
    print(f"❌ Cypher 查询测试失败: {e}")
    all_passed = False

print()

# 测试 7：统计信息查询
print("7. 测试统计信息查询...")
print("-" * 50)

try:
    from db.neo4j_utils import Neo4jUtils

    neo4j = Neo4jUtils()
    neo4j.connect()

    stats = neo4j.get_statistics()
    print("✅ 统计信息获取成功:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    neo4j.close()

except Exception as e:
    print(f"❌ 统计信息查询失败: {e}")
    all_passed = False

print()

# 总结
print("=" * 50)
print("📊 测试总结")
print("=" * 50)

if all_passed:
    print("🎉 所有测试通过！Neo4j 基础功能正常")
    sys.exit(0)
else:
    print("⚠️  部分测试失败，请检查上述错误")
    sys.exit(1)
