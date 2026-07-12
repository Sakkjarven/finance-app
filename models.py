from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String) 
    
class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    balance = Column(Float, default = 0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))    
    category_id = Column(Integer, ForeignKey("categories.id"))    

class BudgetAllocation(Base):
    __tablename__ = "budget_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    month = Column(String) 
    amount = Column(Float) 
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))