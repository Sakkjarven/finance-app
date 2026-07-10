from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"

class UserCreate(BaseModel):
    username : str
class UserResponse(BaseModel):
    id : int
    username : str

    class Config:
        from_attributes = True
class AccountCreate(BaseModel):
    user_id : int
    name : str
class AccountResponse(BaseModel):
    id : int
    name : str
    balance : float
    user_id : int

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name : str
    user_id : int

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

    user_id : int
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