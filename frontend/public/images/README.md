# 流程图设置说明

## 📸 添加流程图图片

请将你提供的手机搜索流程图保存为：`phone-search-flowchart.png`

### 流程图内容预览
你的流程图应该显示以下搜索流程：
```
搜索"phone" → 瀏覽20個商品 → 點擊"iPhone 14" → 輸入"iPhone" → 瀏覽10個商品 → 刷新頁面 → 點擊"iPhone 16" → 跳轉購買
```

### 最新更新
已使用最新的中文流程図替换所有产品的流程图展示。

### 使用位置
此流程图将在以下地方显示：
- 手机产品详情页面的用户评测区域
- AI意图识别响应区域的图标
- 所有相关商品的流程展示

### 技术说明
所有相关的代码文件已经更新为使用 `/images/phone-search-flowchart.png` 路径，包括：
- `src/data/phone-threads.ts` - 手机产品数据
- `src/data/threads.ts` - 原始产品数据（备用）
- `src/components/EcommerceSearch.tsx` - 主搜索组件

只需将图片文件放在正确位置即可自动生效！
