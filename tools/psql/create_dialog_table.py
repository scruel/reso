#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建用户历史操作表 dialog

该脚本用于在 PostgreSQL 数据库中创建 dialog 表，用于存储用户的历史操作记录。

表结构:
- uuid: 唯一标识符
- message: 用户消息
- reply: 系统回复
- intend_title: 意图标题
- intend_attrs: 意图属性
- intend_stop_words: 意图停用词
"""

from dotenv import load_dotenv
import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

db_config = {
    'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
    'port': os.getenv('POSTGRESQL_PORT', '5432'),
    'database': os.getenv('POSTGRESQL_NAME', 'postgres'),
    'user': os.getenv('POSTGRESQL_USER', 'postgres'),
    'password': os.getenv('POSTGRESQL_PASSWORD', 'password')
}

def create_dialog_table():
    """
    创建 dialog 表
    """
    # 数据库连接配置
    # 可以通过环境变量配置，或者直接修改这些值
    
    try:
        # 连接数据库
        print(f"正在连接数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        conn = psycopg2.connect(**db_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 创建表的 SQL 语句
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS dialog (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) NOT NULL UNIQUE,
            message TEXT,
            reply TEXT,
            intend_title VARCHAR(255),
            intend_attrs JSONB,
            intend_stop_words TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 执行创建表语句
        print("正在创建 dialog 表...")
        cursor.execute(create_table_sql)
        
        # 创建索引以提高查询性能
        index_sql = """
        CREATE INDEX IF NOT EXISTS idx_dialog_uuid ON dialog(uuid);
        CREATE INDEX IF NOT EXISTS idx_dialog_created_at ON dialog(created_at);
        CREATE INDEX IF NOT EXISTS idx_dialog_intend_title ON dialog(intend_title);
        """
        
        print("正在创建索引...")
        cursor.execute(index_sql)
        
        # 创建更新时间触发器
        trigger_sql = """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        DROP TRIGGER IF EXISTS update_dialog_updated_at ON dialog;
        CREATE TRIGGER update_dialog_updated_at
            BEFORE UPDATE ON dialog
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
        
        print("正在创建更新时间触发器...")
        cursor.execute(trigger_sql)
        
        print("✅ dialog 表创建成功！")
        print("\n表结构:")
        print("- id: 自增主键")
        print("- uuid: 唯一标识符 (VARCHAR(36), UNIQUE)")
        print("- message: 用户消息 (TEXT)")
        print("- reply: 系统回复 (TEXT)")
        print("- intend_title: 意图标题 (VARCHAR(255))")
        print("- intend_attrs: 意图属性 (JSONB)")
        print("- intend_stop_words: 意图停用词 (TEXT[])")
        print("- created_at: 创建时间 (TIMESTAMP WITH TIME ZONE)")
        print("- updated_at: 更新时间 (TIMESTAMP WITH TIME ZONE)")
        
    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("数据库连接已关闭")
    
    return True


def show_table_info():
    """
    显示表信息
    """
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'dialog'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        if columns:
            print("\n📋 dialog 表结构:")
            print("-" * 60)
            print(f"{'字段名':<20} {'类型':<15} {'可空':<8} {'默认值':<15}")
            print("-" * 60)
            for col in columns:
                nullable = "是" if col[2] == "YES" else "否"
                default = col[3] if col[3] else ""
                print(f"{col[0]:<20} {col[1]:<15} {nullable:<8} {default:<15}")
        else:
            print("❌ dialog 表不存在")
            
    except Exception as e:
        print(f"❌ 查询表信息失败: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    print("🚀 开始创建 dialog 表...")
    print("\n💡 提示: 请确保已设置以下环境变量或修改脚本中的默认值:")
    print("- DB_HOST: 数据库主机地址")
    print("- DB_PORT: 数据库端口")
    print("- DB_NAME: 数据库名称")
    print("- DB_USER: 数据库用户名")
    print("- DB_PASSWORD: 数据库密码")
    print()
    
    if create_dialog_table():
        show_table_info()
    else:
        print("❌ 表创建失败")
