import os
import requests
from datetime import datetime

API_URL = os.getenv("FINANCE_API_URL", "http://127.0.0.1:8000")

def _parse_error(res: requests.Response) -> str:
    try:
        data = res.json()
        detail = data.get("detail")
        if isinstance(detail, list):
            return detail[0].get("msg", str(detail))
        return str(detail) if detail else f"Ошибка {res.status_code}"
    except Exception:
        return res.text or f"Ошибка {res.status_code}"

def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

# --- Авторизация ---
def login(username: str, password: str) -> tuple[bool, str]:
    try:
        res = requests.post(f"{API_URL}/login", data={"username": username, "password": password}, timeout=5)
        if res.status_code == 200:
            return True, res.json().get("access_token", "")
        return False, _parse_error(res)
    except Exception as ex:
        return False, f"Бэкенд недоступен: {ex}"

def register(email: str, password: str) -> tuple[bool, str]:
    try:
        res = requests.post(f"{API_URL}/register", json={"email": email, "password": password}, timeout=5)
        if res.status_code in (200, 201):
            return True, "Аккаунт успешно создан!"
        return False, _parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

# --- Счета ---
def get_accounts(token: str) -> tuple[bool, list, str]:
    try:
        res = requests.get(f"{API_URL}/accounts/", headers=_headers(token), timeout=5)
        if res.status_code == 200:
            return True, res.json(), ""
        return False, [], _parse_error(res)
    except Exception as ex:
        return False, [], f"Ошибка сети: {ex}"

def create_account(token: str, name: str, balance: float) -> tuple[bool, str]:
    try:
        res = requests.post(
            f"{API_URL}/accounts/", 
            json={"name": name, "balance": balance}, 
            headers=_headers(token), 
            timeout=5
        )
        if res.status_code in (200, 201):
            return True, "Счет успешно создан!"
        return False, _parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

# --- Категории ---
def get_categories(token: str) -> tuple[bool, list, str]:
    try:
        res = requests.get(f"{API_URL}/categories/", headers=_headers(token), timeout=5)
        if res.status_code == 200:
            return True, res.json(), ""
        return False, [], _parse_error(res)
    except Exception as ex:
        return False, [], f"Ошибка сети: {ex}"

def create_category(token: str, name: str) -> tuple[bool, str]:
    try:
        res = requests.post(
            f"{API_URL}/categories/", 
            json={"name": name}, 
            headers=_headers(token), 
            timeout=5
        )
        if res.status_code in (200, 201):
            return True, "Категория успешно создана!"
        return False, _parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

# --- Транзакции ---
def get_transactions(token: str) -> tuple[bool, list, str]:
    try:
        res = requests.get(f"{API_URL}/transactions/", headers=_headers(token), timeout=5)
        if res.status_code == 200:
            return True, res.json(), ""
        return False, [], _parse_error(res)
    except Exception as ex:
        return False, [], f"Ошибка сети: {ex}"

def create_transaction(
    token: str, 
    amount: float, 
    description: str, 
    tx_type: str, 
    account_id: int, 
    category_id: int
) -> tuple[bool, str]:
    payload = {
        "amount": amount,
        "description": description or None,
        "type": tx_type,
        "account_id": account_id,
        "category_id": category_id,
        "date": datetime.utcnow().isoformat()
    }
    try:
        res = requests.post(f"{API_URL}/transactions/", json=payload, headers=_headers(token), timeout=5)
        if res.status_code in (200, 201):
            return True, "Транзакция успешно записана!"
        return False, _parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

# --- Бюджеты и Аналитика ---
def set_budget(token: str, month: str, amount: float, category_id: int) -> tuple[bool, str]:
    payload = {"month": month, "amount": amount, "category_id": category_id}
    try:
        res = requests.post(f"{API_URL}/budgets/", json=payload, headers=_headers(token), timeout=5)
        if res.status_code in (200, 201):
            return True, "Бюджет установлен!"
        return False, _parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

def get_budget_summary(token: str, month: str) -> tuple[bool, list, str]:
    try:
        res = requests.get(
            f"{API_URL}/analytics/budget-summary/", 
            params={"month": month}, 
            headers=_headers(token), 
            timeout=5
        )
        if res.status_code == 200:
            return True, res.json(), ""
        return False, [], _parse_error(res)
    except Exception as ex:
        return False, [], f"Ошибка сети: {ex}"