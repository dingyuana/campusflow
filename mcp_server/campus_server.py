"""
Day 9: MCP Server 开发

实现 Model Context Protocol 服务器
封装校务三大系统：教务、财务、宿管
"""

from typing import Any, Dict, List
from langchain.tools import tool
from pydantic import BaseModel, Field


# 教务系统查询
class AcademicQueryInput(BaseModel):
    student_id: str = Field(description="学号")


@tool(args_schema=AcademicQueryInput)
def query_academic_record(student_id: str) -> Dict[str, Any]:
    """
    查询学生学籍信息
    
    包括：专业、年级、学分、GPA
    """
    # 模拟数据
    return {
        "student_id": student_id,
        "major": "计算机科学与技术",
        "grade": "2024级",
        "credits": 45,
        "gpa": 3.7
    }


# 财务系统查询
class PaymentQueryInput(BaseModel):
    student_id: str = Field(description="学号")


@tool(args_schema=PaymentQueryInput)
def query_payment_status(student_id: str) -> Dict[str, Any]:
    """
    查询缴费状态
    
    包括：学费、住宿费缴费情况
    """
    return {
        "student_id": student_id,
        "tuition_paid": True,
        "tuition_amount": 6500,
        "dorm_paid": True,
        "dorm_amount": 1200,
        "outstanding": 0
    }


# 宿管系统查询
class DormQueryInput(BaseModel):
    student_id: str = Field(description="学号")


@tool(args_schema=DormQueryInput)
def query_dormitory_assignment(student_id: str) -> Dict[str, Any]:
    """
    查询宿舍分配情况
    
    包括：宿舍楼、房间号、室友
    """
    return {
        "student_id": student_id,
        "building": "东区1号楼",
        "room": "302",
        "roommates": ["S002", "S003"],
        "bed": 2
    }


def get_mcp_tools() -> List:
    """获取所有 MCP 工具"""
    return [
        query_academic_record,
        query_payment_status,
        query_dormitory_assignment
    ]
