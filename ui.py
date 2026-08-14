import customtkinter as ctk
from views.auth_view import AuthView
from views.main_view import MainView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YNAB Финансы")
        self.geometry("420x700")
        self.resizable(False, False)

        self.token = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_auth_view()

    def show_auth_view(self):
        self._switch_view(AuthView)

    def show_main_view(self):
        self._switch_view(MainView)

    def _switch_view(self, view_class):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        frame = view_class(parent=self.container, controller=self)
        frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()