import tkinter as tk

from Model import *
from View import *
from Controller import *

import sv_ttk


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title('IDEATE')

        model = Model()
        controller = Controller(model=model)
        view = View(self, controller)
        view.pack()

        controller.set_view(view)


app = App()

sv_ttk.set_theme("light")  # Set light theme
#sv_ttk.set_theme("dark")  # Set dark theme

#sv_ttk.use_light_theme()  # Set light theme
#sv_ttk.use_dark_theme()  # Set dark theme

#sv_ttk.toggle_theme()


app.mainloop()
