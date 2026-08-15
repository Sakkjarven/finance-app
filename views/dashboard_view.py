import customtkinter as ctk
from datetime import datetime
from services import api
from services.async_helper import run_in_background

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.current_month = datetime.now().strftime("%Y-%m")

        # Шапка
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="Сводка и Аналитика", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(side="left")

        self.refresh_btn = ctk.CTkButton(
            header, 
            text="Обновить", 
            width=90, 
            height=30, 
            fg_color="#333333", 
            command=self.load_dashboard_data
        )
        self.refresh_btn.pack(side="right")

        # Карточки баланса
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 15))

        self.balance_card = ctk.CTkFrame(cards_frame, fg_color="#1f2937", corner_radius=10)
        self.balance_card.pack(side="left", fill="both", expand=True, padx=(0, 8), ipady=10)
        
        ctk.CTkLabel(self.balance_card, text="Общий баланс счетов", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=15, pady=(5, 0))
        self.balance_val = ctk.CTkLabel(self.balance_card, text="Загрузка...", font=ctk.CTkFont(size=22, weight="bold"), text_color="#10b981")
        self.balance_val.pack(anchor="w", padx=15)

        self.month_card = ctk.CTkFrame(cards_frame, fg_color="#1f2937", corner_radius=10)
        self.month_card.pack(side="left", fill="both", expand=True, padx=(8, 0), ipady=10)
        
        ctk.CTkLabel(self.month_card, text="Текущий расчетный период", font=ctk.CTkFont(size=12), text_color="#9ca3af").pack(anchor="w", padx=15, pady=(5, 0))
        self.month_val = ctk.CTkLabel(self.month_card, text=self.current_month, font=ctk.CTkFont(size=22, weight="bold"), text_color="#3b82f6")
        self.month_val.pack(anchor="w", padx=15)

        ctk.CTkLabel(self, text=f"Исполнение бюджетов ({self.current_month})", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10, 8))
        self.budget_scroll = ctk.CTkScrollableFrame(self, height=180, fg_color="#18181b", corner_radius=10)
        self.budget_scroll.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self, text="Последние операции", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(5, 8))
        self.tx_scroll = ctk.CTkScrollableFrame(self, height=160, fg_color="#18181b", corner_radius=10)
        self.tx_scroll.pack(fill="both", expand=True)

        self.load_dashboard_data()

    def load_dashboard_data(self):
        self.refresh_btn.configure(state="disabled", text="...")
        
        def fetch_all():
            ok_acc, accounts, _ = api.get_accounts(self.controller.token)
            ok_bud, summaries, _ = api.get_budget_summary(self.controller.token, self.current_month)
            ok_tx, tx_list, _ = api.get_transactions(self.controller.token)
            return (accounts if ok_acc else [], summaries if ok_bud else [], tx_list if ok_tx else [])

        def on_loaded(data):
            accounts, summaries, tx_list = data
            self.after(0, lambda: self._update_ui(accounts, summaries, tx_list))

        run_in_background(fetch_all, on_success=on_loaded)

    def _update_ui(self, accounts, summaries, tx_list):
        self.refresh_btn.configure(state="normal", text="Обновить")

        # 1. Баланс
        total_bal = sum(acc.get("balance", 0.0) for acc in accounts)
        self.balance_val.configure(text=f"{total_bal:,.2f} ₽".replace(",", " "))

        # 2. Бюджеты
        for w in self.budget_scroll.winfo_children():
            w.destroy()

        if summaries:
            for item in summaries:
                name = item["category_name"]
                budgeted = item["budgeted"]
                spent = item["spent"]
                remaining = item["remaining"]

                ratio = min(spent / budgeted, 1.0) if budgeted > 0 else 0.0
                bar_color = "#ef4444" if remaining < 0 else ("#eab308" if ratio > 0.85 else "#10b981")

                row = ctk.CTkFrame(self.budget_scroll, fg_color="transparent")
                row.pack(fill="x", pady=5, padx=5)

                header_row = ctk.CTkFrame(row, fg_color="transparent")
                header_row.pack(fill="x")
                ctk.CTkLabel(header_row, text=name, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
                ctk.CTkLabel(
                    header_row, 
                    text=f"Потрачено: {spent:,.0f} ₽ из {budgeted:,.0f} ₽ (Остаток: {remaining:,.0f} ₽)", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#9ca3af"
                ).pack(side="right")

                bar = ctk.CTkProgressBar(row, height=8, progress_color=bar_color)
                bar.pack(fill="x", pady=(4, 0))
                bar.set(ratio)
        else:
            ctk.CTkLabel(self.budget_scroll, text="Нет бюджетов на этот месяц", text_color="gray").pack(pady=20)

        for w in self.tx_scroll.winfo_children():
            w.destroy()

        if tx_list:
            for tx in reversed(tx_list[-10:]):
                row = ctk.CTkFrame(self.tx_scroll, fg_color="#27272a", corner_radius=6)
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
            ctk.CTkLabel(self.tx_scroll, text="История операций пуста", text_color="gray").pack(pady=20)