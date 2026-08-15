import customtkinter as ctk
from services import api

class AccountsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Левая колонка: Добавление
        left_col = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=10)
        left_col.pack(side="left", fill="y", padx=(0, 15), ipadx=10)

        ctk.CTkLabel(left_col, text="Создать счет", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        self.name_entry = ctk.CTkEntry(left_col, placeholder_text="Название (напр.: Сбербанк, Наличные)", width=280)
        self.name_entry.pack(padx=15, pady=8)

        self.balance_entry = ctk.CTkEntry(left_col, placeholder_text="Начальный баланс (напр.: 10000)", width=280)
        self.balance_entry.pack(padx=15, pady=8)

        self.submit_btn = ctk.CTkButton(left_col, text="Сохранить счет", width=280, height=38, command=self.on_submit)
        self.submit_btn.pack(padx=15, pady=(12, 6))

        self.status_label = ctk.CTkLabel(left_col, text="", font=ctk.CTkFont(size=12), wraplength=280)
        self.status_label.pack(padx=15, pady=5)

        # Правая колонка: Список счетов
        right_col = ctk.CTkFrame(self, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_col, text="Ваши финансовые счета", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        self.accounts_scroll = ctk.CTkScrollableFrame(right_col, fg_color="#18181b", corner_radius=10)
        self.accounts_scroll.pack(fill="both", expand=True)

        self.load_accounts()

    def load_accounts(self):
        for widget in self.accounts_scroll.winfo_children():
            widget.destroy()

        ok, accounts, err = api.get_accounts(self.controller.token)
        if ok and accounts:
            for acc in accounts:
                row = ctk.CTkFrame(self.accounts_scroll, fg_color="#27272a", corner_radius=8)
                row.pack(fill="x", pady=4, padx=5)

                ctk.CTkLabel(row, text=acc["name"], font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=12)
                ctk.CTkLabel(row, text=f"{acc['balance']:,.2f} ₽", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10b981").pack(side="right", padx=15)
        else:
            ctk.CTkLabel(self.accounts_scroll, text="Счетов пока нет. Создайте первый слева!", text_color="gray").pack(pady=20)

    def on_submit(self):
        name = self.name_entry.get().strip()
        bal_raw = self.balance_entry.get().strip() or "0"

        if not name:
            self.status_label.configure(text="Введите название счета!", text_color="#FF5555")
            return

        try:
            bal = float(bal_raw)
        except ValueError:
            self.status_label.configure(text="Баланс должен быть числом!", text_color="#FF5555")
            return

        success, msg = api.create_account(self.controller.token, name, bal)
        if success:
            self.status_label.configure(text=msg, text_color="#55FF55")
            self.name_entry.delete(0, "end")
            self.balance_entry.delete(0, "end")
            self.load_accounts()
        else:
            self.status_label.configure(text=msg, text_color="#FF5555")