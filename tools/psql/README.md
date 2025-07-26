# PostgreSQL Dialog 表管理工具

这个目录包含用于创建和管理 PostgreSQL 中 `dialog` 表的 Python 脚本。该表用于存储用户的历史操作记录。

## 文件说明

- `create_dialog_table.py` - 创建 dialog 表的脚本
- `dialog_operations.py` - dialog 表的 CRUD 操作示例
- `README.md` - 本说明文件

## 表结构

`dialog` 表包含以下字段：

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | SERIAL | 自增主键 | PRIMARY KEY |
| uuid | VARCHAR(36) | 唯一标识符 | NOT NULL, UNIQUE |
| message | TEXT | 用户消息 | - |
| reply | TEXT | 系统回复 | - |
| intend_title | VARCHAR(255) | 意图标题 | - |
| intend_attrs | JSONB | 意图属性 | - |
| intend_stop_words | TEXT[] | 意图停用词数组 | - |
| created_at | TIMESTAMP WITH TIME ZONE | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | 更新时间 | DEFAULT CURRENT_TIMESTAMP |

## 使用方法

### 1. 创建表

```bash
cd /home/scruel/reso/tools/psql
python create_dialog_table.py
```

这个脚本会：
- 创建 `dialog` 表
- 创建必要的索引
- 创建自动更新 `updated_at` 字段的触发器
- 显示表结构信息

### 2. 使用 CRUD 操作

```bash
python dialog_operations.py
```

这个脚本包含一个演示程序，展示如何：
- 插入新的对话记录
- 根据 UUID 查询记录
- 更新现有记录
- 删除记录
- 列出所有记录

### 3. 在代码中使用

```python
from dialog_operations import DialogManager

# 创建管理器实例
manager = DialogManager()

# 插入新记录
uuid = manager.insert_dialog(
    message="用户的问题",
    reply="系统的回答",
    intend_title="问答",
    intend_attrs={"category": "general"},
    intend_stop_words=["的", "了", "吗"]
)

# 查询记录
dialog = manager.get_dialog_by_uuid(uuid)

# 更新记录
manager.update_dialog(uuid, reply="更新后的回答")

# 删除记录
manager.delete_dialog(uuid)

# 列出记录
dialogs = manager.list_dialogs(limit=10)
```

## 依赖要求

确保已安装以下 Python 包：

```bash
pip install psycopg2-binary
```

这个依赖已经包含在 `tools/requirements.txt` 中。

## 注意事项

1. **数据库权限**：确保数据库用户有创建表、索引和触发器的权限
2. **UUID 唯一性**：每个对话记录的 UUID 必须唯一
3. **JSONB 类型**：`intend_attrs` 字段使用 JSONB 类型，可以存储结构化的 JSON 数据
4. **数组类型**：`intend_stop_words` 字段使用 PostgreSQL 的数组类型
5. **时区**：时间戳字段包含时区信息

## 索引说明

为了提高查询性能，脚本会自动创建以下索引：

- `idx_dialog_uuid`：UUID 字段索引（用于快速查找）
- `idx_dialog_created_at`：创建时间索引（用于时间范围查询）
- `idx_dialog_intend_title`：意图标题索引（用于按意图分类查询）

## 触发器说明

脚本会创建一个触发器 `update_dialog_updated_at`，在每次更新记录时自动更新 `updated_at` 字段为当前时间。

## 故障排除

### 连接失败
- 检查数据库服务是否运行
- 验证连接参数是否正确
- 确认网络连接和防火墙设置

### 权限错误
- 确保数据库用户有足够的权限
- 检查数据库和表的访问权限

### 依赖问题
- 确保已安装 `psycopg2-binary`
- 检查 Python 版本兼容性

## 扩展功能

可以根据需要扩展以下功能：

1. **分页查询**：已在 `list_dialogs` 方法中实现
2. **条件查询**：可以添加按意图、时间范围等条件查询的方法
3. **批量操作**：可以添加批量插入、更新、删除的方法
4. **数据导出**：可以添加导出为 CSV、JSON 等格式的功能
5. **数据统计**：可以添加统计分析功能
