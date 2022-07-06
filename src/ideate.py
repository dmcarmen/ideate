import tkinter as tk

from Model import *
from View import *
from Controller import *

import sv_ttk


class App(tk.Tk):
    """IDEATE app class.

    Args:
        tk (_type_): _description_
    """

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
# sv_ttk.set_theme("dark")  # Set dark theme

app.mainloop()
