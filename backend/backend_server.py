#!/usr/bin/env python3
"""
簡化的 FastAPI 後端服務器
支持前端所需的所有API接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

app = FastAPI(
    title="Reso Backend API",
    description="E-commerce search backend API",
    version="1.0.0"
)

# 添加CORS中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境請設置具體域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 數據模型 =====

class Product(BaseModel):
    id: str
    title: str
    price: int
    image: str
    category: str
    categoryColor: Optional[str] = "#6B7280"
    brand: str
    rating: float
    url: str
    flowImage: Optional[str] = None
    author: Optional[str] = None

class LogMessage(BaseModel):
    message: str

class SearchRequest(BaseModel):
    query: str
    userId: str
    sessionId: str

class RecommendationRequest(BaseModel):
    userId: str
    context: str = "homepage"
    limit: int = 10
    productId: Optional[str] = None

# ===== 模擬數據庫 =====

# 商品數據
products_db = [
    Product(
        id="1",
        title="Apple iPhone 15 Pro Max 256GB",
        price=42990,
        image="https://source.unsplash.com/400x400?iphone",
        category="手機",
        categoryColor="#3B82F6",
        brand="Apple",
        rating=4.9,
        url="#",
        flowImage="https://source.unsplash.com/600x300?phone,workflow",
        author="TechReviewer Alex"
    ),
    Product(
        id="2",
        title="Samsung Galaxy S24 Ultra 1TB",
        price=330673,
        image="https://source.unsplash.com/400x400?samsung",
        category="手機",
        categoryColor="#3B82F6",
        brand="Samsung",
        rating=4.8,
        url="#"
    ),
    Product(
        id="3",
        title="Sony WH-1000XM5 無線降噪耳機",
        price=123071,
        image="https://source.unsplash.com/400x400?headphones",
        category="耳機",
        categoryColor="#8B5CF6",
        brand="Sony",
        rating=4.7,
        url="#",
        flowImage="https://source.unsplash.com/600x300?headphones,review",
        author="AudioExpert Sarah"
    ),
    Product(
        id="4",
        title="Dell XPS 13 Plus 觸控筆電",
        price=705027,
        image="https://source.unsplash.com/400x400?laptop",
        category="電腦",
        categoryColor="#10B981",
        brand="Dell",
        rating=4.6,
        url="#",
        flowImage="https://source.unsplash.com/600x300?laptop,review",
        author="TechGuru Mike"
    ),
    Product(
        id="5",
        title="Nintendo Switch OLED 白色主機",
        price=649661,
        image="https://source.unsplash.com/400x400?nintendo",
        category="遊戲",
        categoryColor="#EF4444",
        brand="Nintendo",
        rating=4.5,
        url="#"
    )
]

# 日誌存儲
client_logs = []
search_logs = []
click_logs = []

# ===== API 路由 =====

@app.get("/")
async def root():
    return {"message": "Reso Backend API", "status": "running"}

# 商品相關API
@app.get("/api/products")
async def get_products(q: Optional[str] = None, category: Optional[str] = None, page: int = 1, limit: int = 20):
    """獲取商品列表，支持搜索和分頁"""
    filtered_products = products_db
    
    # 搜索過濾
    if q:
        filtered_products = [
            p for p in filtered_products 
            if q.lower() in p.title.lower() or 
               q.lower() in p.category.lower() or 
               q.lower() in p.brand.lower()
        ]
    
    # 分類過濾
    if category:
        filtered_products = [p for p in filtered_products if p.category == category]
    
    # 分頁
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_products = filtered_products[start_idx:end_idx]
    
    return {
        "success": True,
        "data": paginated_products,
        "total": len(filtered_products),
        "page": page,
        "limit": limit
    }

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """獲取單個商品詳情"""
    for product in products_db:
        if product.id == product_id:
            return {"success": True, "data": product}
    
    raise HTTPException(status_code=404, detail="Product not found")

# 用戶行為追蹤API
@app.post("/api/client-log")
async def log_client_behavior(logs: List[LogMessage]):
    """記錄用戶行為事件"""
    processed_logs = []
    
    for log in logs:
        processed_log = {
            "id": f"{int(datetime.now().timestamp() * 1000)}-{len(client_logs)}",
            "message": log.message,
            "timestamp": datetime.now().isoformat()
        }
        processed_logs.append(processed_log)
        client_logs.append(processed_log)
        
        print(f"📊 {log.message}")
    
    # 保持最新200條記錄
    if len(client_logs) > 200:
        client_logs[:] = client_logs[-200:]
    
    return {
        "success": True,
        "message": f"Logged {len(processed_logs)} client events",
        "count": len(processed_logs)
    }

@app.get("/api/client-log")
async def get_client_logs():
    """獲取用戶行為統計數據"""
    stats = {}
    for log in client_logs:
        log_type = log.get("type", "unknown")
        stats[log_type] = stats.get(log_type, 0) + 1
    
    return {
        "success": True,
        "data": client_logs,
        "total": len(client_logs),
        "stats": stats
    }

# 搜索記錄API
@app.post("/api/log-search")
async def log_search(log_entry: LogMessage):
    """記錄用戶搜索行為"""
    processed_entry = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "message": log_entry.message,
        "timestamp": datetime.now().isoformat()
    }
    
    search_logs.append(processed_entry)
    
    # 保持最新100條記錄
    if len(search_logs) > 100:
        search_logs[:] = search_logs[-100:]
    
    print(f"🔍 {log_entry.message}")
    
    return {
        "success": True,
        "message": "Search logged successfully",
        "logId": processed_entry["id"]
    }

@app.get("/api/log-search")
async def get_search_logs():
    """獲取搜索記錄"""
    return {
        "success": True,
        "data": search_logs,
        "total": len(search_logs)
    }

# 點擊記錄API
@app.post("/api/log-click")
async def log_click(log_entry: LogMessage):
    """記錄用戶點擊商品行為"""
    processed_entry = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "message": log_entry.message,
        "timestamp": datetime.now().isoformat()
    }
    
    click_logs.append(processed_entry)
    
    # 保持最新100條記錄
    if len(click_logs) > 100:
        click_logs[:] = click_logs[-100:]
    
    print(f"👆 {log_entry.message}")
    
    return {
        "success": True,
        "message": "Click logged successfully",
        "logId": processed_entry["id"]
    }

@app.get("/api/log-click")
async def get_click_logs():
    """獲取點擊記錄"""
    return {
        "success": True,
        "data": click_logs,
        "total": len(click_logs)
    }

# 數據分析API
@app.get("/api/analytics")
async def get_analytics():
    """獲取用戶行為的綜合分析數據"""
    # 統計唯一用戶
    unique_users = set()
    for log in search_logs:
        unique_users.add(log.get("sessionId", "anonymous"))
    for log in click_logs:
        unique_users.add(log.get("sessionId", "anonymous"))
    for log in client_logs:
        unique_users.add(log.get("userId", "anonymous"))
    
    # 統計熱門類別
    category_count = {}
    for log in click_logs:
        category = log.get("category", "未知")
        category_count[category] = category_count.get(category, 0) + 1
    
    top_categories = [
        {"category": category, "count": count}
        for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # 統計熱門搜索詞
    query_count = {}
    for log in search_logs:
        query = log.get("query", "").strip()
        if query:
            query_count[query] = query_count.get(query, 0) + 1
    
    top_search_queries = [
        {"query": query, "count": count}
        for query, count in sorted(query_count.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # 統計熱門商品
    product_count = {}
    for log in click_logs:
        product_id = log.get("productId")
        if product_id:
            if product_id not in product_count:
                product_count[product_id] = {
                    "productId": product_id,
                    "title": log.get("title", "未知商品"),
                    "count": 0
                }
            product_count[product_id]["count"] += 1
    
    top_clicked_products = sorted(product_count.values(), key=lambda x: x["count"], reverse=True)[:5]
    
    # 模擬時間線數據
    timeline = [
        {
            "timestamp": datetime.now().isoformat(),
            "searches": len(search_logs),
            "clicks": len(click_logs),
            "pageviews": len([log for log in client_logs if log.get("type") == "pageview"])
        }
    ]
    
    # 最近活動
    recent_activity = []
    for log in search_logs[-10:]:
        recent_activity.append({
            "type": "search",
            "timestamp": log.get("timestamp"),
            "details": log
        })
    for log in click_logs[-10:]:
        recent_activity.append({
            "type": "click",
            "timestamp": log.get("timestamp"),
            "details": log
        })
    
    # 按時間排序
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = recent_activity[:20]
    
    return {
        "success": True,
        "data": {
            "summary": {
                "totalSearches": len(search_logs),
                "totalClicks": len(click_logs),
                "totalClientEvents": len(client_logs),
                "uniqueUsers": len(unique_users),
                "topCategories": top_categories,
                "topSearchQueries": top_search_queries,
                "topClickedProducts": top_clicked_products
            },
            "timeline": timeline,
            "recentActivity": recent_activity
        },
        "generatedAt": datetime.now().isoformat()
    }

# AI搜索API
@app.post("/api/search")
async def ai_search(request: SearchRequest):
    """智能搜索，返回搜索結果和意圖分析"""
    query = request.query.lower()
    
    # 搜索商品
    filtered_products = [
        p for p in products_db 
        if query in p.title.lower() or 
           query in p.category.lower() or 
           query in p.brand.lower()
    ]
    
    # 分析意圖
    if "iphone" in query or "蘋果" in query:
        intent_title = "iPhone 系列"
        intent_attrs = ["高端", "iOS", "攝影", "5G", "Premium", "Apple", "Smartphone", "Camera"]
    elif "耳機" in query or "headphone" in query:
        intent_title = "耳機系列"
        intent_attrs = ["音質", "降噪", "無線", "舒適", "Audio", "Wireless", "Noise-Cancelling", "Hi-Fi"]
    elif "電腦" in query or "laptop" in query:
        intent_title = "筆電系列"
        intent_attrs = ["效能", "便攜", "辦公", "遊戲", "Performance", "Portable", "Professional", "Gaming"]
    else:
        intent_title = "精選商品"
        intent_attrs = ["精選", "品質", "設計", "實用", "Premium", "Quality", "Design", "Essential"]
    
    message = f"為您找到 {len(filtered_products)} 個相關商品，根據您的搜尋「{request.query}」為您推薦最適合的選擇。"
    
    return {
        "success": True,
        "data": {
            "intent": {
                "title": intent_title,
                "attrs": intent_attrs
            },
            "message": message,
            "products": filtered_products,
            "total": len(filtered_products)
        }
    }

# 推薦API
@app.post("/api/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """基於用戶行為的個性化推薦"""
    # 簡單的推薦邏輯：返回評分最高的商品
    recommended_products = sorted(products_db, key=lambda p: p.rating, reverse=True)[:request.limit]
    
    return {
        "success": True,
        "data": {
            "recommendations": recommended_products,
            "total": len(recommended_products),
            "reason": "基於您的瀏覽歷史和熱門商品推薦"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
