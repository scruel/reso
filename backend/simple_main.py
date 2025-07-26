from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class Product(BaseModel):
    id: str
    title: str
    price: int
    image: str
    category: str
    brand: str
    rating: float
    url: str

# Mock data
products_db = [
    Product(id="1", title="iPhone 15 Pro Max 256GB", price=42990, image="https://...", category="手機", brand="Apple", rating=4.9, url="#"),
    # Add more mock products as needed
]

@app.get("/api/products", response_model=List[Product])
async def get_products():
    return products_db

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# A simpler main to run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
