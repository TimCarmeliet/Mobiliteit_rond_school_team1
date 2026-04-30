import tkinter as tk
from tkinter import ttk, messagebox

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobiliteit rond de School - Project")
        self.geometry("950x650")
        self.controller = None
        
        style = ttk.Style(self)
        style.theme_use('clam')
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_beheer = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_beheer, text='Data Beheer (CRUD)')
        self.notebook.add(self.tab_dashboard, text='Dashboard & Analyses')
        
        self._build_beheer_tab()
        
        ttk.Label(self.tab_dashboard, text="Hier komen later de tabellen en grafieken.", font=("Arial", 12)).pack(pady=20)

    def _build_beheer_tab(self):
        # Maak een sub-notebook voor de CRUD operaties
        self.beheer_notebook = ttk.Notebook(self.tab_beheer)
        self.beheer_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.tab_studenten = ttk.Frame(self.beheer_notebook)
        self.tab_vervoer = ttk.Frame(self.beheer_notebook)
        self.tab_logs = ttk.Frame(self.beheer_notebook)

        self.beheer_notebook.add(self.tab_studenten, text='Studenten Beheren')
        self.beheer_notebook.add(self.tab_vervoer, text='Vervoersmiddelen')
        self.beheer_notebook.add(self.tab_logs, text='Verplaatsingen (Logs)')

        self._build_student_ui()
        self._build_vervoer_ui()
        self._build_logs_ui()

    # --- UI: Studenten ---
    def _build_student_ui(self):
        form_frame = ttk.Frame(self.tab_studenten)
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
        
        btn_frame = ttk.Frame(self.tab_studenten)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Toevoegen", command=lambda: self.controller.add_student()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Aanpassen", command=lambda: self.controller.update_student()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verwijderen", command=lambda: self.controller.delete_student()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Leegmaken", command=self.clear_student_form).pack(side="left", padx=5)
        
        self.tree_students = ttk.Treeview(self.tab_studenten, columns=("id", "naam", "klas", "afstand"), show="headings")
        for col, text in zip(("id", "naam", "klas", "afstand"), ("ID", "Naam", "Klas", "Afstand (km)")):
            self.tree_students.heading(col, text=text)
        self.tree_students.column("id", width=50)
        self.tree_students.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_students.bind("<<TreeviewSelect>>", self._on_select_student)

    # --- UI: Vervoersmiddelen ---
    def _build_vervoer_ui(self):
        form_frame = ttk.Frame(self.tab_vervoer)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form_frame, text="Type Vervoer:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_vervoer_type = ttk.Entry(form_frame)
        self.entry_vervoer_type.grid(row=0, column=1, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self.tab_vervoer)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Toevoegen", command=lambda: self.controller.add_transport()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verwijderen", command=lambda: self.controller.delete_transport()).pack(side="left", padx=5)
        
        self.tree_trans = ttk.Treeview(self.tab_vervoer, columns=("id", "type"), show="headings")
        self.tree_trans.heading("id", text="ID")
        self.tree_trans.heading("type", text="Type")
        self.tree_trans.column("id", width=50)
        self.tree_trans.pack(fill="both", expand=True, padx=10, pady=10)

    # --- UI: Verplaatsingen (Logs) ---
    def _build_logs_ui(self):
        form_frame = ttk.Frame(self.tab_logs)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form_frame, text="Student:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_student = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_student.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Vervoer:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_vervoer = ttk.Combobox(form_frame, state="readonly", width=15)
        self.combo_vervoer.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Datum (DD/MM/YYYY):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_datum = ttk.Entry(form_frame)
        self.entry_datum.grid(row=0, column=5, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self.tab_logs)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Toevoegen", command=lambda: self.controller.add_log()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Verwijderen", command=lambda: self.controller.delete_log()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Vernieuw Lijsten", command=lambda: self.controller.refresh_all_tables()).pack(side="left", padx=5)

        self.tree_logs = ttk.Treeview(self.tab_logs, columns=("id", "student", "vervoer", "datum"), show="headings")
        for col, text in zip(("id", "student", "vervoer", "datum"), ("ID", "Student ID", "Transport ID", "Datum")):
            self.tree_logs.heading(col, text=text)
        self.tree_logs.column("id", width=50)
        self.tree_logs.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Helpers voor de Controller ---
    def set_controller(self, controller):
        self.controller = controller

    def show_error(self, message):
        messagebox.showerror("Fout", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)

    # Formulier Helpers Studenten
    def get_student_form_data(self): return {"naam": self.entry_naam.get(), "klas": self.entry_klas.get(), "afstand": self.entry_afstand.get()}
    def clear_student_form(self): [e.delete(0, tk.END) for e in (self.entry_naam, self.entry_klas, self.entry_afstand)]
    def _on_select_student(self, event):
        selected = self.tree_students.selection()
        if selected:
            v = self.tree_students.item(selected[0])['values']
            self.clear_student_form()
            self.entry_naam.insert(0, v[1]); self.entry_klas.insert(0, v[2]); self.entry_afstand.insert(0, v[3])

    # Treeview Fillers
    def populate_tree(self, tree, data):
        for item in tree.get_children(): tree.delete(item)
        for row in data: tree.insert("", tk.END, values=row)

    def get_selected_id(self, tree):
        selected = tree.selection()
        return tree.item(selected[0])['values'][0] if selected else None