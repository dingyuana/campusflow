"""
Day 12: 并行计算

实现：
- 节点并行 (Send API)
- Map-Reduce 批量处理
- 异步任务
"""

import asyncio
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed


class ParallelProcessor:
    """并行处理器"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
    
    def parallel_map(
        self,
        func: Callable,
        items: List[Any],
        *args
    ) -> List[Any]:
        """
        Map-Reduce 并行处理
        
        Args:
            func: 处理函数
            items: 待处理项列表
            *args: 额外参数
            
        Returns:
            处理结果列表
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_item = {
                executor.submit(func, item, *args): item 
                for item in items
            }
            
            # 收集结果
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append((item, result, None))
                except Exception as e:
                    results.append((item, None, str(e)))
        
        return results
    
    async def async_batch_process(
        self,
        func: Callable,
        items: List[Any]
    ) -> List[Any]:
        """异步批量处理"""
        tasks = [func(item) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)


def batch_generate_welcome_letters(students: List[Dict]) -> List[str]:
    """
    批量生成欢迎信示例
    
    Map-Reduce 模式：
    - Map: 为每个学生生成信件
    - Reduce: 合并结果
    """
    def generate_letter(student: Dict) -> str:
        return f"""
        亲爱的 {student['name']} 同学：
        
        欢迎来到 CampusFlow 智慧校园！
        您的学号是 {student['student_id']}，所属 {student['major']} 专业。
        
        祝您学业顺利！
        """
    
    processor = ParallelProcessor(max_workers=3)
    results = processor.parallel_map(generate_letter, students)
    
    return [r[1] for r in results if r[1]]
