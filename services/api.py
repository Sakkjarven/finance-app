import requests
from datetime import datetime

API_URL = "http://localhost:8000"

def parse_error(response: requests.Response) -> str:
    try: 
        data = response.json()
        detail = data.get("detail")
        if isinstance(detail, list):
            return detail[0].get("msg", str(detail))
        return str(detail) if detail else f"Ошибка {response.status_code}"
    except Exception:
        return response.text or f"Ошибка {response.status_code}"

def login(username: str, password: str) -> tuple[bool, str]:
    try:
        res = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password},
            timeout=5
        )
        
        if res.status_code == 200:
            token = res.json().get("access_token")
            return True, token
        return False, parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

def register(email: str, password: str) -> tuple[bool, str]:
    try:
        res = requests.post(
            f"{API_URL}/register",
            json={"email": email, "password": password},
            timeout=5
        )
        if res.status_code in (200, 201):
            return True, "Успешно"
        return False, parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"

def get_references(token: str) -> tuple[bool, dict, dict, str]:
    # Исправлено: Authorization через 'z'
    headers = {"Authorization": f"Bearer {token}"}
    try:
        acc_res = requests.get(f"{API_URL}/accounts/", headers=headers, timeout=5)
        cat_res = requests.get(f"{API_URL}/categories/", headers=headers, timeout=5)

        if acc_res.status_code != 200:
            return False, {}, {}, parse_error(acc_res)
        if cat_res.status_code != 200:
            return False, {}, {}, parse_error(cat_res)

        accounts = {item["name"]: item["id"] for item in acc_res.json()}
        categories = {item["name"]: item["id"] for item in cat_res.json()}
        return True, accounts, categories, ""
    except Exception as ex:
        return False, {}, {}, f"Ошибка загрузки: {ex}"

def add_transaction(token: str, amount: float, description: str, account_id: int, category_id: int) -> tuple[bool, str]:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "amount": amount,
        "description": description or None,
        "account_id": account_id,
        "category_id": category_id,
        "type": "expense",
        "date": datetime.utcnow().isoformat()
    }
    try:
        res = requests.post(
            f"{API_URL}/transactions/",
            json=payload,
            headers=headers,
            timeout=5
        )
        if res.status_code in (200, 201):
            return True, "Транзакция успешно добавлена!"
        return False, parse_error(res)
    except Exception as ex:
        return False, f"Ошибка сети: {ex}"