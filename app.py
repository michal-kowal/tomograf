import tkinter as tk
from tkinter import filedialog

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.choose_button = tk.Button(self, text="Wybierz plik", command=self.choose_file)
        self.choose_button.pack()

        self.file_label = tk.Label(self, text="")
        self.file_label.pack()

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        self.file_label.config(text=file_path)