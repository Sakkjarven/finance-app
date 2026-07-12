import flet as ft
from datetime import datetime 
import requests

API_URL = "http://localhost:8000"

def main(page: ft.Page):
    page.title = "YNAB Финансы"
    page.window.width = 450
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    amount_field = ft.TextField(label="Сумма", keyboard_type=ft.KeyboardType.NUMBER)
    desc_field = ft.TextField(label="Описание (например: Пятерочка)")
    
    account_dropdown = ft.Dropdown(label="Счет (откуда)")
    category_dropdown = ft.Dropdown(label="Категория (на что)")
    
    status_text = ft.Text("", size=16)

    def load_references(e=None):
        """Загружаем счета и категории с бэкенда"""
        try:
            account_dropdown.options.clear()
            category_dropdown.options.clear()

            accounts_res = requests.get(f"{API_URL}/accounts/") 
            categories_res = requests.get(f"{API_URL}/categories/")

            if accounts_res.status_code == 200:
                for acc in accounts_res.json():
                    account_dropdown.options.append(ft.dropdown.Option(key=str(acc["id"]), text=acc["name"]))
            
            if categories_res.status_code == 200:
                for cat in categories_res.json():
                    category_dropdown.options.append(ft.dropdown.Option(key=str(cat["id"]), text=cat["name"]))

            status_text.value = "Справочники успешно загружены!"
            status_text.color = ft.Colors.BLUE
        except Exception as ex:
            status_text.value = f"Ошибка загрузки данных: {ex}"
            status_text.color = ft.Colors.RED
        
        page.update()

    def submit_transaction(e):
        """Отправляем новую транзакцию на бэкенд"""
        if not amount_field.value or not account_dropdown.value or not category_dropdown.value:
            status_text.value = "Пожалуйста, заполни все поля!"
            status_text.color = ft.Colors.RED
            page.update()
            return

        payload = {
            "amount": float(amount_field.value),
            "description": desc_field.value,
            "account_id": int(account_dropdown.value),
            "category_id": int(category_dropdown.value),
            "user_id" : 1,
            "type" : "expense",
            "date" : datetime.now().isoformat()
        }

        try:
            res = requests.post(f"{API_URL}/transactions/", json=payload)
            if res.status_code in [200, 201]:
                status_text.value = "успешно добавлена!"
                status_text.color = ft.Colors.GREEN
                amount_field.value = ""
                desc_field.value = ""
            else:
                status_text.value = f"Ошибка API: {res.text}"
                status_text.color = ft.Colors.RED
        except Exception as ex:
            status_text.value = f"Ошибка сети: {ex}"
            status_text.color = ft.Colors.RED
        
        page.update()

    load_btn = ft.Button(
        content=ft.Text("Обновить списки (Счета/Категории)"), 
        on_click=load_references
    )
    submit_btn = ft.Button(
        content=ft.Text("Добавить трату"), 
        on_click=submit_transaction,
        width=400
    )

    # --- Собираем всё на экран ---
    page.add(
        ft.Text("Новая транзакция", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        load_btn,
        account_dropdown,
        category_dropdown,
        amount_field,
        desc_field,
        ft.Container(height=10), # Пробел для красоты
        submit_btn,
        status_text
    )

    load_references()

ft.run(main)