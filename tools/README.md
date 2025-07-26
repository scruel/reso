# 商品数据导入 PGVector 工具

这个工具用于将 `resource/good` 目录下的商品信息自动导入到 PGVector 数据库中，使用 qwen-embedding 模型进行向量化索引，实现语义化搜索功能。

## 功能特性

- 自动扫描 `resource/good` 目录下的所有商品文件夹
- 读取每个商品的 `clean_data.json` 和 `detail.txt` 文件
- 使用 Qwen 嵌入模型生成商品的语义向量
- 将商品信息和向量存储到 PostgreSQL + PGVector 数据库
- 支持跳过已存在的商品（避免重复导入）
- 完整的日志记录和错误处理

## 数据库表结构

```sql
CREATE TABLE goods (
    id SERIAL PRIMARY KEY,
    good_short_name VARCHAR(255) NOT NULL,
    price VARCHAR(50),
    brand_name VARCHAR(255),
    catagory_full VARCHAR(500),
    sub_catagory VARCHAR(255),
    item_catagory VARCHAR(255),
    pic_url TEXT,
    detail TEXT,
    embedding vector(1536),  -- 向量维度根据模型而定
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 安装依赖

1. 确保已安装 PostgreSQL 和 PGVector 扩展
2. 安装 Python 依赖：

```bash
cd tools
pip install -r requirements.txt
```

## 配置数据库

### 方法1：环境变量

设置以下环境变量：

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=reso
export DB_USER=postgres
export DB_PASSWORD=your_password
```

### 方法2：修改脚本

直接在 `import_goods_to_pgvector.py` 文件中修改 `db_params` 字典：

```python
db_params = {
    'host': 'your_host',
    'port': '5432',
    'database': 'your_database',
    'user': 'your_user',
    'password': 'your_password'
}
```

## 使用方法

```bash
cd tools
python import_goods_to_pgvector.py
```

## 商品数据格式

每个商品应该有一个独立的文件夹，包含以下文件：

### clean_data.json
```json
{
    "good_short_name": "商品短名称",
    "price": "价格",
    "brand_name": "品牌名称",
    "catagory_full": "完整分类路径",
    "sub_catagory": "子分类",
    "item_catagory": "商品分类",
    "pic_url": "图片URL"
}
```

### detail.txt
包含商品的详细描述信息。

## 语义搜索示例

导入完成后，可以使用以下 SQL 进行语义搜索：

```sql
-- 搜索与查询最相似的商品
SELECT 
    good_short_name,
    brand_name,
    price,
    catagory_full,
    1 - (embedding <=> $1) as similarity
FROM goods 
ORDER BY embedding <=> $1 
LIMIT 10;
```

其中 `$1` 是查询文本的嵌入向量。

## 日志文件

脚本运行时会生成 `import_goods.log` 文件，记录详细的执行日志，包括：
- 成功导入的商品
- 跳过的商品（已存在）
- 错误信息
- 统计信息

## 注意事项

1. **模型下载**：首次运行时会自动下载 Qwen 嵌入模型，需要网络连接
2. **内存使用**：模型加载需要一定内存，建议至少 4GB 可用内存
3. **GPU 加速**：如果有 CUDA 环境，会自动使用 GPU 加速
4. **数据库权限**：确保数据库用户有创建表和索引的权限
5. **PGVector 扩展**：确保 PostgreSQL 已安装 pgvector 扩展

## 故障排除

### 常见问题

1. **模型下载失败**
   - 检查网络连接
   - 可能需要配置代理或使用镜像源

2. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证连接参数是否正确
   - 确认防火墙设置

3. **PGVector 扩展未安装**
   ```sql
   CREATE EXTENSION vector;
   ```

4. **内存不足**
   - 关闭其他应用程序释放内存
   - 考虑使用更小的模型

### 查看日志

```bash
tail -f import_goods.log
```

## 扩展功能

可以根据需要扩展脚本功能：

1. **批量处理**：支持分批处理大量商品
2. **增量更新**：检测文件变化，只更新修改过的商品
3. **多模型支持**：支持不同的嵌入模型
4. **API 接口**：提供 REST API 进行搜索
5. **Web 界面**：创建可视化的搜索界面