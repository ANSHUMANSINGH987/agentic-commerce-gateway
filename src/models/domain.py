from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, CheckConstraint, JSON, DateTime, func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pgvector.sqlalchemy import Vector
import uuid
from src.config import settings

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'products'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    stock_count = Column(Integer, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIM)) 

    __table_args__ = (
        CheckConstraint('stock_count >= 0', name='check_stock_non_negative'),
    )

    pricing_rules = relationship("PricingRule", back_populates="product", cascade="all, delete-orphan")


class PricingRule(Base):
    __tablename__ = 'pricing_rules'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), ForeignKey('products.id'), nullable=False)
    min_quantity = Column(Integer, nullable=False)
    max_discount_pct = Column(Numeric(5, 2), nullable=False)

    __table_args__ = (
        CheckConstraint('max_discount_pct <= 15.00', name='check_max_discount_limit'),
        CheckConstraint('max_discount_pct >= 0.00', name='check_min_discount_limit'),
    )

    product = relationship("Product", back_populates="pricing_rules")


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(PG_UUID(as_uuid=True), nullable=False)
    agent_action = Column(String(50), nullable=False) 
    details = Column(JSON, nullable=False) 
    rule_status = Column(String(50), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())