#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog 表 CRUD 操作

专门针对 dialog 表的四个核心操作：
1. 录入 dialog
2. 清空 dialog
3. 获取所有的 message
4. 获取最后一行 intend_title 及 intend_attrs

使用环境变量配置数据库连接。
"""

from dotenv import load_dotenv
import psycopg2
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
db_config = {
    'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
    'port': os.getenv('POSTGRESQL_PORT', '5432'),
    'database': os.getenv('POSTGRESQL_NAME', 'postgres'),
    'user': os.getenv('POSTGRESQL_USER', 'postgres'),
    'password': os.getenv('POSTGRESQL_PASSWORD', 'password')
}

class DialogCRUD:
    """Dialog 表的 CRUD 操作类"""
    
    def __init__(self):
        """初始化数据库连接配置"""
        self.db_config = db_config
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def insert_dialog(self, message: str, reply: str, intend_title: str = None, 
                     intend_attrs: List[str] = None, 
                     intend_stop_words: List[str] = None,
                     dialog_uuid: str = None) -> bool:
        """
        录入 dialog 记录
        
        Args:
            message: 用户消息
            reply: 系统回复
            intend_title: 意图标题
            intend_attrs: 意图属性（字典格式）
            intend_stop_words: 意图停用词列表
            dialog_uuid: 对话UUID，如果不提供则自动生成
            
        Returns:
            bool: 插入是否成功
        """
        conn = None
        cursor = None
        
        try:
            # 如果没有提供UUID，则自动生成
            if not dialog_uuid:
                dialog_uuid = str(uuid.uuid4())
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 准备插入语句
            insert_sql = """
                INSERT INTO dialog (uuid, message, reply, intend_title, intend_attrs, intend_stop_words)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # 处理 JSON 数据
            
            # 执行插入
            cursor.execute(insert_sql, (
                dialog_uuid,
                message,
                reply,
                intend_title,
                intend_attrs,
                intend_stop_words
            ))
            
            conn.commit()
            logger.info(f"成功录入 dialog 记录，UUID: {dialog_uuid}")
            return True
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"录入 dialog 失败: {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"录入 dialog 时发生未知错误: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def clear_dialog(self) -> bool:
        """
        清空 dialog 表中的所有记录
        
        Returns:
            bool: 清空是否成功
        """
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 执行清空操作，使用 TRUNCATE 可以重置自增 ID
            cursor.execute("TRUNCATE TABLE dialog RESTART IDENTITY")
            deleted_count = cursor.rowcount
            
            conn.commit()
            logger.info(f"成功清空 dialog 表，删除了 {deleted_count} 条记录")
            return True
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"清空 dialog 表失败: {e}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"清空 dialog 表时发生未知错误: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """
        获取所有的 message
        
        Returns:
            List[Dict]: 包含所有消息的列表，每个元素包含 id, uuid, message, created_at
        """
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 查询所有消息
            select_sql = """
                SELECT id, uuid, message, created_at
                FROM dialog
                WHERE message IS NOT NULL
                ORDER BY created_at ASC
            """
            
            cursor.execute(select_sql)
            results = cursor.fetchall()
            
            # 转换为字典列表
            messages = []
            for row in results:
                messages.append(row[2])
                # messages.append({
                #     'id': row[0],
                #     'uuid': row[1],
                #     'message': row[2],
                #     'created_at': row[3]
                # })
            
            logger.info(f"成功获取 {len(messages)} 条消息记录")
            return messages
            
        except psycopg2.Error as e:
            logger.error(f"获取所有消息失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取所有消息时发生未知错误: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_last_intent_info(self) -> Optional[Dict[str, Any]]:
        """
        获取最后一行的 intend_title 及 intend_attrs
        
        Returns:
            Optional[Dict]: 包含最后一条记录的意图信息，格式为：
            {
                'id': int,
                'uuid': str,
                'intend_title': str,
                'intend_attrs': dict,
                'created_at': datetime
            }
            如果没有记录则返回 None
        """
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 查询最后一条记录的意图信息
            select_sql = """
                SELECT id, uuid, intend_title, intend_attrs, intend_stop_words, created_at
                FROM dialog
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            cursor.execute(select_sql)
            result = cursor.fetchone()
            
            if result:
                # 解析 JSON 属性
                intent_info = {
                    'id': result[0],
                    'uuid': result[1],
                    'intend_title': result[2],
                    'intend_attrs': result[3],
                    'intend_stop_words': result[4],
                    'created_at': result[5]
                }
                logger.info(f"成功获取最后一条记录的意图信息，ID: {result[0]}")
                return intent_info
            else:
                logger.info("dialog 表中没有记录")
                return None
                
        except psycopg2.Error as e:
            logger.error(f"获取最后一条意图信息失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取最后一条意图信息时发生未知错误: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        获取 dialog 表的基本信息
        
        Returns:
            Dict: 包含表的统计信息
        """
        conn = None
        cursor = None
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 获取总记录数
            cursor.execute("SELECT COUNT(*) FROM dialog")
            total_count = cursor.fetchone()[0]
            
            # 获取有消息的记录数
            cursor.execute("SELECT COUNT(*) FROM dialog WHERE message IS NOT NULL")
            message_count = cursor.fetchone()[0]
            
            # 获取有意图标题的记录数
            cursor.execute("SELECT COUNT(*) FROM dialog WHERE intend_title IS NOT NULL")
            intent_count = cursor.fetchone()[0]
            
            # 获取最早和最晚的记录时间
            cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM dialog")
            time_range = cursor.fetchone()
            
            info = {
                'total_records': total_count,
                'records_with_message': message_count,
                'records_with_intent': intent_count,
                'earliest_record': time_range[0],
                'latest_record': time_range[1]
            }
            
            return info
            
        except psycopg2.Error as e:
            logger.error(f"获取表信息失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"获取表信息时发生未知错误: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


def demo_dialog_crud():
    """演示 Dialog CRUD 操作"""
    print("🚀 开始演示 Dialog CRUD 操作...")
    
    # 创建 CRUD 实例
    crud = DialogCRUD()

    try:
        # 1. 获取表信息
        print("\n1. 获取表信息...")
        table_info = crud.get_table_info()
        print(f"表信息: {table_info}")
        
        # 2. 录入 dialog 记录
        print("\n2. 录入 dialog 记录...")
        
        # 录入第一条记录
        success1 = crud.insert_dialog(
            message="你好，我想了解你们的产品",
            reply="您好！很高兴为您介绍我们的产品。请问您对哪方面比较感兴趣？",
            intend_title="产品咨询",
            intend_attrs=["属性1", "属性1", "属性1"],
            intend_stop_words=["的", "了", "你们"]
        )
        print(f"第一条记录录入结果: {'成功' if success1 else '失败'}")
        
        # 录入第二条记录
        success2 = crud.insert_dialog(
            message="价格怎么样？",
            reply="我们的产品价格非常有竞争力，具体价格会根据您的需求定制。",
            intend_title="价格询问",
            intend_attrs=["属性1", "属性1", "属性1"],
        )
        print(f"第二条记录录入结果: {'成功' if success2 else '失败'}")
        
        # 录入第三条记录
        success3 = crud.insert_dialog(
            message="谢谢你的介绍",
            reply="不客气！如果您还有其他问题，随时可以联系我们。",
            intend_title="感谢",
            intend_attrs=["属性1", "属性1", "属性1"],
        )
        print(f"第三条记录录入结果: {'成功' if success3 else '失败'}")
        
        # 3. 获取所有消息
        print("\n3. 获取所有消息...")
        all_messages = crud.get_all_messages()
        print(f"共获取到 {len(all_messages)} 条消息:")
        for i, msg in enumerate(all_messages, 1):
            print(msg)
        
        # 4. 获取最后一行的意图信息
        print("\n4. 获取最后一行的意图信息...")
        last_intent = crud.get_last_intent_info()
        if last_intent:
            print(f"最后一条记录的意图信息:")
            print(f"  ID: {last_intent['id']}")
            print(f"  UUID: {last_intent['uuid']}")
            print(f"  意图标题: {last_intent['intend_title']}")
            print(f"  意图属性: {last_intent['intend_attrs']}")
            print(f"  创建时间: {last_intent['created_at']}")
        else:
            print("没有找到记录")
        
        # 5. 再次获取表信息
        print("\n5. 更新后的表信息...")
        updated_info = crud.get_table_info()
        print(f"更新后的表信息: {updated_info}")
        
        # 6. 演示清空操作（可选，注释掉以保留数据）
        print("\n6. 清空操作演示（已注释，如需测试请取消注释）")
        clear_success = crud.clear_dialog()
        print(f"清空结果: {'成功' if clear_success else '失败'}")
        
        if clear_success:
            final_info = crud.get_table_info()
            print(f"清空后的表信息: {final_info}")
        
    except Exception as e:
        logger.error(f"演示过程中出错: {e}")
    
    print("\n✅ Dialog CRUD 操作演示完成！")


if __name__ == "__main__":
    print("💡 提示: 请确保已设置以下环境变量:")
    print("- POSTGRESQL_HOST: 数据库主机地址")
    print("- POSTGRESQL_PORT: 数据库端口")
    print("- POSTGRESQL_NAME: 数据库名称")
    print("- POSTGRESQL_USER: 数据库用户名")
    print("- POSTGRESQL_PASSWORD: 数据库密码")
    print("\n💡 请确保已运行 create_dialog_table.py 创建了 dialog 表")
    print()
    
    demo_dialog_crud()
