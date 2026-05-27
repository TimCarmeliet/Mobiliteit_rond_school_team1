import tkinter as tk
from tkinter import ttk

class StudentenBeheerFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Form fields
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Naam:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_naam = ttk.Entry(form_frame, width=20)
        self.entry_naam.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Klas:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_klas = ttk.Entry(form_frame, width=10)
        self.entry_klas.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Afstand (km):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_afstand = ttk.Entry(form_frame, width=10)
        self.entry_afstand.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Toevoegen", command=lambda: self.view.controller.add_student()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✏️ Aanpassen", command=lambda: self.view.controller.update_student()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Verwijderen", style="Danger.TButton", command=lambda: self.view.controller.delete_student()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 Leegmaken", command=self.view.clear_student_form).pack(side="left", padx=5)
        
        # List with Scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_students = ttk.Treeview(list_frame, columns=("id", "naam", "klas", "afstand"), show="headings")
        for col, text in zip(("id", "naam", "klas", "afstand"), ("ID", "Naam", "Klas", "Afstand (km)")):
            self.tree_students.heading(col, text=text)
            self.tree_students.column(col, anchor="w" if col == "naam" else "center", width=250 if col == "naam" else 80)
        self.tree_students.pack(side='left', fill="both", expand=True)
        self.tree_students.bind("<<TreeviewSelect>>", self.view._on_select_student)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_students.yview)
        self.tree_students.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')


class VervoersmiddelenFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Form fields
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Type Vervoer:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_vervoer_type = ttk.Entry(form_frame, width=25)
        self.entry_vervoer_type.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Toevoegen", command=lambda: self.view.controller.add_transport()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Verwijderen", style="Danger.TButton", command=lambda: self.view.controller.delete_transport()).pack(side="left", padx=5)
        
        # List with Scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_trans = ttk.Treeview(list_frame, columns=("id", "type"), show="headings")
        self.tree_trans.heading("id", text="ID")
        self.tree_trans.heading("type", text="Type Vervoersmiddel")
        self.tree_trans.column("id", anchor="center", width=80)
        self.tree_trans.column("type", anchor="center", width=300)
        self.tree_trans.pack(side='left', fill="both", expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_trans.yview)
        self.tree_trans.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')


class VerplaatsingenFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Form fields
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Student:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_student = ttk.Combobox(form_frame, state="readonly", width=32)
        self.combo_student.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Vervoer:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_vervoer = ttk.Combobox(form_frame, state="readonly", width=18)
        self.combo_vervoer.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Datum (YYYY-MM-DD):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_datum = ttk.Entry(form_frame, width=15)
        self.entry_datum.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Toevoegen", command=lambda: self.view.controller.add_log()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Verwijderen", style="Danger.TButton", command=lambda: self.view.controller.delete_log()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Vernieuw Lijsten", command=lambda: self.view.controller.refresh_all_tables()).pack(side="left", padx=5)

        # List with Scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_logs = ttk.Treeview(list_frame, columns=("id", "student", "vervoer", "datum"), show="headings")
        for col, text in zip(("id", "student", "vervoer", "datum"), ("Ritten ID", "Student ID (Naam / Klas)", "Vervoer ID (Type)", "Datum")):
            self.tree_logs.heading(col, text=text)
            self.tree_logs.column(col, anchor="center", width=80 if col in ('id', 'datum') else 220)
        self.tree_logs.pack(side='left', fill="both", expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_logs.yview)
        self.tree_logs.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')


class AanwezighedenBeheerFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Form fields
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Student:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_student = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_student.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Datum (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_datum = ttk.Entry(form_frame, width=15)
        self.entry_datum.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        ttk.Label(form_frame, text="Status:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.combo_status = ttk.Combobox(form_frame, values=['aanwezig', 'afwezig', 'laat'], state="readonly", width=12)
        self.combo_status.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Registreer", command=lambda: self.view.controller.add_aanwezigheid()).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Verwijderen", style="Danger.TButton", command=lambda: self.view.controller.delete_aanwezigheid()).pack(side="left", padx=5)

        # List with Scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree_aanw = ttk.Treeview(list_frame, columns=("id", "student", "datum", "status"), show="headings")
        for col, text in zip(("id", "student", "datum", "status"), ("ID", "Student (Naam / Klas)", "Datum", "Status")):
            self.tree_aanw.heading(col, text=text)
            self.tree_aanw.column(col, anchor="center", width=80 if col == "id" else 200)
        self.tree_aanw.pack(side='left', fill="both", expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_aanw.yview)
        self.tree_aanw.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')