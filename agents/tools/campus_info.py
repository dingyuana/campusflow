"""
Day 1: 校园信息查询工具集
包含图书馆、缴费、宿舍等基础查询工具
"""

from langchain.tools import tool
from datetime import datetime
import random


@tool
def query_campus_library_status() -> str:
    """查询图书馆当前开放状态和剩余座位数"""
    # 模拟真实数据（后续可接真实 API）
    current_hour = datetime.now().hour
    is_open = 8 <= current_hour <= 22
    seats_available = random.randint(50, 500) if is_open else 0
    
    return f"图书馆{'开放中' if is_open else '已闭馆'}，剩余座位：{seats_available}"


@tool
def query_tuition_payment(method: str) -> str:
    """
    查询学费缴纳方式详情
    Args:
        method: 缴纳方式，可选值："银行转账", "支付宝", "微信支付", "现场缴费"
    """
    payment_info = {
        "银行转账": "账号：6222-xxxx-xxxx，开户行：工商银行XX分行，备注：学号+姓名",
        "支付宝": "搜索生活号'XX大学财务处'，输入学号查询缴费",
        "微信支付": "关注公众号'XX大学'，菜单栏【学生服务】-【缴费大厅】",
        "现场缴费": "行政楼 302 财务处窗口，工作日 9:00-16:00"
    }
    return payment_info.get(method, "不支持该缴费方式")


@tool
def query_dormitory_info(building: str) -> str:
    """
    查询宿舍楼基本信息
    Args:
        building: 宿舍楼栋号，如"A1", "B3"
    """
    dorm_db = {
        "A1": "四人间，独立卫浴，空调，1200元/年",
        "A2": "六人间，公共卫浴，空调，800元/年",
        "B3": "四人间，独立卫浴，无空调，1000元/年"
    }
    return dorm_db.get(building, "未找到该宿舍楼信息，可选：A1, A2, B3")
