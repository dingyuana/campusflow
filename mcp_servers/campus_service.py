"""
Day 9: MCP Server 校务系统集成
封装教务、财务、宿管系统 API
"""

from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime


# 创建 MCP Server
mcp = FastMCP("campus_service")


# 模拟校务系统数据库
MOCK_DB = {
    "students": {
        "2024001": {"name": "李明", "tuition_paid": False, "dorm_assigned": "A1-301"},
        "2024002": {"name": "王芳", "tuition_paid": True, "dorm_assigned": "A2-205"}
    },
    "courses": {
        "CS101": {"name": "Python编程", "capacity": 100, "enrolled": 85},
        "CS102": {"name": "数据结构", "capacity": 80, "enrolled": 78}
    }
}


@mcp.tool()
def check_tuition_status(student_id: str) -> str:
    """
    查询学生缴费状态
    
    Args:
        student_id: 学生学号，如"2024001"
        
    Returns:
        JSON 格式的缴费状态
    """
    student = MOCK_DB["students"].get(student_id)
    if not student:
        return json.dumps({"error": "学生不存在"}, ensure_ascii=False)
    
    status = "已缴费" if student["tuition_paid"] else "未缴费"
    return json.dumps({
        "student_id": student_id,
        "name": student["name"],
        "tuition_status": status,
        "timestamp": datetime.now().isoformat()
    }, ensure_ascii=False)


@mcp.tool()
def assign_dormitory(student_id: str, building: str, room: str) -> str:
    """
    分配宿舍（宿管系统接口）
    
    Args:
        student_id: 学生学号
        building: 楼栋，如"A1"
        room: 房间号，如"301"
        
    Returns:
        JSON 格式的分配结果
    """
    if student_id not in MOCK_DB["students"]:
        return json.dumps({"error": "学生不存在"}, ensure_ascii=False)
    
    dorm_id = f"{building}-{room}"
    MOCK_DB["students"][student_id]["dorm_assigned"] = dorm_id
    
    return json.dumps({
        "success": True,
        "student_id": student_id,
        "dormitory": dorm_id,
        "message": f"成功分配宿舍：{dorm_id}"
    }, ensure_ascii=False)


@mcp.tool()
def query_course_enrollment(course_id: str) -> str:
    """
    查询课程选课人数（教务系统接口）
    
    Args:
        course_id: 课程代码，如"CS101"
        
    Returns:
        JSON 格式的选课信息
    """
    course = MOCK_DB["courses"].get(course_id)
    if not course:
        return json.dumps({"error": "课程不存在"}, ensure_ascii=False)
    
    remaining = course["capacity"] - course["enrolled"]
    return json.dumps({
        "course_id": course_id,
        "course_name": course["name"],
        "capacity": course["capacity"],
        "enrolled": course["enrolled"],
        "remaining": remaining,
        "status": "已满" if remaining <= 0 else "可选课"
    }, ensure_ascii=False)


@mcp.resource("student://{student_id}/profile")
def get_student_profile(student_id: str) -> str:
    """
    MCP Resource：获取学生档案（URI 访问模式）
    
    Args:
        student_id: 学生学号
        
    Returns:
        JSON 格式的学生档案
    """
    student = MOCK_DB["students"].get(student_id)
    if not student:
        return "学生不存在"
    
    return json.dumps(student, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 启动 Server（Stdio 模式）
    print("🚀 启动 MCP Server (Stdio 模式)...")
    mcp.run(transport='stdio')
