import customtkinter as ctk
from services import api

class AuthView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        box = ctk.CTkFrame(self, fg_color="#242424", corner_radius=12)
        box.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(box, text="YNAB Finance", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(padx=30, pady=(30, 5))

        subtitle = ctk.CTkLabel(box, text="Управление личным бюджетом", font=ctk.CTkFont(size=13), text_color="gray")
        subtitle.pack(padx=30, pady=(0, 20))

        self.email_entry = ctk.CTkEntry(box, placeholder_text="Email", width=280, height=38)
        self.email_entry.pack(padx=30, pady=8)

        self.pass_entry = ctk.CTkEntry(box, placeholder_text="Пароль", show="*", width=280, height=38)
        self.pass_entry.pack(padx=30, pady=8)

        self.status_label = ctk.CTkLabel(box, text="", font=ctk.CTkFont(size=12), wraplength=280)
        self.status_label.pack(padx=30, pady=5)

        self.login_btn = ctk.CTkButton(box, text="Войти", width=280, height=40, command=self.on_login)
        self.login_btn.pack(padx=30, pady=(8, 4))

        self.register_btn = ctk.CTkButton(
            box, 
            text="Создать аккаунт", 
            width=280, 
            height=36, 
            fg_color="#333333", 
            hover_color="#444444", 
            command=self.on_register
        )
        self.register_btn.pack(padx=30, pady=(4, 30))

        self.email_entry.bind("<Return>", lambda e: self.on_login())
        self.pass_entry.bind("<Return>", lambda e: self.on_login())

    def on_login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not email or not password:
            self.status_label.configure(text="Заполните все поля!", text_color="#FF5555")
            return

        success, result = api.login(email, password)
        if success:
            self.controller.token = result
            self.controller.user_email = email
            self.controller.show_main_app()
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
            self.status_label.configure(text=f"{message} Теперь войдите.", text_color="#55FF55")
        else:
            self.status_label.configure(text=message, text_color="#FF5555")