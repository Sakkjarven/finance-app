from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance AI app")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello!"}

#Endpoints fur users

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

#Endpoints fur accounts

@app.post("/accounts/", response_model=schemas.AccountResponse)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(user_id=account.user_id, balance=account.balance, name=account.name)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.get("/accounts/", response_model=list[schemas.AccountResponse])
def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(models.Account).all()
    return accounts

#Endpoints fur categories

@app.post("/categories/", response_model=schemas.CategoryCreate)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(name=category.name, user_id=category.user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=list[schemas.CategoryResponse])
def get_category(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

#Endpoints fur transactions

@app.post("/transactions/", response_model=schemas.TransactionResponse)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == transaction.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счет не найден")
    if transaction.type == schemas.TransactionType.expense:
        if(account.balance < transaction.amount):
            raise HTTPException(status_code=400, detail="balance less than expense")
        account.balance -= transaction.amount
    elif transaction.type == schemas.TransactionType.income:
        account.balance += transaction.amount
    db_transaction = models.Transaction(
        amount=transaction.amount,
        description=transaction.description,
        type=transaction.type,
        user_id=transaction.user_id,
        account_id=transaction.account_id,
        category_id=transaction.category_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/transactions/", response_model=list[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()
    return transactions

# endpoints for budget alloc

@app.post("/budgets/", response_model=schemas.BudgetAllocationResponse)
def set_budget(budget: schemas.BudgetAllocationCreate, db: Session = Depends(get_db)):
    existing_budget = db.query(models.BudgetAllocation).filter(
        models.BudgetAllocation.user_id == budget.user_id,
        models.BudgetAllocation.category_id == budget.category_id,
        models.BudgetAllocation.month == budget.month
    ).first()

    if existing_budget:
        existing_budget.amount = budget.amount
        db.commit()
        db.refresh(existing_budget)
        return existing_budget
    else:
        new_budget = models.BudgetAllocation(
            month=budget.month,
            amount=budget.amount,
            user_id=budget.user_id,
            category_id=budget.category_id
        )
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        return new_budget

@app.get("/budgets/", response_model=list[schemas.BudgetAllocationResponse])
def get_budgets(db: Session = Depends(get_db)):
    return db.query(models.BudgetAllocation).all()

#endpoints for analytics

@app.get("/analytics/budget-summary/", response_model=list[schemas.CategorySummary])
def get_budget_summary(user_id: int, month: str, db: Session = Depends(get_db)):
    budgets = db.query(models.BudgetAllocation).filter(
        models.BudgetAllocation.user_id == user_id,
        models.BudgetAllocation.month == month
    ).all()

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.type == schemas.TransactionType.expense
    ).all()

    monthly_transactions = [
        t for t in transactions 
        if t.date.strftime("%Y-%m") == month
    ]

    summary = []
    for b in budgets:
        category = db.query(models.Category).filter(models.Category.id == b.category_id).first()
        category_name = category.name if category else "Неизвестно"
        
        spent = sum(t.amount for t in monthly_transactions if t.category_id == b.category_id)
        
        summary.append(schemas.CategorySummary(
            category_id=b.category_id,
            category_name=category_name,
            budgeted=b.amount,
            spent=spent,
            remaining=b.amount - spent
        ))
    
    return summary