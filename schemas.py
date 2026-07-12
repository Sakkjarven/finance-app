from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"

class UserBase(BaseModel):
    email : str

class UserCreate(UserBase):
    password : str

class UserResponse(UserBase):
    id : int
    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    name : str
    balance : float = 0.0 
class AccountResponse(BaseModel):
    id : int
    name : str
    balance : float
    user_id : int

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name : str

class CategoryResponse(BaseModel):
    id : int
    name : str
    user_id : int

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    amount : float
    description : str | None = None
    date : datetime
    type : TransactionType

    account_id : int
    category_id : int

class TransactionResponse(BaseModel):
    id : int
    amount : float
    description : str | None
    date : datetime
    type : TransactionType

    user_id : int
    account_id : int
    category_id : int
    
    class Config:
        from_attributes = True

class BudgetAllocationCreate(BaseModel):
    month : str       
    amount : float    
    user_id : int
    category_id : int

class BudgetAllocationResponse(BaseModel):
    id : int
    month : str
    amount : float
    user_id : int
    category_id : int

    class Config:
        from_attributes = True

class CategorySummary(BaseModel):
    category_id: int
    category_name: str
    budgeted: float     
    spent: float        
    remaining: float
        
    class Config:
        from_attributes = True