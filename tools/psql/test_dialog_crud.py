#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件

用于测试 dialog 表的各种 CRUD 操作功能。
"""

import unittest
import uuid
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 导入测试模块
from dialog_crud import DialogCRUD
from db_manager import DatabaseManager, DialogCRUD as AdvancedDialogCRUD
from advanced_crud import AdvancedDialogCRUD as SuperAdvancedDialogCRUD
from config import get_config

# 加载环境变量
load_dotenv()

class TestDialogCRUD(unittest.TestCase):
    """基础 CRUD 操作测试"""
    
    def setUp(self):
        """测试前准备"""
        self.crud = DialogCRUD()
        self.test_uuid = str(uuid.uuid4())
        
    def test_insert_dialog(self):
        """测试录入对话"""
        success = self.crud.insert_dialog(
            message="测试消息",
            reply="测试回复",
            intend_title="测试意图",
            intend_attrs={"test": True, "confidence": 0.9},
            intend_stop_words=["测试", "的"],
            dialog_uuid=self.test_uuid
        )
        self.assertTrue(success, "录入对话应该成功")
        
    def test_get_all_messages(self):
        """测试获取所有消息"""
        # 先插入一条记录
        self.crud.insert_dialog(
            message="测试获取消息",
            reply="测试回复",
            dialog_uuid=str(uuid.uuid4())
        )
        
        messages = self.crud.get_all_messages()
        self.assertIsInstance(messages, list, "应该返回列表")
        self.assertGreater(len(messages), 0, "应该有至少一条消息")
        
        # 检查消息格式
        if messages:
            msg = messages[0]
            self.assertIn('message', msg, "消息应该包含 message 字段")
            self.assertIn('created_at', msg, "消息应该包含 created_at 字段")
            
    def test_get_last_intent_info(self):
        """测试获取最后一行意图信息"""
        # 先插入一条记录
        test_title = "测试最后意图"
        test_attrs = {"test_last": True, "priority": "high"}
        
        self.crud.insert_dialog(
            message="测试最后意图消息",
            reply="测试回复",
            intend_title=test_title,
            intend_attrs=test_attrs,
            dialog_uuid=str(uuid.uuid4())
        )
        
        last_intent = self.crud.get_last_intent_info()
        self.assertIsNotNone(last_intent, "应该返回最后一条意图信息")
        self.assertEqual(last_intent['intend_title'], test_title, "意图标题应该匹配")
        self.assertEqual(last_intent['intend_attrs'], test_attrs, "意图属性应该匹配")
        
    def test_get_table_info(self):
        """测试获取表信息"""
        table_info = self.crud.get_table_info()
        self.assertIsInstance(table_info, dict, "应该返回字典")
        self.assertIn('total_records', table_info, "应该包含总记录数")
        self.assertIsInstance(table_info['total_records'], int, "总记录数应该是整数")

class TestAdvancedDialogCRUD(unittest.TestCase):
    """高级 CRUD 操作测试"""
    
    def setUp(self):
        """测试前准备"""
        self.db_manager = DatabaseManager()
        self.crud = AdvancedDialogCRUD(self.db_manager)
        
    def tearDown(self):
        """测试后清理"""
        self.db_manager.close_pool()
        
    def test_batch_create(self):
        """测试批量创建"""
        records = [
            {
                'uuid': str(uuid.uuid4()),
                'message': '批量测试消息1',
                'reply': '批量测试回复1',
                'intend_title': '批量测试意图1'
            },
            {
                'uuid': str(uuid.uuid4()),
                'message': '批量测试消息2',
                'reply': '批量测试回复2',
                'intend_title': '批量测试意图2'
            }
        ]
        
        created_count = self.crud.batch_create(records)
        self.assertEqual(created_count, 2, "应该创建2条记录")
        
    def test_search_by_intent(self):
        """测试按意图搜索"""
        # 先插入测试数据
        test_intent = "搜索测试意图"
        self.crud.create({
            'uuid': str(uuid.uuid4()),
            'message': '搜索测试消息',
            'reply': '搜索测试回复',
            'intend_title': test_intent
        })
        
        results = self.crud.search_by_intent('搜索测试')
        self.assertIsInstance(results, list, "应该返回列表")
        
        # 检查结果中是否包含我们的测试数据
        found = any(r['intend_title'] == test_intent for r in results)
        self.assertTrue(found, "应该找到测试意图")
        
    def test_get_statistics(self):
        """测试获取统计信息"""
        stats = self.crud.get_statistics()
        self.assertIsInstance(stats, dict, "应该返回字典")
        self.assertIn('total_records', stats, "应该包含总记录数")

class TestSuperAdvancedDialogCRUD(unittest.TestCase):
    """超级高级 CRUD 操作测试"""
    
    def setUp(self):
        """测试前准备"""
        self.db_manager = DatabaseManager()
        self.crud = SuperAdvancedDialogCRUD(self.db_manager)
        
    def tearDown(self):
        """测试后清理"""
        self.db_manager.close_pool()
        
    def test_get_recent_conversations(self):
        """测试获取最近对话"""
        # 先插入一条最近的记录
        self.crud.create({
            'uuid': str(uuid.uuid4()),
            'message': '最近对话测试',
            'reply': '最近对话回复',
            'intend_title': '最近对话意图'
        })
        
        recent = self.crud.get_recent_conversations(hours=24, limit=10)
        self.assertIsInstance(recent, list, "应该返回列表")
        
    def test_get_conversation_analytics(self):
        """测试获取对话分析"""
        analytics = self.crud.get_conversation_analytics(days=7)
        self.assertIsInstance(analytics, dict, "应该返回字典")
        self.assertIn('total_conversations', analytics, "应该包含总对话数")
        
    def test_duplicate_detection(self):
        """测试重复检测"""
        # 插入两条相同的消息
        same_message = "重复检测测试消息"
        for i in range(2):
            self.crud.create({
                'uuid': str(uuid.uuid4()),
                'message': same_message,
                'reply': f'重复检测回复{i}',
                'intend_title': '重复检测意图'
            })
        
        duplicates = self.crud.duplicate_detection()
        self.assertIsInstance(duplicates, list, "应该返回列表")

class TestConfig(unittest.TestCase):
    """配置管理测试"""
    
    def test_get_config(self):
        """测试获取配置"""
        config = get_config()
        self.assertIsNotNone(config, "应该返回配置对象")
        
    def test_validate_config(self):
        """测试配置验证"""
        config = get_config()
        is_valid = config.validate_config()
        self.assertIsInstance(is_valid, bool, "验证结果应该是布尔值")
        
    def test_get_database_config(self):
        """测试获取数据库配置"""
        config = get_config()
        db_config = config.get_database_config()
        self.assertIsInstance(db_config, dict, "应该返回字典")
        self.assertIn('host', db_config, "应该包含主机配置")
        self.assertIn('port', db_config, "应该包含端口配置")
        self.assertIn('database', db_config, "应该包含数据库名配置")

class TestDatabaseConnection(unittest.TestCase):
    """数据库连接测试"""
    
    def test_basic_connection(self):
        """测试基础连接"""
        crud = DialogCRUD()
        # 尝试获取表信息来测试连接
        try:
            table_info = crud.get_table_info()
            self.assertIsInstance(table_info, dict, "连接成功应该返回表信息")
        except Exception as e:
            self.fail(f"数据库连接失败: {e}")
            
    def test_connection_pool(self):
        """测试连接池"""
        db_manager = DatabaseManager()
        try:
            # 测试获取连接
            with db_manager.get_connection() as conn:
                self.assertIsNotNone(conn, "应该能获取到连接")
                
                # 测试执行查询
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 as test")
                    result = cursor.fetchone()
                    self.assertEqual(result[0], 1, "查询应该返回正确结果")
        finally:
            db_manager.close_pool()

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行 PostgreSQL Dialog CRUD 测试")
    print("=" * 60)
    
    # 检查环境变量
    required_vars = ['POSTGRESQL_HOST', 'POSTGRESQL_PORT', 'POSTGRESQL_NAME', 
                    'POSTGRESQL_USER', 'POSTGRESQL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("💡 请确保已设置 .env 文件或环境变量")
        return False
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestConfig,
        TestDatabaseConnection,
        TestDialogCRUD,
        TestAdvancedDialogCRUD,
        TestSuperAdvancedDialogCRUD
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
        print(f"📊 运行了 {result.testsRun} 个测试")
    else:
        print("❌ 部分测试失败")
        print(f"📊 运行了 {result.testsRun} 个测试")
        print(f"❌ 失败: {len(result.failures)} 个")
        print(f"💥 错误: {len(result.errors)} 个")
        
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
                
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)