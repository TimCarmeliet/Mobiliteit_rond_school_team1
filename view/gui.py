import tkinter as tk
from tkinter import ttk, messagebox

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobiliteit rond de School - Project")
        self.geometry("1100x850") 
        self.controller = None
        
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Geheugen voor de status van de grafieken (Standaard type)
        self.chart_states = {
            'vervoer': {'type': 'pie', 'data': {}, 'titel': ""},
            'afstand': {'type': 'bar', 'data': {}, 'titel': ""},
            'klassen': {'type': 'bar', 'data': {}, 'titel': ""},
            'categorie': {'type': 'pie', 'data': {}, 'titel': ""},
            'co2': {'type': 'bar', 'data': {}, 'titel': ""}
        }
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_beheer = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_beheer, text='Data Beheer (CRUD)')
        self.notebook.add(self.tab_dashboard, text='Dashboard & Analyses')
        
        self._build_beheer_tab()
        self._build_dashboard_tab()

    # ==========================================
    # BEHEER TABBLADEN (CRUD)
    # ==========================================
    def _build_beheer_tab(self):
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


    # ==========================================
    # DASHBOARD & ANALYSES TABBLADEN
    # ==========================================
    def _build_dashboard_tab(self):
        self.dashboard_notebook = ttk.Notebook(self.tab_dashboard)
        self.dashboard_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.tab_overzicht = ttk.Frame(self.dashboard_notebook)
        self.tab_vervoer_analyse = ttk.Frame(self.dashboard_notebook)
        self.tab_afstand_analyse = ttk.Frame(self.dashboard_notebook)
        self.tab_klassen_analyse = ttk.Frame(self.dashboard_notebook)
        self.tab_categorie_analyse = ttk.Frame(self.dashboard_notebook)
        self.tab_co2_analyse = ttk.Frame(self.dashboard_notebook)

        self.dashboard_notebook.add(self.tab_overzicht, text='Overzicht Data')
        self.dashboard_notebook.add(self.tab_vervoer_analyse, text='Vervoersmiddelen')
        self.dashboard_notebook.add(self.tab_afstand_analyse, text='Afstand Analyse')
        self.dashboard_notebook.add(self.tab_klassen_analyse, text='Klassenanalyse')
        self.dashboard_notebook.add(self.tab_categorie_analyse, text='Afstandscategorieën (Extra)')
        self.dashboard_notebook.add(self.tab_co2_analyse, text='CO₂ Analyse (Uitbreiding)')

        self._build_overzicht_ui()
        self._build_vervoer_analyse_ui()
        self._build_afstand_analyse_ui()
        self._build_klassen_analyse_ui()
        self._build_categorie_analyse_ui()
        self._build_co2_analyse_ui()

    def _build_overzicht_ui(self):
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
        self.tree_vervoer_stat = ttk.Treeview(self.tab_vervoer_analyse, columns=("Vervoersmiddel", "Aantal Ritten", "Percentage"), show="headings", height=5)
        for h in ("Vervoersmiddel", "Aantal Ritten", "Percentage"):
            self.tree_vervoer_stat.heading(h, text=h)
            self.tree_vervoer_stat.column(h, anchor="center")
        self.tree_vervoer_stat.pack(fill='x', padx=10, pady=10)
        
        # Toggle knop
        btn_frame = ttk.Frame(self.tab_vervoer_analyse)
        btn_frame.pack(fill='x', padx=15, pady=(5, 0))
        self.btn_toggle_vervoer = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.toggle_grafiek('vervoer'))
        self.btn_toggle_vervoer.pack(side='right')

        self.canvas_vervoer = tk.Canvas(self.tab_vervoer_analyse, bg='white', height=380)
        self.canvas_vervoer.pack(fill='both', expand=True, padx=15, pady=5)

    def _build_afstand_analyse_ui(self):
        self.lbl_gem_afstand_totaal = ttk.Label(self.tab_afstand_analyse, text="Algemene gemiddelde afstand tot school: -- km", font=("Arial", 11, "bold"))
        self.lbl_gem_afstand_totaal.pack(padx=10, pady=10, anchor='w')
        
        self.tree_afstand_stat = ttk.Treeview(self.tab_afstand_analyse, columns=("Vervoersmiddel", "Gemiddelde Afstand (km)", "Totaal Aantal km"), show="headings", height=5)
        for h in ("Vervoersmiddel", "Gemiddelde Afstand (km)", "Totaal Aantal km"):
            self.tree_afstand_stat.heading(h, text=h)
            self.tree_afstand_stat.column(h, anchor="center")
        self.tree_afstand_stat.pack(fill='x', padx=10, pady=10)
        
        # Toggle knop
        btn_frame = ttk.Frame(self.tab_afstand_analyse)
        btn_frame.pack(fill='x', padx=15, pady=(5, 0))
        self.btn_toggle_afstand = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.toggle_grafiek('afstand'))
        self.btn_toggle_afstand.pack(side='right')

        self.canvas_afstand = tk.Canvas(self.tab_afstand_analyse, bg='white', height=380)
        self.canvas_afstand.pack(fill='both', expand=True, padx=15, pady=5)

    def _build_klassen_analyse_ui(self):
        self.tree_klassen_stat = ttk.Treeview(self.tab_klassen_analyse, columns=("Klas", "Aantal Leerlingen", "Gemiddelde Afstand (km)", "Verdeling Vervoersmiddelen"), show="headings", height=6)
        for h in ("Klas", "Aantal Leerlingen", "Gemiddelde Afstand (km)", "Verdeling Vervoersmiddelen"):
            self.tree_klassen_stat.heading(h, text=h)
            if h == "Verdeling Vervoersmiddelen":
                self.tree_klassen_stat.column(h, width=350, anchor="w")
            else:
                self.tree_klassen_stat.column(h, width=120, anchor="center")
        self.tree_klassen_stat.pack(fill='x', padx=10, pady=10)
        
        # Toggle knop
        btn_frame = ttk.Frame(self.tab_klassen_analyse)
        btn_frame.pack(fill='x', padx=15, pady=(5, 0))
        self.btn_toggle_klassen = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.toggle_grafiek('klassen'))
        self.btn_toggle_klassen.pack(side='right')

        self.canvas_klassen = tk.Canvas(self.tab_klassen_analyse, bg='white', height=380)
        self.canvas_klassen.pack(fill='both', expand=True, padx=15, pady=5)

    def _build_categorie_analyse_ui(self):
        self.tree_categorie_stat = ttk.Treeview(self.tab_categorie_analyse, columns=("Categorie", "Totaal Ritten", "Populairste Vervoer", "Verdeling"), show="headings", height=4)
        for h in ("Categorie", "Totaal Ritten", "Populairste Vervoer", "Verdeling"):
            self.tree_categorie_stat.heading(h, text=h)
            self.tree_categorie_stat.column(h, width=150, anchor="center")
        self.tree_categorie_stat.column("Verdeling", width=350, anchor="w")
        self.tree_categorie_stat.pack(fill='x', padx=10, pady=10)
        
        # Toggle knop
        btn_frame = ttk.Frame(self.tab_categorie_analyse)
        btn_frame.pack(fill='x', padx=15, pady=(5, 0))
        self.btn_toggle_categorie = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.toggle_grafiek('categorie'))
        self.btn_toggle_categorie.pack(side='right')

        self.canvas_categorie = tk.Canvas(self.tab_categorie_analyse, bg='white', height=380)
        self.canvas_categorie.pack(fill='both', expand=True, padx=15, pady=5)

    def _build_co2_analyse_ui(self):
        filter_frame = ttk.LabelFrame(self.tab_co2_analyse, text="Filters")
        filter_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(filter_frame, text="Klas:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_filter_klas = ttk.Combobox(filter_frame, state="readonly", width=10)
        self.combo_filter_klas.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Vervoer:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_filter_vervoer = ttk.Combobox(filter_frame, state="readonly", width=10)
        self.combo_filter_vervoer.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="Afstand:").grid(row=0, column=4, padx=5, pady=5)
        self.combo_filter_afstand = ttk.Combobox(filter_frame, values=["Alle", "Kort (0-5 km)", "Middel (5.1-10 km)", "Lang (>10 km)"], state="readonly", width=15)
        self.combo_filter_afstand.set("Alle")
        self.combo_filter_afstand.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(filter_frame, text="Pas Filters Toe", command=lambda: self.controller.update_co2_analyse()).grid(row=0, column=6, padx=10, pady=5)

        self.tree_co2_stat = ttk.Treeview(self.tab_co2_analyse, columns=("Vervoersmiddel", "Aantal Ritten", "Totale CO2 (gram)"), show="headings", height=4)
        for h in ("Vervoersmiddel", "Aantal Ritten", "Totale CO2 (gram)"):
            self.tree_co2_stat.heading(h, text=h)
            self.tree_co2_stat.column(h, anchor="center")
        self.tree_co2_stat.pack(fill='x', padx=10, pady=10)

        # Toggle knop
        btn_frame = ttk.Frame(self.tab_co2_analyse)
        btn_frame.pack(fill='x', padx=15, pady=(5, 0))
        self.btn_toggle_co2 = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.toggle_grafiek('co2'))
        self.btn_toggle_co2.pack(side='right')

        self.canvas_co2 = tk.Canvas(self.tab_co2_analyse, bg='white', height=380)
        self.canvas_co2.pack(fill='both', expand=True, padx=15, pady=5)


    # ==========================================
    # TOGGLE & TEKENFUNCTIES
    # ==========================================
    def update_grafiek(self, chart_id, data=None, titel=None):
        """Update de opgeslagen data of forceert een hertweergave op basis van het huidige geselecteerde type."""
        if data is not None:
            self.chart_states[chart_id]['data'] = data
        if titel is not None:
            self.chart_states[chart_id]['titel'] = titel
            
        state = self.chart_states[chart_id]
        canvas = getattr(self, f"canvas_{chart_id}")
        btn = getattr(self, f"btn_toggle_{chart_id}")
        
        # Teken de juiste grafiek en update de knop tekst
        if state['type'] == 'pie':
            self.teken_cirkeldiagram(canvas, state['data'], state['titel'])
            btn.config(text=" Wissel naar Staafdiagram ")
        else:
            self.teken_grafiek(canvas, state['data'], state['titel'])
            btn.config(text=" Wissel naar Cirkeldiagram ")

    def toggle_grafiek(self, chart_id):
        """Flipt de state tussen staaf- en cirkeldiagram en roept update_grafiek aan."""
        current_type = self.chart_states[chart_id]['type']
        self.chart_states[chart_id]['type'] = 'bar' if current_type == 'pie' else 'pie'
        self.update_grafiek(chart_id)

    def setup_overzicht_tree(self, headers, data):
        self.tree_overzicht["columns"] = headers
        self.tree_overzicht["show"] = "headings"
        for h in headers:
            self.tree_overzicht.heading(h, text=h)
            self.tree_overzicht.column(h, width=150, anchor="center")
        self.populate_tree(self.tree_overzicht, data)

    def teken_grafiek(self, canvas, data_dict, titel):
        canvas.update_idletasks()
        canvas.delete("all")
        if not data_dict: return
        
        c_width = canvas.winfo_width()
        c_height = canvas.winfo_height()
        
        if c_width <= 1: c_width = 950
        if c_height <= 1: c_height = 380
        
        margin_left, margin_bottom, margin_top, margin_right = 80, 75, 50, 40 
        graph_width = c_width - margin_left - margin_right
        graph_height = c_height - margin_top - margin_bottom
        
        canvas.create_text(c_width / 2, 22, text=titel, font=("Arial", 12, "bold"), fill="#222222")
        
        max_val = max(data_dict.values()) if max(data_dict.values()) > 0 else 1
        num_items = len(data_dict)
        
        slot_width = graph_width / num_items
        bar_width = slot_width * 0.55
        spacing = slot_width * 0.45
        
        for i, (key, value) in enumerate(data_dict.items()):
            x_start = margin_left + (i * slot_width) + (spacing / 2)
            x_end = x_start + bar_width
            bar_h = (value / max_val) * graph_height
            y_start = c_height - margin_bottom - bar_h
            y_end = c_height - margin_bottom
            
            canvas.create_rectangle(x_start, y_start, x_end, y_end, fill="#5D9CEC", outline="#4A89DC", width=1.5)
            canvas.create_text((x_start + x_end) / 2, y_start - 12, text=f"{value}", font=("Arial", 9, "bold"), fill="#111111")
            
            y_offset = 18 if i % 2 == 0 else 38
            canvas.create_text((x_start + x_end) / 2, y_end + y_offset, text=str(key), font=("Arial", 9, "bold"), fill="#333333", justify="center")

        canvas.create_line(margin_left, c_height - margin_bottom, c_width - margin_right, c_height - margin_bottom, width=2, fill="#444444") 
        canvas.create_line(margin_left, margin_top, margin_left, c_height - margin_bottom, width=2, fill="#444444") 
        
        num_ticks = 4
        for t in range(num_ticks + 1):
            tick_val = (max_val / num_ticks) * t
            tick_y = c_height - margin_bottom - (t / num_ticks) * graph_height
            canvas.create_line(margin_left - 4, tick_y, margin_left, tick_y, width=1.5, fill="#444444")
            display_val = f"{int(tick_val)}" if tick_val.is_integer() else f"{tick_val:.1f}"
            canvas.create_text(margin_left - 10, tick_y, text=display_val, font=("Arial", 9), anchor="e", fill="#555555")

    def teken_cirkeldiagram(self, canvas, data_dict, titel):
        """Tekent een mooi, gekleurd cirkeldiagram (pie chart) met een duidelijke legenda ernaast."""
        canvas.update_idletasks()
        canvas.delete("all")
        
        totaal = sum(data_dict.values())
        if not data_dict or totaal == 0:
            return
            
        c_width = canvas.winfo_width()
        c_height = canvas.winfo_height()
        
        if c_width <= 1: c_width = 950
        if c_height <= 1: c_height = 380
        
        canvas.create_text(c_width / 2, 25, text=titel, font=("Arial", 12, "bold"), fill="#222222")
        
        margin = 60
        box_size = min(c_width / 2.5, c_height - margin * 1.5)
        cx = c_width / 3  
        cy = c_height / 2 + 10
        
        x0 = cx - box_size / 2
        y0 = cy - box_size / 2
        x1 = cx + box_size / 2
        y1 = cy + box_size / 2
        
        # Moderne kleurenpalet voor de taartpunten
        kleuren = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#1A535C", "#A2D5F2", "#FF9F1C", "#2EC4B6", "#E71D36"]
        start_angle = 90  
        
        legend_x = cx + box_size / 2 + 60
        legend_y = y0 + 30
        
        kleur_index = 0
        for key, value in data_dict.items():
            if value == 0: continue
                
            extent_angle = (value / totaal) * 360
            huidige_kleur = kleuren[kleur_index % len(kleuren)]
            
            canvas.create_arc(x0, y0, x1, y1, start=start_angle, extent=-extent_angle, fill=huidige_kleur, outline="white", width=2)
            canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 20, fill=huidige_kleur, outline="#777")
            
            pct = round((value / totaal) * 100, 1)
            lbl_text = f"{key}   |   {value} ({pct}%)"
            canvas.create_text(legend_x + 35, legend_y + 10, text=lbl_text, font=("Arial", 11), anchor="w", fill="#333333")
            
            start_angle -= extent_angle
            legend_y += 35
            kleur_index += 1

    # ==========================================
    # ALGEMEEN BEHEER
    # ==========================================
    def set_controller(self, controller): self.controller = controller
    def show_error(self, message): messagebox.showerror("Fout", message)
    def show_info(self, message): messagebox.showinfo("Info", message)
    def get_student_form_data(self): return {"naam": self.entry_naam.get(), "klas": self.entry_klas.get(), "afstand": self.entry_afstand.get()}
    def clear_student_form(self): [e.delete(0, tk.END) for e in (self.entry_naam, self.entry_klas, self.entry_afstand)]
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