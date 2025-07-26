# PostgreSQL Dialog 表管理工具

这个目录包含用于创建和管理 PostgreSQL 中 `dialog` 表的 Python 脚本。该表用于存储用户的历史操作记录。

## 文件说明

- `create_dialog_table.py` - 创建 dialog 表的脚本
- `dialog_operations.py` - dialog 表的 CRUD 操作示例（已废弃，推荐使用新版本）
- `dialog_crud.py` - 专门针对 dialog 表的四个核心 CRUD 操作
- `db_manager.py` - 完整的数据库管理器，包含连接池和高级 CRUD 功能
- `advanced_crud.py` - 高级 CRUD 操作，包含复杂查询、数据分析、导入导出等
- `config.py` - 配置管理模块，统一管理环境变量和数据库配置
- `example_usage.py` - 完整的使用示例，展示所有功能
- `test_dialog_crud.py` - 单元测试文件，验证所有功能
- `.env.example` - 环境变量配置模板
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

### 1. 配置环境变量

复制环境变量模板并配置：

```bash
cd /home/scruel/reso/tools/psql
cp .env.example .env
# 编辑 .env 文件，填入实际的数据库连接信息
```

### 2. 创建表

```bash
python create_dialog_table.py
```

### 3. 运行示例

```bash
# 查看完整功能演示
python example_usage.py
```

### 4. 运行测试

```bash
# 验证所有功能是否正常
python test_dialog_crud.py
```

这个脚本会：
- 创建 `dialog` 表
- 创建必要的索引
- 创建自动更新 `updated_at` 字段的触发器
- 显示表结构信息

### 2. 使用核心 CRUD 操作

```bash
python dialog_crud.py
```

这个脚本提供四个核心操作：
- 录入 dialog 记录
- 清空 dialog 表
- 获取所有的 message
- 获取最后一行 intend_title 及 intend_attrs

### 3. 使用完整数据库管理器

```bash
python db_manager.py
```

这个脚本提供完整的数据库管理功能：
- 连接池管理
- 事务处理
- 完整的 CRUD 操作
- 批量操作
- 统计信息

### 4. 使用高级 CRUD 操作

```bash
python advanced_crud.py
```

这个脚本提供高级功能：
- 按日期范围搜索
- 按意图搜索
- 按属性搜索
- 对话分析
- 数据导入导出
- 重复记录检测

### 5. 在代码中使用

#### 使用核心 CRUD 操作

```python
from dialog_crud import DialogCRUD

# 创建 CRUD 实例
crude = DialogCRUD()

# 录入 dialog
success = crud.insert_dialog(
    message="用户的问题",
    reply="系统的回答",
    intend_title="问答",
    intend_attrs={"category": "general"},
    intend_stop_words=["的", "了", "吗"]
)

# 获取所有消息
messages = crud.get_all_messages()

# 获取最后一行意图信息
last_intent = crud.get_last_intent_info()

# 清空表（谨慎使用）
# crud.clear_dialog()
```

#### 使用完整数据库管理器

```python
from db_manager import DatabaseManager, DialogCRUD

# 创建数据库管理器
db_manager = DatabaseManager()
dialog_crud = DialogCRUD(db_manager)

# 创建记录
success = dialog_crud.create(
    uuid_str="your-uuid",
    message="用户消息",
    reply="系统回复",
    intend_title="意图标题",
    intend_attrs={"confidence": 0.95},
    intend_stop_words=["停用词"]
)

# 读取记录
record = dialog_crud.read_by_uuid("your-uuid")

# 更新记录
dialog_crud.update("your-uuid", message="更新的消息")

# 删除记录
dialog_crud.delete("your-uuid")

# 批量创建
records = [{"uuid": "uuid1", "message": "msg1"}, ...]
dialog_crud.batch_create(records)

# 关闭连接池
db_manager.close_pool()
```

## 环境配置

### 1. 依赖要求

确保已安装以下 Python 包：

```bash
pip install psycopg2-binary python-dotenv
```

或者在项目根目录运行：

```bash
pip install -r requirements.txt
```

## 项目结构

```
tools/psql/
├── create_dialog_table.py    # 创建表脚本
├── dialog_crud.py            # 基础 CRUD 操作
├── db_manager.py             # 数据库管理器
├── advanced_crud.py          # 高级 CRUD 操作
├── config.py                 # 配置管理
├── example_usage.py          # 使用示例
├── test_dialog_crud.py       # 单元测试
├── .env.example              # 环境变量模板
└── README.md                 # 说明文档
```

### 2. 环境变量配置

在项目根目录创建 `.env` 文件，或设置以下环境变量：

```bash
# PostgreSQL 数据库配置
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_NAME=postgres
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=password
POSTGRESQL_MIN_CONN=1
POSTGRESQL_MAX_CONN=10
POSTGRESQL_TIMEOUT=30

# 应用配置（可选）
DEBUG=False
LOG_LEVEL=INFO
MAX_RECORDS_PER_QUERY=1000
DEFAULT_PAGE_SIZE=50
```

可以使用 `config.py` 生成配置模板：

```bash
python config.py
```

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
