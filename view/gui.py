import tkinter as tk
from tkinter import ttk, messagebox

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobiliteit rond de School - Project")
        self.geometry("1000x750") # Iets ruimer gemaakt voor de grafieken
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
        self._build_dashboard_tab() # Nieuwe dashboard UI initialisatie

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

    # --- UI: DASHBOARD (NIEUW!) ---
    def _build_dashboard_tab(self):
        """Bouwt de interface voor de dashboards en analyses met tabbladen."""
        self.dashboard_notebook = ttk.Notebook(self.tab_dashboard)
        self.dashboard_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.tab_overzicht = ttk.Frame(self.dashboard_notebook)
        self.tab_vervoer_analyse = ttk.Frame(self.dashboard_notebook)
        self.tab_afstand_analyse = ttk.Frame(self.dashboard_notebook)
        self.tab_klassen_analyse = ttk.Frame(self.dashboard_notebook)

        self.dashboard_notebook.add(self.tab_overzicht, text='Overzicht Data')
        self.dashboard_notebook.add(self.tab_vervoer_analyse, text='Vervoersmiddelen Analyse')
        self.dashboard_notebook.add(self.tab_afstand_analyse, text='Afstand Analyse')
        self.dashboard_notebook.add(self.tab_klassen_analyse, text='Klassenanalyse')

        self._build_overzicht_ui()
        self._build_vervoer_analyse_ui()
        self._build_afstand_analyse_ui()
        self._build_klassen_analyse_ui()

    def _build_overzicht_ui(self):
        """Tabblad 1: Dynamische weergave van één gekozen tabel."""
        top_frame = ttk.Frame(self.tab_overzicht)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Kies te bekijken tabel:").pack(side='left', padx=5)
        self.combo_overzicht_tabel = ttk.Combobox(top_frame, values=['Students', 'Transport', 'Mobility_log'], state='readonly')
        self.combo_overzicht_tabel.set('Students')
        self.combo_overzicht_tabel.pack(side='left', padx=5)
        self.combo_overzicht_tabel.bind("<<ComboboxSelected>>", lambda e: self.controller.laad_overzicht_tabel())
        
        self.tree_overzicht = ttk.Treeview(self.tab_overzicht)
        self.tree_overzicht.pack(fill='both', expand=True, padx=10, pady=10)

    def _build_vervoer_analyse_ui(self):
        """Tabblad 2: Verdeling van de vervoersmiddelen met een tabel en staafdiagram."""
        self.tree_vervoer_stat = ttk.Treeview(self.tab_vervoer_analyse, columns=("Vervoersmiddel", "Aantal Ritten", "Percentage"), show="headings", height=5)
        for h in ("Vervoersmiddel", "Aantal Ritten", "Percentage"):
            self.tree_vervoer_stat.heading(h, text=h)
            self.tree_vervoer_stat.column(h, anchor="center")
        self.tree_vervoer_stat.pack(fill='x', padx=10, pady=10)
        
        self.canvas_vervoer = tk.Canvas(self.tab_vervoer_analyse, bg='white', height=280)
        self.canvas_vervoer.pack(fill='both', expand=True, padx=10, pady=5)

    def _build_afstand_analyse_ui(self):
        """Tabblad 3: Analyse van de afstanden tot school."""
        self.lbl_gem_afstand_totaal = ttk.Label(self.tab_afstand_analyse, text="Algemene gemiddelde afstand tot school: -- km", font=("Arial", 11, "bold"))
        self.lbl_gem_afstand_totaal.pack(padx=10, pady=10, anchor='w')
        
        self.tree_afstand_stat = ttk.Treeview(self.tab_afstand_analyse, columns=("Vervoersmiddel", "Gemiddelde Afstand (km)", "Totaal Aantal km (Extra)"), show="headings", height=5)
        for h in ("Vervoersmiddel", "Gemiddelde Afstand (km)", "Totaal Aantal km (Extra)"):
            self.tree_afstand_stat.heading(h, text=h)
            self.tree_afstand_stat.column(h, anchor="center")
        self.tree_afstand_stat.pack(fill='x', padx=10, pady=10)
        
        self.canvas_afstand = tk.Canvas(self.tab_afstand_analyse, bg='white', height=250)
        self.canvas_afstand.pack(fill='both', expand=True, padx=10, pady=5)

    def _build_klassen_analyse_ui(self):
        """Tabblad 4: Statistieken per klas."""
        self.tree_klassen_stat = ttk.Treeview(self.tab_klassen_analyse, columns=("Klas", "Aantal Leerlingen", "Gemiddelde Afstand (km)", "Verdeling Vervoersmiddelen"), show="headings", height=6)
        for h in ("Klas", "Aantal Leerlingen", "Gemiddelde Afstand (km)", "Verdeling Vervoersmiddelen"):
            self.tree_klassen_stat.heading(h, text=h)
            if h == "Verdeling Vervoersmiddelen":
                self.tree_klassen_stat.column(h, width=350, anchor="w")
            else:
                self.tree_klassen_stat.column(h, width=120, anchor="center")
        self.tree_klassen_stat.pack(fill='x', padx=10, pady=10)
        
        self.canvas_klassen = tk.Canvas(self.tab_klassen_analyse, bg='white', height=230)
        self.canvas_klassen.pack(fill='both', expand=True, padx=10, pady=5)

    def setup_overzicht_tree(self, headers, data):
        """Stelt de kolommen van de ruwe tabelweergave dynamisch in."""
        self.tree_overzicht["columns"] = headers
        self.tree_overzicht["show"] = "headings"
        for h in headers:
            self.tree_overzicht.heading(h, text=h)
            self.tree_overzicht.column(h, width=150, anchor="center")
        self.populate_tree(self.tree_overzicht, data)

    def teken_grafiek(self, canvas, data_dict, titel):
        """Universele pure-Python grafiek-tekenfunctie met Tkinter Canvas."""
        canvas.delete("all")
        if not data_dict:
            return
        
        c_width = int(canvas.winfo_width()) if canvas.winfo_width() > 1 else int(canvas['width'])
        c_height = int(canvas.winfo_height()) if canvas.winfo_height() > 1 else int(canvas['height'])
        
        margin_left, margin_bottom, margin_top, margin_right = 60, 40, 40, 30
        graph_width = c_width - margin_left - margin_right
        graph_height = c_height - margin_top - margin_bottom
        
        # Titel & Assen
        canvas.create_text(c_width / 2, 20, text=titel, font=("Arial", 11, "bold"), fill="black")
        canvas.create_line(margin_left, c_height - margin_bottom, c_width - margin_right, c_height - margin_bottom, width=2, fill="black")
        canvas.create_line(margin_left, margin_top, margin_left, c_height - margin_bottom, width=2, fill="black")
        
        max_val = max(data_dict.values()) if max(data_dict.values()) > 0 else 1
        num_items = len(data_dict)
        bar_width = (graph_width / num_items) * 0.6
        spacing = (graph_width / num_items) * 0.4
        
        for i, (key, value) in enumerate(data_dict.items()):
            x_start = margin_left + (i * (graph_width / num_items)) + (spacing / 2)
            x_end = x_start + bar_width
            
            bar_h = (value / max_val) * graph_height
            y_start = c_height - margin_bottom - bar_h
            y_end = c_height - margin_bottom
            
            # Teken staaf en labels
            canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="#4a90e2", outline="#2a60a2")
            canvas.create_text((x_start + x_end) / 2, y_start - 10, text=f"{value}", font=("Arial", 9, "bold"), fill="black")
            canvas.create_text((x_start + x_end) / 2, y_end + 15, text=str(key), font=("Arial", 9), fill="black")

    # --- Helpers voor de Controller (Onveranderd) ---
    def set_controller(self, controller):
        self.controller = controller

    def show_error(self, message):
        messagebox.showerror("Fout", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)

    def get_student_form_data(self): 
        return {"naam": self.entry_naam.get(), "klas": self.entry_klas.get(), "afstand": self.entry_afstand.get()}
    
    def clear_student_form(self): 
        [e.delete(0, tk.END) for e in (self.entry_naam, self.entry_klas, self.entry_afstand)]
        
    def _on_select_student(self, event):
        selected = self.tree_students.selection()
        if selected:
            v = self.tree_students.item(selected[0])['values']
            self.clear_student_form()
            self.entry_naam.insert(0, v[1]); self.entry_klas.insert(0, v[2]); self.entry_afstand.insert(0, v[3])

    def populate_tree(self, tree, data):
        for item in tree.get_children(): tree.delete(item)
        for row in data: tree.insert("", tk.END, values=row)

    def get_selected_id(self, tree):
        selected = tree.selection()
        return tree.item(selected[0])['values'][0] if selected else None