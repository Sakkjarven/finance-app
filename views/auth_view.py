import customtkinter as ctk
from services import api

class AuthView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.title = ctk.CTkLabel(self, text="YNAB Finance", font=ctk.CTkFont(size=28, weight="bold"))
        self.title.pack(pady=(30, 5))

        self.subtitle = ctk.CTkLabel(self, text="Авторизация", font=ctk.CTkFont(size=14), text_color="gray")
        self.subtitle.pack(pady=(0, 25))

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=320, height=40)
        self.email_entry.pack(pady=8)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*", width=320, height=40)
        self.pass_entry.pack(pady=8)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), wraplength=300)
        self.status_label.pack(pady=5)

        self.login_btn = ctk.CTkButton(self, text="Войти в систему", width=320, height=42, command=self.on_login)
        self.login_btn.pack(pady=(10, 6))

        self.register_btn = ctk.CTkButton(
            self, 
            text="Создать новый аккаунт", 
            width=320, 
            height=38, 
            fg_color="#2b2b2b", 
            hover_color="#3a3a3a", 
            command=self.on_register
        )
        self.register_btn.pack(pady=6)

        self.email_entry.bind("<Return>", lambda e: self.on_login())
        self.pass_entry.bind("<Return>", lambda e: self.on_login())

    def on_login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not email or not password:
            self.status_label.configure(text="Заполните email и пароль!", text_color="#FF5555")
            return

        success, result = api.login(email, password)
        if success:
            self.controller.token = result
            self.controller.show_main_view()
        else:
            self.status_label.configure(text=result, text_color="#FF5555")

    def on_register(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not email or not password:
            self.status_label.configure(text="Заполните поля для регистрации!", text_color="#FF5555")
            return

        success, message = api.register(email, password)
        if success:
            self.status_label.configure(text=f"{message} Теперь нажмите «Войти»", text_color="#55FF55")
        else:
            self.status_label.configure(text=message, text_color="#FF5555")