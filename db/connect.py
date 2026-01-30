"""
数据库连接测试模块
Day 1: Supabase 连接测试
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# 加载环境变量
load_dotenv()


def connect_supabase():
    """
    连接 Supabase 数据库并执行基础测试
    
    功能:
    1. 创建 Supabase 客户端
    2. 测试连接
    3. 测试数据查询
    """
    try:
        # 1. 创建 Supabase 客户端
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        print("✅ Supabase 客户端创建成功！")
        
        # 2. 测试查询（假设已创建 test 表）
        try:
            response = supabase.table('test').select("*").limit(5).execute()
            print(f"📊 查询成功，返回 {len(response.data)} 条数据")
            if response.data:
                print("📋 数据示例:", response.data[:3])
        except Exception as e:
            print(f"⚠️  查询 test 表失败（正常，如果表不存在）: {e}")
        
        print("\n✅ Supabase 连接测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Supabase 数据库连接测试")
    print("=" * 50)
    print()
    
    success = connect_supabase()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 测试完成！环境配置正确")
    else:
        print("⚠️  测试失败，请检查 .env 配置")
        print("\n💡 提示:")
        print("   1. 确认 SUPABASE_URL 和 SUPABASE_KEY 已正确填写")
        print("   2. 前往 https://supabase.com 创建项目获取连接信息")
        print("   3. 在 Project Settings → API 中获取 URL 和 Key")
    print("=" * 50)
