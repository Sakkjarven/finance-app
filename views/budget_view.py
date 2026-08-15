import customtkinter as ctk
from datetime import datetime
from services import api

class BudgetView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.categories_map = {}

        # Левая колонка: Форма назначения лимита
        left_col = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=10)
        left_col.pack(side="left", fill="y", padx=(0, 15), ipadx=10)

        ctk.CTkLabel(left_col, text="Назначить бюджет", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(left_col, text="Месяц (ГГГГ-ММ):", anchor="w").pack(fill="x", padx=15)
        self.month_entry = ctk.CTkEntry(left_col, width=280)
        self.month_entry.insert(0, datetime.now().strftime("%Y-%m"))
        self.month_entry.pack(padx=15, pady=(0, 8))

        ctk.CTkLabel(left_col, text="Категория:", anchor="w").pack(fill="x", padx=15)
        self.category_menu = ctk.CTkOptionMenu(left_col, values=["Загрузка..."], width=280)
        self.category_menu.pack(padx=15, pady=(0, 8))

        ctk.CTkLabel(left_col, text="Лимит бюджета (₽):", anchor="w").pack(fill="x", padx=15)
        self.amount_entry = ctk.CTkEntry(left_col, placeholder_text="Например: 25000", width=280)
        self.amount_entry.pack(padx=15, pady=(0, 8))

        self.submit_btn = ctk.CTkButton(left_col, text="Установить лимит", width=280, height=38, command=self.on_submit)
        self.submit_btn.pack(padx=15, pady=(10, 6))

        self.status_label = ctk.CTkLabel(left_col, text="", font=ctk.CTkFont(size=12), wraplength=280)
        self.status_label.pack(padx=15, pady=5)

        # Правая колонка: Отчет по исполнению
        right_col = ctk.CTkFrame(self, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        header_right = ctk.CTkFrame(right_col, fg_color="transparent")
        header_right.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_right, text="Исполнение бюджета", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        load_month_btn = ctk.CTkButton(
            header_right, 
            text="Показать месяц", 
            width=120, 
            height=30, 
            fg_color="#333333", 
            command=self.load_summary
        )
        load_month_btn.pack(side="right")

        self.summary_scroll = ctk.CTkScrollableFrame(right_col, fg_color="#18181b", corner_radius=10)
        self.summary_scroll.pack(fill="both", expand=True)

        self.init_data()

    def init_data(self):
        ok, cats, _ = api.get_categories(self.controller.token)
        if ok and cats:
            self.categories_map = {item["name"]: item["id"] for item in cats}
            names = list(self.categories_map.keys())
            self.category_menu.configure(values=names)
            self.category_menu.set(names[0])
        self.load_summary()

    def load_summary(self):
        for widget in self.summary_scroll.winfo_children():
            widget.destroy()

        month = self.month_entry.get().strip()
        ok, summaries, err = api.get_budget_summary(self.controller.token, month)

        if ok and summaries:
            for item in summaries:
                row = ctk.CTkFrame(self.summary_scroll, fg_color="#27272a", corner_radius=8)
                row.pack(fill="x", pady=5, padx=5)

                name = item["category_name"]
                budgeted = item["budgeted"]
                spent = item["spent"]
                remaining = item["remaining"]

                ratio = min(spent / budgeted, 1.0) if budgeted > 0 else 0.0
                bar_color = "#ef4444" if remaining < 0 else ("#eab308" if ratio > 0.85 else "#10b981")

                top_line = ctk.CTkFrame(row, fg_color="transparent")
                top_line.pack(fill="x", padx=12, pady=(10, 2))

                ctk.CTkLabel(top_line, text=name, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
                ctk.CTkLabel(
                    top_line, 
                    text=f"Осталось: {remaining:,.2f} ₽", 
                    font=ctk.CTkFont(size=13, weight="bold"), 
                    text_color="#10b981" if remaining >= 0 else "#ef4444"
                ).pack(side="right")

                stats_line = ctk.CTkFrame(row, fg_color="transparent")
                stats_line.pack(fill="x", padx=12, pady=(0, 6))
                ctk.CTkLabel(
                    stats_line, 
                    text=f"Бюджет: {budgeted:,.2f} ₽  |  Траты: {spent:,.2f} ₽", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#9ca3af"
                ).pack(side="left")

                bar = ctk.CTkProgressBar(row, height=8, progress_color=bar_color)
                bar.pack(fill="x", padx=12, pady=(0, 12))
                bar.set(ratio)
        else:
            ctk.CTkLabel(self.summary_scroll, text=f"Нет данных по бюджетам за {month}", text_color="gray").pack(pady=20)

    def on_submit(self):
        month = self.month_entry.get().strip()
        cat_name = self.category_menu.get()
        amt_raw = self.amount_entry.get().strip()

        if not month or cat_name not in self.categories_map or not amt_raw:
            self.status_label.configure(text="Заполните все поля!", text_color="#FF5555")
            return

        try:
            amount = float(amt_raw)
        except ValueError:
            self.status_label.configure(text="Лимит должен быть числом!", text_color="#FF5555")
            return

        success, msg = api.set_budget(
            self.controller.token, 
            month, 
            amount, 
            self.categories_map[cat_name]
        )

        if success:
            self.status_label.configure(text=msg, text_color="#55FF55")
            self.amount_entry.delete(0, "end")
            self.load_summary()
        else:
            self.status_label.configure(text=msg, text_color="#FF5555")