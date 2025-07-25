# 🤖 多Agent AI推荐系统

基于CAMEL框架的智能油烟机推荐系统，采用层级式多Agent协作架构。

## 🎯 核心功能

- **智能意图理解** - 自然语言需求分析
- **文档内容解析** - 支持文档/链接上传分析  
- **个性化推荐** - 基于用户需求匹配产品
- **质量验证** - 多维度推荐结果检查
- **行为记录** - 用户交互行为分析

## 🏗️ 系统架构

```
用户 → IntentAgent → DocAsAgent → ExecutionAgent → CheckAgent
       (意图理解)   (推荐生成)    (操作执行)      (质量验证)
                      ↕
               BehaviorRecorderAgent
                  (行为记录)
```

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，填入你的API密钥
KIMI_API_KEY=your_kimi_api_key_here
```

### 3. 运行系统
```bash
# 真实AI模式
python real_ai_test.py

# 基础测试模式  
python test_system.py
```

## 🔧 Agent说明

| Agent | 功能 | 技术栈 |
|-------|------|---------|
| **DocAsAgent** | 文档解析 + 产品推荐 | ReAct模式 + 向量匹配 |
| **IntentAgent** | 用户意图理解 | CAMEL + Kimi模型 |
| **ExecutionAgent** | 操作执行 | CAMEL + 智能决策 |
| **CheckAgent** | 质量验证 | CAMEL + 多维评估 |
| **BehaviorRecorderAgent** | 行为分析 | CAMEL + 数据洞察 |

## 💡 使用示例

```
👤 请输入您的需求: 我家厨房8平米，预算3000元，需要静音的油烟机

🤖 AI分析中...
✨ 推荐: 方太CXW-200-EMC2 - 静音大吸力，2999元超值之选！
```

## 📦 依赖要求

- Python 3.11+
- CAMEL AI Framework
- OpenAI兼容API (Kimi)
- aiohttp, pydantic等

## 🔗 相关链接

- [CAMEL Framework](https://github.com/camel-ai/camel)
- [Kimi API](https://platform.moonshot.cn/)

## 📄 License

MIT License 