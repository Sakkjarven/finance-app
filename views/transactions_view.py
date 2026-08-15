import customtkinter as ctk
from services import api

class TransactionsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.accounts_map = {}
        self.categories_map = {}

        left_col = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=10)
        left_col.pack(side="left", fill="y", padx=(0, 15), pady=0, ipadx=10)

        ctk.CTkLabel(left_col, text="Новая операция", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        self.type_switch = ctk.CTkSegmentedButton(left_col, values=["Расход", "Доход"], width=280)
        self.type_switch.set("Расход")
        self.type_switch.pack(padx=15, pady=(0, 10))

        ctk.CTkLabel(left_col, text="Счет:", anchor="w").pack(fill="x", padx=15)
        self.account_menu = ctk.CTkOptionMenu(left_col, values=["Загрузка..."], width=280)
        self.account_menu.pack(padx=15, pady=(0, 10))

        ctk.CTkLabel(left_col, text="Категория:", anchor="w").pack(fill="x", padx=15)
        self.category_menu = ctk.CTkOptionMenu(left_col, values=["Загрузка..."], width=280)
        self.category_menu.pack(padx=15, pady=(0, 10))

        self.amount_entry = ctk.CTkEntry(left_col, placeholder_text="Сумма (например: 1500)", width=280)
        self.amount_entry.pack(padx=15, pady=6)

        self.desc_entry = ctk.CTkEntry(left_col, placeholder_text="Описание (необязательно)", width=280)
        self.desc_entry.pack(padx=15, pady=6)

        self.submit_btn = ctk.CTkButton(left_col, text="Записать транзакцию", width=280, height=38, command=self.on_submit)
        self.submit_btn.pack(padx=15, pady=(15, 6))

        self.status_label = ctk.CTkLabel(left_col, text="", font=ctk.CTkFont(size=12), wraplength=280)
        self.status_label.pack(padx=15, pady=5)

        right_col = ctk.CTkFrame(self, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_col, text="История операций", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        self.history_scroll = ctk.CTkScrollableFrame(right_col, fg_color="#18181b", corner_radius=10)
        self.history_scroll.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        ok_acc, accs, _ = api.get_accounts(self.controller.token)
        if ok_acc and accs:
            self.accounts_map = {item["name"]: item["id"] for item in accs}
            names = list(self.accounts_map.keys())
            self.account_menu.configure(values=names)
            self.account_menu.set(names[0])

        ok_cat, cats, _ = api.get_categories(self.controller.token)
        if ok_cat and cats:
            self.categories_map = {item["name"]: item["id"] for item in cats}
            names = list(self.categories_map.keys())
            self.category_menu.configure(values=names)
            self.category_menu.set(names[0])

        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        ok_tx, txs, _ = api.get_transactions(self.controller.token)
        if ok_tx and txs:
            for tx in reversed(txs):
                row = ctk.CTkFrame(self.history_scroll, fg_color="#27272a", corner_radius=6)
                row.pack(fill="x", pady=3, padx=5)

                is_income = tx.get("type") == "income"
                amount_str = f"{'+' if is_income else '-'}{tx['amount']:,.2f} ₽"
                color = "#10b981" if is_income else "#f87171"

                desc = tx.get("description") or ("Доход" if is_income else "Расход")
                date_str = tx.get("date", "")[:10]

                ctk.CTkLabel(row, text=f" {desc} ", font=ctk.CTkFont(size=13)).pack(side="left", padx=10, pady=8)
                ctk.CTkLabel(row, text=date_str, font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=amount_str, font=ctk.CTkFont(size=13, weight="bold"), text_color=color).pack(side="right", padx=10)
        else:
            ctk.CTkLabel(self.history_scroll, text="Нет транзакций", text_color="gray").pack(pady=20)

    def on_submit(self):
        amount_raw = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip()
        acc_name = self.account_menu.get()
        cat_name = self.category_menu.get()
        tx_type = "income" if self.type_switch.get() == "Доход" else "expense"

        if not amount_raw or acc_name not in self.accounts_map or cat_name not in self.categories_map:
            self.status_label.configure(text="Заполните сумму, счет и категорию!", text_color="#FF5555")
            return

        try:
            amount = float(amount_raw)
        except ValueError:
            self.status_label.configure(text="Сумма должна быть числом!", text_color="#FF5555")
            return

        success, msg = api.create_transaction(
            token=self.controller.token,
            amount=amount,
            description=desc,
            tx_type=tx_type,
            account_id=self.accounts_map[acc_name],
            category_id=self.categories_map[cat_name]
        )

        if success:
            self.status_label.configure(text=msg, text_color="#55FF55")
            self.amount_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")
            self.load_data()
        else:
            self.status_label.configure(text=msg, text_color="#FF5555")