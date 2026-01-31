"""
业务逻辑层（Service）- 学生相关
提供学生相关的业务逻辑
"""

from typing import List, Dict, Any, Optional
from api.dao.student_dao import StudentDAO
from api.dao.course_dao import CourseDAO, EnrollmentDAO


class StudentService:
    """学生服务"""

    def __init__(self):
        """
        初始化学生服务
        """
        self.student_dao = StudentDAO()
        self.course_dao = CourseDAO()
        self.enrollment_dao = EnrollmentDAO()

    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建学生记录（包含业务逻辑）

        Args:
            student_data: 学生数据

        Returns:
            创建的学生记录
        """
        # 业务逻辑：验证必填字段
        required_fields = ['student_id', 'name']
        for field in required_fields:
            if field not in student_data:
                raise ValueError(f"缺少必填字段: {field}")

        # 业务逻辑：检查学号是否已存在
        existing = self.student_dao.get_student_by_id(student_data['student_id'])
        if existing:
            raise ValueError(f"学号 {student_data['student_id']} 已存在")

        # 创建学生
        return self.student_dao.create_student(student_data)

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        获取学生信息（包含选课信息）

        Args:
            student_id: 学号

        Returns:
            学生信息（含选课）
        """
        # 获取基本信息
        student = self.student_dao.get_student_by_id(student_id)
        if not student:
            return None

        # 获取选课信息
        enrollments = self.enrollment_dao.get_student_courses(student['id'])

        # 组合结果
        result = {
            **student,
            'courses': enrollments
        }

        return result

    def get_students(self, department_code: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取学生列表（支持按院系筛选）

        Args:
            department_code: 院系代码（可选）
            limit: 每页数量
            offset: 偏移量

        Returns:
            学生列表
        """
        if department_code:
            return self.student_dao.get_students_by_department(department_code)
        else:
            return self.student_dao.get_all_students(limit, offset)

    def update_student(self, student_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新学生信息（包含业务逻辑）

        Args:
            student_id: 学号
            update_data: 更新数据

        Returns:
            更新后的学生信息
        """
        # 业务逻辑：不允许修改学号
        if 'student_id' in update_data:
            del update_data['student_id']

        # 更新学生
        return self.student_dao.update_student(student_id, update_data)

    def delete_student(self, student_id: str) -> bool:
        """
        删除学生记录（包含业务逻辑）

        Args:
            student_id: 学号

        Returns:
            是否删除成功
        """
        # 业务逻辑：检查学生是否有选课记录
        student = self.student_dao.get_student_by_id(student_id)
        if student:
            enrollments = self.enrollment_dao.get_student_courses(student['id'])
            if enrollments:
                raise ValueError("该学生有选课记录，无法删除")

        # 删除学生
        return self.student_dao.delete_student(student_id)

    def search_students(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索学生

        Args:
            keyword: 搜索关键词

        Returns:
            学生列表
        """
        return self.student_dao.search_students(keyword)

    def enroll_course(self, student_id: str, course_id: str, semester: str) -> Dict[str, Any]:
        """
        学生选课（包含业务逻辑）

        Args:
            student_id: 学生 UUID
            course_id: 课程 UUID
            semester: 学期

        Returns:
            选课记录
        """
        # 业务逻辑：检查课程是否存在
        course = self.course_dao.get_course_by_id(course_id)
        if not course:
            raise ValueError(f"课程 {course_id} 不存在")

        # 业务逻辑：检查是否已选过该课程
        existing_enrollments = self.enrollment_dao.get_student_courses(student_id, semester)
        for enrollment in existing_enrollments:
            if enrollment['course_id'] == course_id:
                raise ValueError("该学生已选修此课程")

        # 创建选课记录
        enrollment_data = {
            'student_id': student_id,
            'course_id': course_id,
            'semester': semester,
            'status': 'enrolled'
        }

        return self.enrollment_dao.enroll_course(enrollment_data)

    def drop_course(self, enrollment_id: str) -> bool:
        """
        学生退课（包含业务逻辑）

        Args:
            enrollment_id: 选课记录 ID

        Returns:
            是否退课成功
        """
        # 业务逻辑：不允许退已完成或已及格的课程
        # 这里可以添加更多业务逻辑

        # 退课
        return self.enrollment_dao.drop_course(enrollment_id)

    def get_student_courses(self, student_id: str, semester: str = None) -> List[Dict[str, Any]]:
        """
        获取学生的选课列表

        Args:
            student_id: 学生 UUID
            semester: 学期（可选）

        Returns:
            选课列表
        """
        return self.enrollment_dao.get_student_courses(student_id, semester)
