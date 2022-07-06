import textwrap
import tkinter as tk
from tkinter import ttk
import pandas as pd


class ToolTip(object):
    """Class to create a ToolTip (text widget over some widget if it is hovered for example)
    """

    def __init__(self, widget):
        """
        Args:
            widget (tkinter widget): widget over which appears text.
        """
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        """Display text in tooltip window

        Args:
            text (str): text that appears when self.widget is hovered.
        """
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(tw, text=self.text, justify=tk.LEFT,
                          background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                          font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        """Hides ToolTip.
        """
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def createToolTip(widget, text):
    """Creates a ToolTip instance.

    Args:
        widget (tkinter widget): widget over which appears text when hovered.
        text (str): text that appears over the widget.
    """
    toolTip = ToolTip(widget)

    text = "\n ".join(textwrap.wrap(
        text, width=30, break_long_words=False))

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def popup(msg):
    """popup windows with a message.

    Args:
        msg (str): message to show.
    """
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack(pady=(0, 5))
    popup.mainloop()


class EntryWithPlaceholder(tk.Entry):
    """Create Entry widget with placeholder. 

    Args:
        tk.Entry
    """

    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        """

        Args:
            master (master window, optional): master window where widget is located. Defaults to None.
            placeholder (str, optional): placeholder text for the entry. Defaults to "PLACEHOLDER".
            color (str, optional): placeholder text. Defaults to 'grey'.
        """
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        """Writes placeholder on the Entry.
        """
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        """Hides placeholder when Entry is focused.
        """
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        """Shows placeholder when Entry is unfocused.
        """
        if not self.get():
            self.put_placeholder()


class HyperlinkManager:
    """Class to manage Hyperlinks.
    """

    def __init__(self, text):
        """

        Args:
            text (str): link text.
        """
        self.text = text

        self.text.tag_config("hyper", foreground="blue", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)

        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return


def check_format(shape_file, datos_vars):
    """Function to check if tabulated file format is what we expect. It expects datos_vars 
    variables to be the columns of the file, and if velocity (v) is on the list, it expects 
    'vx', 'vy' and 'vz' columns. It is case insensitive and it expects the delimitator to be \t.

    Args:
        shape_file (str): complete path to where the tabulated data file is located.
        datos_vars (list): list with the variables name expected to appear on the file header.

    Raises:
        Exception: _description_
    """
    df = pd.read_csv(shape_file, sep='\t')
    flag = True
    err_msg = ""
    df_columns_lower = [x.lower() for x in df.columns]
    for var in datos_vars.keys():
        if datos_vars[var] is True:
            if var != "velocity":
                if var not in df_columns_lower:
                    err_msg += ("La columna " + str(var) +
                                " no está en el fichero.\n")
                    flag = False
            else:
                for v in ['vx', 'vy', 'vz']:
                    if v not in df_columns_lower:
                        err_msg += ("La columna " + str(var) +
                                    ' (' + str(v) + ") no está en el fichero.\n")
                        flag = False
    if flag is False:
        raise Exception(
            err_msg + "El fichero no tiene el formato correcto.")


def str2bool(txt):
    """Transforms str (true o 1) to boolean (True).

    Args:
        txt (str): text to transform.

    Returns:
        bool: True if text equals true or 1, else False.
    """
    return txt.lower() in ['true', '1']
