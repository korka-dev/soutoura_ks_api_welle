from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100))
    sous_category = Column(String(100)) 
    stock = Column(Integer, default=0)
    images = Column(JSON)
    sizes = Column(JSON, default=[])
    colors = Column(JSON, default=[])
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    