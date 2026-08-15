import customtkinter as ctk
from views.auth_view import AuthView
from views.dashboard_view import DashboardView
from views.transactions_view import TransactionsView
from views.accounts_view import AccountsView
from views.categories_view import CategoriesView
from views.budget_view import BudgetView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YNAB Финансы — Система управления бюджетом")
        self.geometry("1020x680")
        self.minsize(960, 600)

        self.token = None
        self.user_email = ""

        self.nav_buttons = {}

        # Базовый контейнер
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.show_auth_view()

    def clear_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_auth_view(self):
        self.clear_container()
        auth_frame = AuthView(self.main_container, self)
        auth_frame.pack(fill="both", expand=True)

    def show_main_app(self):
        self.clear_container()

        # 1. Сайдбар слева
        sidebar = ctk.CTkFrame(self.main_container, width=220, fg_color="#18181b", corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Логотип
        ctk.CTkLabel(sidebar, text="YNAB Finance", font=ctk.CTkFont(size=20, weight="bold")).pack(padx=20, pady=(25, 5), anchor="w")
        
        # Инфо о пользователе
        user_lbl = ctk.CTkLabel(sidebar, text=self.user_email, font=ctk.CTkFont(size=11), text_color="#9ca3af")
        user_lbl.pack(padx=20, pady=(0, 20), anchor="w")

        # Кнопки навигации
        nav_items = [
            ("Дашборд", DashboardView),
            ("Транзакции", TransactionsView),
            ("Бюджеты", BudgetView),
            ("Счета", AccountsView),
            ("Категории", CategoriesView),
        ]

        self.nav_buttons = {}
        for title, view_cls in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=title,
                height=38,
                anchor="w",
                fg_color="transparent",
                hover_color="#27272a",
                text_color="#e4e4e7",
                command=lambda v=view_cls, t=title: self.navigate_to(v, t)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[title] = btn

        # Кнопка выхода внизу
        logout_btn = ctk.CTkButton(
            sidebar,
            text="Выйти",
            height=36,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.logout
        )
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)

        # 2. Область для экранов справа
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=25, pady=20)

        # Открываем Дашборд по умолчанию
        self.navigate_to(DashboardView, "Дашборд")

    def navigate_to(self, view_class, title):
        # Подсветка активной кнопки меню
        for name, btn in self.nav_buttons.items():
            if name == title:
                btn.configure(fg_color="#3b82f6", text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color="#e4e4e7")

        # Очистка и отрисовка вьюшки
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view = view_class(self.content_frame, self)
        view.pack(fill="both", expand=True)

    def logout(self):
        self.token = None
        self.user_email = ""
        self.show_auth_view()

if __name__ == "__main__":
    app = App()
    app.mainloop()