import customtkinter as ctk
from services import api

class MainView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.accounts_map = {}
        self.categories_map = {}

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 15))

        title = ctk.CTkLabel(header, text="YNAB Финансы", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(side="left")

        logout_btn = ctk.CTkButton(
            header, 
            text="Выйти", 
            width=70, 
            height=30, 
            fg_color="#444444", 
            hover_color="#333333", 
            command=self.logout
        )
        logout_btn.pack(side="right")

        sep = ctk.CTkFrame(self, height=2, fg_color="#333333")
        sep.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self, text="Счет (откуда):", anchor="w").pack(fill="x")
        self.account_menu = ctk.CTkOptionMenu(self, values=["Загрузка..."], width=350, height=38)
        self.account_menu.pack(pady=(0, 10))

        ctk.CTkLabel(self, text="Категория (на что):", anchor="w").pack(fill="x")
        self.category_menu = ctk.CTkOptionMenu(self, values=["Загрузка..."], width=350, height=38)
        self.category_menu.pack(pady=(0, 10))

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Сумма (например: 500)", width=350, height=38)
        self.amount_entry.pack(pady=5)

        self.desc_entry = ctk.CTkEntry(self, placeholder_text="Описание (например: Продукты)", width=350, height=38)
        self.desc_entry.pack(pady=5)

        self.submit_btn = ctk.CTkButton(self, text="Добавить трату", width=350, height=42, command=self.on_submit)
        self.submit_btn.pack(pady=(15, 8))

        self.refresh_btn = ctk.CTkButton(
            self, 
            text="Обновить справочники", 
            width=350, 
            height=36, 
            fg_color="#2b2b2b", 
            hover_color="#3a3a3a", 
            command=self.load_data
        )
        self.refresh_btn.pack(pady=4)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), wraplength=350)
        self.status_label.pack(pady=10)

        self.load_data()

    def logout(self):
        self.controller.token = None
        self.controller.show_auth_view()

    def load_data(self):
        success, accounts, categories, err = api.get_references(self.controller.token)
        if not success:
            self.status_label.configure(text=err, text_color="#FF5555")
            return

        self.accounts_map = accounts
        self.categories_map = categories

        acc_names = list(accounts.keys())
        cat_names = list(categories.keys())

        self.account_menu.configure(values=acc_names or ["Нет счетов"])
        self.account_menu.set(acc_names[0] if acc_names else "Нет счетов")

        self.category_menu.configure(values=cat_names or ["Нет категорий"])
        self.category_menu.set(cat_names[0] if cat_names else "Нет категорий")

        self.status_label.configure(text="Справочники обновлены", text_color="#55AAFF")

    def on_submit(self):
        amount_raw = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip()
        acc_name = self.account_menu.get()
        cat_name = self.category_menu.get()

        if not amount_raw or acc_name not in self.accounts_map or cat_name not in self.categories_map:
            self.status_label.configure(text="Заполните сумму и выберите счет и категорию!", text_color="#FF5555")
            return

        try:
            amount = float(amount_raw)
        except ValueError:
            self.status_label.configure(text="Сумма должна быть числом!", text_color="#FF5555")
            return

        success, message = api.add_transaction(
            token=self.controller.token,
            amount=amount,
            description=desc,
            account_id=self.accounts_map[acc_name],
            category_id=self.categories_map[cat_name]
        )

        if success:
            self.status_label.configure(text=message, text_color="#55FF55")
            self.amount_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")
        else:
            self.status_label.configure(text=message, text_color="#FF5555")