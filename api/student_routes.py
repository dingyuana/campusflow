"""
API 层（接口层）- 学生相关
提供学生相关的 RESTful API 接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from api.services.student_service import StudentService


# Pydantic 模型定义
class StudentCreate(BaseModel):
    """学生创建模型"""
    student_id: str
    name: str
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    department_code: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = "active"


class StudentUpdate(BaseModel):
    """学生更新模型"""
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    department_code: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None


class EnrollmentCreate(BaseModel):
    """选课创建模型"""
    student_id: str
    course_id: str
    semester: str


# 创建路由器
router = APIRouter(prefix="/api/students", tags=["学生"])
student_service = StudentService()


@router.post("/", response_model=dict)
def create_student(student: StudentCreate):
    """
    创建学生记录

    Args:
        student: 学生数据

    Returns:
        创建的学生记录
    """
    try:
        result = student_service.create_student(student.dict())
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建学生失败: {str(e)}")


@router.get("/{student_id}", response_model=dict)
def get_student(student_id: str):
    """
    获取学生信息（包含选课）

    Args:
        student_id: 学号

    Returns:
        学生信息
    """
    try:
        result = student_service.get_student(student_id)
        if not result:
            raise HTTPException(status_code=404, detail="学生不存在")

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生失败: {str(e)}")


@router.get("/", response_model=dict)
def get_students(
    department_code: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    获取学生列表（支持按院系筛选）

    Args:
        department_code: 院系代码（可选）
        limit: 每页数量
        offset: 偏移量

    Returns:
        学生列表
    """
    try:
        result = student_service.get_students(department_code, limit, offset)
        return {
            "success": True,
            "data": result,
            "total": len(result),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询学生列表失败: {str(e)}")


@router.put("/{student_id}", response_model=dict)
def update_student(student_id: str, student_update: StudentUpdate):
    """
    更新学生信息

    Args:
        student_id: 学号
        student_update: 更新数据

    Returns:
        更新后的学生信息
    """
    try:
        result = student_service.update_student(student_id, student_update.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="学生不存在")

        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新学生失败: {str(e)}")


@router.delete("/{student_id}", response_model=dict)
def delete_student(student_id: str):
    """
    删除学生记录

    Args:
        student_id: 学号

    Returns:
        删除结果
    """
    try:
        success = student_service.delete_student(student_id)
        if not success:
            raise HTTPException(status_code=404, detail="学生不存在")

        return {
            "success": True,
            "message": "学生删除成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除学生失败: {str(e)}")


@router.get("/search/{keyword}", response_model=dict)
def search_students(keyword: str):
    """
    搜索学生（按姓名或学号）

    Args:
        keyword: 搜索关键词

    Returns:
        学生列表
    """
    try:
        result = student_service.search_students(keyword)
        return {
            "success": True,
            "data": result,
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索学生失败: {str(e)}")


@router.post("/{student_id}/enrollments", response_model=dict)
def enroll_course(student_id: str, enrollment: EnrollmentCreate):
    """
    学生选课

    Args:
        student_id: 学号
        enrollment: 选课数据

    Returns:
        选课记录
    """
    try:
        # 获取学生 UUID
        student = student_service.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")

        result = student_service.enroll_course(
            student['id'],
            enrollment.course_id,
            enrollment.semester
        )
        return {
            "success": True,
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"选课失败: {str(e)}")


@router.get("/{student_id}/enrollments", response_model=dict)
def get_student_courses(student_id: str, semester: Optional[str] = None):
    """
    获取学生的选课列表

    Args:
        student_id: 学号
        semester: 学期（可选）

    Returns:
        选课列表
    """
    try:
        # 获取学生 UUID
        student = student_service.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="学生不存在")

        result = student_service.get_student_courses(student['id'], semester)
        return {
            "success": True,
            "data": result,
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询选课失败: {str(e)}")


@router.delete("/enrollments/{enrollment_id}", response_model=dict)
def drop_course(enrollment_id: str):
    """
    学生退课

    Args:
        enrollment_id: 选课记录 ID

    Returns:
        退课结果
    """
    try:
        success = student_service.drop_course(enrollment_id)
        if not success:
            raise HTTPException(status_code=404, detail="选课记录不存在")

        return {
            "success": True,
            "message": "退课成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"退课失败: {str(e)}")
