#! /usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading

class networkGui(tk.Tk):

    def __init__(self, type, title):
        super().__init__()

        # Add title passed as argument
        self.title(title)

        # Start scrolled text instance
        stFrame = ttk.Frame(self, )
        st = ScrolledText(self, width=50, height=10)
        st.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        # Start progress bar 

        # If its the sender add an input field
        if type == 'sender':
            text = tk.StringVar()
            textBox = ttk.Entry(self, textvariable=text)
            textBox.pack()