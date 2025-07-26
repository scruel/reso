#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例

展示如何使用 dialog 表的各种 CRUD 操作。
"""

from dotenv import load_dotenv
import uuid
import json
from datetime import datetime

# 导入我们的模块
from dialog_crud import DialogCRUD
from db_manager import DatabaseManager, DialogCRUD as AdvancedDialogCRUD
from advanced_crud import AdvancedDialogCRUD as SuperAdvancedDialogCRUD
from config import get_config

# 加载环境变量
load_dotenv()

def example_basic_crud():
    """基础 CRUD 操作示例"""
    print("\n" + "="*50)
    print("基础 CRUD 操作示例")
    print("="*50)
    
    # 创建 CRUD 实例
    crud = DialogCRUD()
    
    try:
        # 1. 录入对话记录
        print("\n1. 录入对话记录...")
        
        dialog_uuid = str(uuid.uuid4())
        success = crud.insert_dialog(
            message="你好，我想了解一下你们的AI助手功能",
            reply="您好！我们的AI助手具有多种功能，包括自然语言处理、智能问答、任务自动化等。您想了解哪个方面呢？",
            intend_title="AI功能咨询",
            intend_attrs={
                "confidence": 0.95,
                "category": "product_inquiry",
                "user_type": "new_user",
                "priority": "high"
            },
            intend_stop_words=["的", "了", "你们", "一下"],
            dialog_uuid=dialog_uuid
        )
        
        if success:
            print(f"✅ 成功录入对话记录，UUID: {dialog_uuid}")
        else:
            print("❌ 录入失败")
            return
        
        # 2. 获取所有消息
        print("\n2. 获取所有消息...")
        messages = crud.get_all_messages()
        print(f"📝 共获取到 {len(messages)} 条消息:")
        for i, msg in enumerate(messages[-3:], 1):  # 只显示最后3条
            print(f"   {i}. [{msg['created_at']}] {msg['message'][:50]}...")
        
        # 3. 获取最后一行意图信息
        print("\n3. 获取最后一行意图信息...")
        last_intent = crud.get_last_intent_info()
        if last_intent:
            print(f"🎯 最后一条记录的意图信息:")
            print(f"   意图标题: {last_intent['intend_title']}")
            print(f"   意图属性: {json.dumps(last_intent['intend_attrs'], ensure_ascii=False, indent=2)}")
            print(f"   创建时间: {last_intent['created_at']}")
        
        # 4. 获取表信息
        print("\n4. 获取表统计信息...")
        table_info = crud.get_table_info()
        print(f"📊 表统计信息:")
        print(f"   总记录数: {table_info.get('total_records', 0)}")
        print(f"   有消息的记录: {table_info.get('records_with_message', 0)}")
        print(f"   有意图的记录: {table_info.get('records_with_intent', 0)}")
        print(f"   最早记录: {table_info.get('earliest_record')}")
        print(f"   最新记录: {table_info.get('latest_record')}")
        
    except Exception as e:
        print(f"❌ 操作过程中出错: {e}")

def example_advanced_crud():
    """高级 CRUD 操作示例"""
    print("\n" + "="*50)
    print("高级 CRUD 操作示例")
    print("="*50)
    
    # 创建数据库管理器和高级 CRUD
    db_manager = DatabaseManager()
    advanced_crud = AdvancedDialogCRUD(db_manager)
    
    try:
        # 1. 批量创建记录
        print("\n1. 批量创建记录...")
        batch_records = [
            {
                'uuid': str(uuid.uuid4()),
                'message': '如何使用语音识别功能？',
                'reply': '语音识别功能可以通过点击麦克风图标激活...',
                'intend_title': '语音功能咨询',
                'intend_attrs': {'confidence': 0.92, 'category': 'voice_feature'}
            },
            {
                'uuid': str(uuid.uuid4()),
                'message': '支持哪些编程语言？',
                'reply': '我们支持Python、JavaScript、Java、C++等多种编程语言...',
                'intend_title': '技术支持',
                'intend_attrs': {'confidence': 0.88, 'category': 'technical_support'}
            },
            {
                'uuid': str(uuid.uuid4()),
                'message': '价格方案是怎样的？',
                'reply': '我们提供免费版、专业版和企业版三种方案...',
                'intend_title': '价格咨询',
                'intend_attrs': {'confidence': 0.94, 'category': 'pricing'}
            }
        ]
        
        created_count = advanced_crud.batch_create(batch_records)
        print(f"✅ 批量创建了 {created_count} 条记录")
        
        # 2. 按意图搜索
        print("\n2. 按意图搜索...")
        intent_results = advanced_crud.search_by_intent('咨询')
        print(f"🔍 找到 {len(intent_results)} 条包含'咨询'的记录")
        for result in intent_results[:2]:  # 只显示前2条
            print(f"   - {result['intend_title']}: {result['message'][:30]}...")
        
        # 3. 按属性搜索
        print("\n3. 按属性搜索...")
        attr_results = advanced_crud.search_by_attributes('category', 'technical_support')
        print(f"🔍 找到 {len(attr_results)} 条技术支持类别的记录")
        
        # 4. 获取统计信息
        print("\n4. 获取统计信息...")
        stats = advanced_crud.get_statistics()
        print(f"📊 数据库统计:")
        print(f"   总记录数: {stats.get('total_records', 0)}")
        print(f"   最新记录: {stats.get('latest_record')}")
        top_intents = stats.get('top_intents', [])
        if top_intents:
            print(f"   热门意图: {top_intents[0]['title']} ({top_intents[0]['count']}次)")
        
    except Exception as e:
        print(f"❌ 高级操作过程中出错: {e}")
    finally:
        # 关闭连接池
        db_manager.close_pool()

def example_super_advanced_crud():
    """超级高级 CRUD 操作示例"""
    print("\n" + "="*50)
    print("超级高级 CRUD 操作示例")
    print("="*50)
    
    # 创建数据库管理器和超级高级 CRUD
    db_manager = DatabaseManager()
    super_crud = SuperAdvancedDialogCRUD(db_manager)
    
    try:
        # 1. 获取最近对话
        print("\n1. 获取最近对话...")
        recent_conversations = super_crud.get_recent_conversations(hours=24, limit=5)
        print(f"💬 最近24小时内有 {len(recent_conversations)} 条对话")
        
        # 2. 获取对话分析
        print("\n2. 获取对话分析...")
        analytics = super_crud.get_conversation_analytics(days=7)
        print(f"📈 过去7天的对话分析:")
        print(f"   总对话数: {analytics.get('total_conversations', 0)}")
        print(f"   平均消息长度: {analytics.get('avg_message_length', 0)} 字符")
        print(f"   平均回复长度: {analytics.get('avg_reply_length', 0)} 字符")
        
        popular_intents = analytics.get('popular_intents', [])
        if popular_intents:
            print(f"   热门意图:")
            for intent in popular_intents[:3]:  # 显示前3个
                print(f"     - {intent['intent']}: {intent['count']}次")
        
        # 3. 检测重复记录
        print("\n3. 检测重复记录...")
        duplicates = super_crud.duplicate_detection()
        print(f"🔍 发现 {len(duplicates)} 组重复记录")
        
        # 4. 导出数据示例（注释掉以避免创建文件）
        print("\n4. 数据导出功能演示...")
        print("   💾 可以导出数据到 CSV 文件")
        print("   📥 可以从 CSV 文件导入数据")
        print("   🧹 可以清理超过指定天数的旧记录")
        
        # export_success = super_crud.export_to_csv('/tmp/dialog_export.csv')
        # print(f"   导出结果: {'成功' if export_success else '失败'}")
        
    except Exception as e:
        print(f"❌ 超级高级操作过程中出错: {e}")
    finally:
        # 关闭连接池
        db_manager.close_pool()

def example_config_usage():
    """配置使用示例"""
    print("\n" + "="*50)
    print("配置管理示例")
    print("="*50)
    
    try:
        # 获取配置
        config = get_config()
        
        # 验证配置
        print("\n1. 验证配置...")
        is_valid = config.validate_config()
        print(f"✅ 配置验证: {'通过' if is_valid else '失败'}")
        
        # 获取数据库配置
        print("\n2. 数据库配置信息...")
        db_config = config.get_database_config()
        print(f"🗄️  数据库主机: {db_config['host']}:{db_config['port']}")
        print(f"🗄️  数据库名称: {db_config['database']}")
        print(f"🗄️  连接池大小: {db_config['minconn']}-{db_config['maxconn']}")
        
        # 获取应用配置
        print("\n3. 应用配置信息...")
        app_config = config.get_app_config()
        print(f"⚙️  调试模式: {app_config['debug']}")
        print(f"⚙️  日志级别: {app_config['log_level']}")
        print(f"⚙️  最大查询记录数: {app_config['max_records_per_query']}")
        
    except Exception as e:
        print(f"❌ 配置操作过程中出错: {e}")

def main():
    """主函数"""
    print("🚀 PostgreSQL Dialog 表 CRUD 操作完整示例")
    print("=" * 60)
    
    print("\n💡 提示: 请确保已设置环境变量并创建了 dialog 表")
    print("💡 如果还没有创建表，请先运行: python create_dialog_table.py")
    
    try:
        # 1. 配置管理示例
        example_config_usage()
        
        # 2. 基础 CRUD 操作
        example_basic_crud()
        
        # 3. 高级 CRUD 操作
        example_advanced_crud()
        
        # 4. 超级高级 CRUD 操作
        example_super_advanced_crud()
        
        print("\n" + "="*60)
        print("✅ 所有示例演示完成！")
        print("\n📚 更多功能请参考各个模块的文档和源代码")
        print("📁 相关文件:")
        print("   - dialog_crud.py: 基础 CRUD 操作")
        print("   - db_manager.py: 数据库管理器")
        print("   - advanced_crud.py: 高级 CRUD 操作")
        print("   - config.py: 配置管理")
        print("   - README.md: 详细说明文档")
        
    except Exception as e:
        print(f"\n❌ 示例执行过程中出错: {e}")
        print("\n🔧 故障排除建议:")
        print("   1. 检查数据库连接配置")
        print("   2. 确保已安装所需依赖: pip install psycopg2-binary python-dotenv")
        print("   3. 确保已创建 dialog 表")
        print("   4. 检查环境变量设置")

if __name__ == "__main__":
    main()