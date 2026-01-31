"""
数据访问层（DAO）- 课程相关
提供对数据库中 course 和 enrollment 表的访问操作
"""

from typing import List, Dict, Any, Optional
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()


class CourseDAO:
    """课程数据访问对象"""

    def __init__(self):
        """
        初始化 Supabase 客户端
        """
        self.client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def create_course(self, course_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建课程记录

        Args:
            course_data: 课程数据字典

        Returns:
            创建的课程记录
        """
        try:
            result = self.client.table('courses').insert(course_data).execute()
            if result.data:
                print(f"✅ 课程创建成功: {course_data.get('name')}")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ 创建课程失败: {e}")
            raise

    def get_course_by_id(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        根据课程代码查询课程

        Args:
            course_id: 课程代码

        Returns:
            课程记录
        """
        try:
            result = self.client.table('courses').select("*").eq('course_id', course_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ 查询课程失败: {e}")
            return None

    def get_all_courses(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有课程（分页）

        Args:
            limit: 每页数量
            offset: 偏移量

        Returns:
            课程列表
        """
        try:
            result = self.client.table('courses').select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            print(f"❌ 查询课程失败: {e}")
            return []

    def update_course(self, course_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新课程信息

        Args:
            course_id: 课程代码
            update_data: 更新数据

        Returns:
            更新后的课程记录
        """
        try:
            result = self.client.table('courses').update(update_data).eq('course_id', course_id).execute()
            if result.data:
                print(f"✅ 课程更新成功: {course_id}")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ 更新课程失败: {e}")
            raise

    def delete_course(self, course_id: str) -> bool:
        """
        删除课程记录

        Args:
            course_id: 课程代码

        Returns:
            是否删除成功
        """
        try:
            result = self.client.table('courses').delete().eq('course_id', course_id).execute()
            print(f"✅ 课程删除成功: {course_id}")
            return True
        except Exception as e:
            print(f"❌ 删除课程失败: {e}")
            return False

    def search_courses(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索课程（按名称或代码）

        Args:
            keyword: 搜索关键词

        Returns:
            课程列表
        """
        try:
            result = self.client.table('courses').select("*").or_(f"name.ilike.%{keyword}%,course_id.ilike.%{keyword}%").execute()
            return result.data
        except Exception as e:
            print(f"❌ 搜索课程失败: {e}")
            return []


class EnrollmentDAO:
    """选课数据访问对象"""

    def __init__(self):
        """
        初始化 Supabase 客户端
        """
        self.client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def enroll_course(self, enrollment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        学生选课

        Args:
            enrollment_data: 选课数据字典
                         必须包含: student_id, course_id, semester

        Returns:
            选课记录
        """
        try:
            result = self.client.table('enrollments').insert(enrollment_data).execute()
            if result.data:
                print(f"✅ 选课成功")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ 选课失败: {e}")
            raise

    def get_student_courses(self, student_id: str, semester: str = None) -> List[Dict[str, Any]]:
        """
        查询某学生的选课记录

        Args:
            student_id: 学生 UUID
            semester: 学期（可选）

        Returns:
            选课列表
        """
        try:
            query = self.client.table('enrollments').select("*, courses(*)").eq('student_id', student_id)
            if semester:
                query = query.eq('semester', semester)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"❌ 查询选课失败: {e}")
            return []

    def get_course_students(self, course_id: str, semester: str = None) -> List[Dict[str, Any]]:
        """
        查询选修某课程的所有学生

        Args:
            course_id: 课程 UUID
            semester: 学期（可选）

        Returns:
            学生列表
        """
        try:
            query = self.client.table('enrollments').select("*, students(*)").eq('course_id', course_id)
            if semester:
                query = query.eq('semester', semester)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"❌ 查询选课学生失败: {e}")
            return []

    def drop_course(self, enrollment_id: str) -> bool:
        """
        学生退课

        Args:
            enrollment_id: 选课记录 ID

        Returns:
            是否退课成功
        """
        try:
            result = self.client.table('enrollments').delete().eq('id', enrollment_id).execute()
            print(f"✅ 退课成功")
            return True
        except Exception as e:
            print(f"❌ 退课失败: {e}")
            return False

    def update_score(self, enrollment_id: str, score: float) -> Optional[Dict[str, Any]]:
        """
        更新选课成绩

        Args:
            enrollment_id: 选课记录 ID
            score: 成绩

        Returns:
            更新后的选课记录
        """
        try:
            result = self.client.table('enrollments').update({'score': score, 'status': 'completed'}).eq('id', enrollment_id).execute()
            if result.data:
                print(f"✅ 成绩更新成功")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ 更新成绩失败: {e}")
            raise
