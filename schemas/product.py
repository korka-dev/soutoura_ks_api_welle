from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    sous_category: Optional[str] = None
    stock: int = 0
    images: Optional[List[str]] = []
    sizes: Optional[List[str]] = []
    colors: Optional[List[str]] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    sous_category: Optional[str] = None
    stock: Optional[int] = None
    images: Optional[List[str]] = None
    sizes: Optional[List[str]] = None  
    colors: Optional[List[str]] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True