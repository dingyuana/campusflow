"""
数据访问层（DAO）- 学生相关
提供对数据库中 student 表的访问操作
"""

from typing import List, Dict, Any, Optional
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()


class StudentDAO:
    """学生数据访问对象"""

    def __init__(self):
        """
        初始化 Supabase 客户端
        """
        self.client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def create_student(self, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建学生记录

        Args:
            student_data: 学生数据字典

        Returns:
            创建的学生记录
        """
        try:
            result = self.client.table('students').insert(student_data).execute()
            if result.data:
                print(f"✅ 学生创建成功: {student_data.get('name')}")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ 创建学生失败: {e}")
            raise

    def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        根据学号查询学生

        Args:
            student_id: 学号

        Returns:
            学生记录
        """
        try:
            result = self.client.table('students').select("*").eq('student_id', student_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ 查询学生失败: {e}")
            return None

    def get_student_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        根据 UUID 查询学生

        Args:
            uuid: 学生 UUID

        Returns:
            学生记录
        """
        try:
            result = self.client.table('students').select("*").eq('id', uuid).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ 查询学生失败: {e}")
            return None

    def get_students_by_department(self, department_code: str) -> List[Dict[str, Any]]:
        """
        查询某院系的所有学生

        Args:
            department_code: 院系代码

        Returns:
            学生列表
        """
        try:
            result = self.client.table('students').select("*").eq('department_code', department_code).execute()
            return result.data
        except Exception as e:
            print(f"❌ 查询学生失败: {e}")
            return []

    def get_all_students(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有学生（分页）

        Args:
            limit: 每页数量
            offset: 偏移量

        Returns:
            学生列表
        """
        try:
            result = self.client.table('students').select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            print(f"❌ 查询学生失败: {e}")
            return []

    def update_student(self, student_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新学生信息

        Args:
            student_id: 学号
            update_data: 更新数据

        Returns:
            更新后的学生记录
        """
        try:
            result = self.client.table('students').update(update_data).eq('student_id', student_id).execute()
            if result.data:
                print(f"✅ 学生更新成功: {student_id}")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ 更新学生失败: {e}")
            raise

    def delete_student(self, student_id: str) -> bool:
        """
        删除学生记录

        Args:
            student_id: 学号

        Returns:
            是否删除成功
        """
        try:
            result = self.client.table('students').delete().eq('student_id', student_id).execute()
            print(f"✅ 学生删除成功: {student_id}")
            return True
        except Exception as e:
            print(f"❌ 删除学生失败: {e}")
            return False

    def search_students(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索学生（按姓名或学号）

        Args:
            keyword: 搜索关键词

        Returns:
            学生列表
        """
        try:
            result = self.client.table('students').select("*").or_(f"name.ilike.%{keyword}%,student_id.ilike.%{keyword}%").execute()
            return result.data
        except Exception as e:
            print(f"❌ 搜索学生失败: {e}")
            return []
