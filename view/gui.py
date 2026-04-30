import tkinter as tk
from tkinter import ttk, messagebox

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobiliteit rond de School - Project")
        self.geometry("900x600")
        self.controller = None
        
        # Basis styling
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Notebook (Tabbladen)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_beheer = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_beheer, text='Data Beheer (CRUD)')
        self.notebook.add(self.tab_dashboard, text='Dashboard & Analyses')
        
        # Bouw de inhoud van de tabbladen
        self._build_beheer_tab()
        
        # Tijdelijke opvulling voor het dashboard
        ttk.Label(self.tab_dashboard, text="Hier komen later de tabellen en grafieken.", font=("Arial", 12)).pack(pady=20)

    def _build_beheer_tab(self):
        """Bouwt de interface voor het beheren van de data (Studenten)"""
        # --- Sectie: Studenten Beheren ---
        frame_students = ttk.LabelFrame(self.tab_beheer, text="Studenten Beheren")
        frame_students.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Invoerformulier
        form_frame = ttk.Frame(frame_students)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form_frame, text="Naam:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_naam = ttk.Entry(form_frame)
        self.entry_naam.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Klas:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_klas = ttk.Entry(form_frame)
        self.entry_klas.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Afstand (km):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_afstand = ttk.Entry(form_frame)
        self.entry_afstand.grid(row=0, column=5, padx=5, pady=5)
        
        # Knoppen
        btn_frame = ttk.Frame(frame_students)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Toevoegen", command=self._on_add_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Aanpassen", command=self._on_update_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verwijderen", command=self._on_delete_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Velden Leegmaken", command=self.clear_student_form).pack(side="left", padx=5)
        
        # Tabel (Treeview)
        columns = ("id", "naam", "klas", "afstand")
        self.tree_students = ttk.Treeview(frame_students, columns=columns, show="headings")
        self.tree_students.heading("id", text="ID")
        self.tree_students.heading("naam", text="Naam")
        self.tree_students.heading("klas", text="Klas")
        self.tree_students.heading("afstand", text="Afstand (km)")
        
        self.tree_students.column("id", width=50)
        self.tree_students.column("afstand", width=100)
        
        self.tree_students.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Klik-event op de tabel (zodat de velden automatisch gevuld worden als je een rij aanklikt)
        self.tree_students.bind("<<TreeviewSelect>>", self._on_select_student)

    # --- Koppeling met de Controller ---
    def set_controller(self, controller):
        self.controller = controller

    # --- Functies voor de View Logica ---
    def get_student_form_data(self):
        """Haalt de tekst uit de invoervelden."""
        return {
            "naam": self.entry_naam.get(),
            "klas": self.entry_klas.get(),
            "afstand": self.entry_afstand.get()
        }

    def clear_student_form(self):
        """Maakt de invoervelden leeg."""
        self.entry_naam.delete(0, tk.END)
        self.entry_klas.delete(0, tk.END)
        self.entry_afstand.delete(0, tk.END)

    def populate_student_tree(self, studenten):
        """Vult de tabel met data uit de database."""
        # Leeg eerst de huidige tabel
        for item in self.tree_students.get_children():
            self.tree_students.delete(item)
        # Vul aan met nieuwe data
        for student in studenten:
            self.tree_students.insert("", tk.END, values=student)

    def get_selected_student_id(self):
        """Haalt het ID op van de geselecteerde rij in de tabel."""
        selected = self.tree_students.selection()
        if selected:
            return self.tree_students.item(selected[0])['values'][0]
        return None

    def _on_select_student(self, event):
        """Vult het formulier als er op een rij geklikt wordt."""
        selected = self.tree_students.selection()
        if selected:
            values = self.tree_students.item(selected[0])['values']
            self.clear_student_form()
            self.entry_naam.insert(0, values[1])
            self.entry_klas.insert(0, values[2])
            self.entry_afstand.insert(0, values[3])

    # --- Knoppen sturen acties naar Controller ---
    def _on_add_student(self):
        if self.controller:
            self.controller.add_student()

    def _on_update_student(self):
        if self.controller:
            self.controller.update_student()

    def _on_delete_student(self):
        if self.controller:
            self.controller.delete_student()

    # --- Pop-ups ---
    def show_error(self, message):
        messagebox.showerror("Fout", message)

    def show_info(self, message):
        messagebox.showinfo("Succes", message)