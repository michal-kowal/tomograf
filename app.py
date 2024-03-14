import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedTk
from tkcalendar import DateEntry
from simulation import simulate
from PIL import Image, ImageTk

class Application(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        
        self.configure(background="#f5f6f7")

        self.title("Tomograf")
        self.geometry("1000x700")

        self.file_path = None

        self.title_label = ttk.Label(self, text="Tomograf", font=(24))
        self.title_label.pack(pady=10)

        self.file_frame = ttk.Frame(self)
        self.file_frame.pack(pady=10)

        self.choose_button = ttk.Button(self.file_frame, text="Wybierz plik", command=self.choose_file)
        self.choose_button.pack(side=tk.LEFT)

        self.file_label = ttk.Label(self.file_frame, text="")
        self.file_label.pack(side=tk.LEFT)

        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(pady=10)

        self.angle_entry = self.create_entry(self.entry_frame, "Kąt przesuwania emitera")
        self.detectors_entry = self.create_entry(self.entry_frame, "Liczba detektorów")
        self.span_entry = self.create_entry(self.entry_frame, "Rozpiętość kątowa detektorów")

        self.checkbox_frame = ttk.Frame(self)
        self.checkbox_frame.pack(pady=10)

        self.step_var = tk.IntVar()
        self.step_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Wyświetlaj kroki pośrednie", variable=self.step_var)
        self.step_checkbox.pack(side=tk.LEFT)

        self.filter_var = tk.IntVar()
        self.filter_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Użyj filtrowania", variable=self.filter_var)
        self.filter_checkbox.pack(side=tk.LEFT)

        self.dicom_checkbox = ttk.Checkbutton(self.checkbox_frame, text="Generuj plik dicom", command=self.toggle_dicom_fields)
        self.dicom_checkbox.pack(side=tk.LEFT)

        self.dicom_fields_frame = ttk.Frame(self)
        self.dicom_fields_frame.pack(pady=10)

        self.first_name_entry = self.create_entry(self.dicom_fields_frame, "Imię pacjenta")
        self.last_name_entry = self.create_entry(self.dicom_fields_frame, "Nazwisko pacjenta")
        self.pesel_entry = self.create_entry(self.dicom_fields_frame, "PESEL")
        
        date_frame = ttk.Frame(self.dicom_fields_frame)
        date_frame.pack(side=tk.LEFT, padx=10)
        date_label = ttk.Label(date_frame, text="Data badania")
        date_label.pack(side=tk.TOP)
        self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, selectbackground='red')
        self.date_entry.pack(side=tk.BOTTOM)

        self.comment_entry = self.create_entry(self.dicom_fields_frame, "Komentarz do badania")

        self.dicom_fields_frame.pack_forget()

        self.simulate_button = ttk.Button(self, text="Symuluj", command=self.run_simulation)
        self.simulate_button.pack(pady=10)

        self.photo_frame = ttk.Frame(self)
        self.photo_frame.pack(pady=10)

    def toggle_dicom_fields(self):
        if self.dicom_fields_frame.winfo_viewable():
            self.dicom_fields_frame.pack_forget()
        else:
            self.dicom_fields_frame.pack()

        if self.photo_frame.winfo_viewable():
            self.photo_frame.pack_forget()

    def choose_file(self):
        self.file_path = filedialog.askopenfilename()
        self.file_label.config(text=self.file_path)

    def create_entry(self, parent, text):
        frame = ttk.Frame(parent)

        label = ttk.Label(frame, text=text)
        label.pack(side=tk.TOP)

        entry = ttk.Entry(frame)
        entry.pack(side=tk.TOP)

        frame.pack(side=tk.LEFT, padx=20)

        return entry
    
    def display_images(self):
        if not self.photo_frame.winfo_viewable():
            self.photo_frame.pack(pady=10)
        
        for widget in self.photo_frame.winfo_children():
            widget.destroy()
        
        img1 = Image.open(self.file_path)
        img2 = Image.open("./result/sinogram.png")
        img3 = Image.open("./result/result.png")

        img1 = img1.resize((250, 250))
        img2 = img2.resize((250, 250))
        img3 = img3.resize((250, 250))

        img1 = ImageTk.PhotoImage(img1)
        img2 = ImageTk.PhotoImage(img2)
        img3 = ImageTk.PhotoImage(img3)

        image_title_frame = ttk.Frame(self.photo_frame)
        image_title_frame.pack()

        # Tworzymy etykiety dla tytułów i obrazów, dodając je do ramki
        img1_label_text = ttk.Label(image_title_frame, text="Obraz wejściowy")
        img1_label_text.grid(row=0, column=0, padx=(0, 10))

        img2_label_text = ttk.Label(image_title_frame, text="Sinogram")
        img2_label_text.grid(row=0, column=1, padx=(0, 10))

        img3_label_text = ttk.Label(image_title_frame, text="Wynik")
        img3_label_text.grid(row=0, column=2, padx=(0, 10))

        img1_label = ttk.Label(image_title_frame, image=img1)
        img1_label.image = img1
        img1_label.grid(row=1, column=0)

        img2_label = ttk.Label(image_title_frame, image=img2)
        img2_label.image = img2
        img2_label.grid(row=1, column=1)

        img3_label = ttk.Label(image_title_frame, image=img3)
        img3_label.image = img3
        img3_label.grid(row=1, column=2)




    def run_simulation(self):
        simulate(self.file_path, int(self.angle_entry.get()), int(self.detectors_entry.get()), int(self.span_entry.get()),
                 self.filter_var.get(), self.step_var.get())
        self.display_images()
