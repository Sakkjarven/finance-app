import customtkinter as ctk
from services import api

class CategoriesView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Левая колонка: Добавление категории
        left_col = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=10)
        left_col.pack(side="left", fill="y", padx=(0, 15), ipadx=10)

        ctk.CTkLabel(left_col, text="Создать категорию", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        self.name_entry = ctk.CTkEntry(left_col, placeholder_text="Название (напр.: Продукты, Авто)", width=280)
        self.name_entry.pack(padx=15, pady=8)

        self.submit_btn = ctk.CTkButton(left_col, text="Сохранить категорию", width=280, height=38, command=self.on_submit)
        self.submit_btn.pack(padx=15, pady=(12, 6))

        self.status_label = ctk.CTkLabel(left_col, text="", font=ctk.CTkFont(size=12), wraplength=280)
        self.status_label.pack(padx=15, pady=5)

        # Правая колонка: Список категорий
        right_col = ctk.CTkFrame(self, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_col, text="Существующие категории", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))

        self.categories_scroll = ctk.CTkScrollableFrame(right_col, fg_color="#18181b", corner_radius=10)
        self.categories_scroll.pack(fill="both", expand=True)

        self.load_categories()

    def load_categories(self):
        for widget in self.categories_scroll.winfo_children():
            widget.destroy()

        ok, categories, err = api.get_categories(self.controller.token)
        if ok and categories:
            for cat in categories:
                row = ctk.CTkFrame(self.categories_scroll, fg_color="#27272a", corner_radius=8)
                row.pack(fill="x", pady=4, padx=5)

                ctk.CTkLabel(row, text=cat["name"], font=ctk.CTkFont(size=14)).pack(side="left", padx=15, pady=10)
                ctk.CTkLabel(row, text=f"ID: {cat['id']}", font=ctk.CTkFont(size=12), text_color="gray").pack(side="right", padx=15)
        else:
            ctk.CTkLabel(self.categories_scroll, text="Категорий пока нет. Создайте первую слева!", text_color="gray").pack(pady=20)

    def on_submit(self):
        name = self.name_entry.get().strip()

        if not name:
            self.status_label.configure(text="Введите название категории!", text_color="#FF5555")
            return

        success, msg = api.create_category(self.controller.token, name)
        if success:
            self.status_label.configure(text=msg, text_color="#55FF55")
            self.name_entry.delete(0, "end")
            self.load_categories()
        else:
            self.status_label.configure(text=msg, text_color="#FF5555")