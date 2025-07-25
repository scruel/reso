
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
```
# 复制环境变量模板
cp .env.template .env
```


### 3. 运行系统
```bash
# 真实AI模式
python real_ai_test.py
