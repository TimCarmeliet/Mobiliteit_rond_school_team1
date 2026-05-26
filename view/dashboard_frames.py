import tkinter as tk
from tkinter import ttk

class OverzichtDataFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Kies te bekijken tabel:").pack(side='left', padx=5)
        self.combo_overzicht_tabel = ttk.Combobox(top_frame, values=['Students', 'Transport', 'Mobility_log'], state='readonly', width=15)
        self.combo_overzicht_tabel.set('Students')
        self.combo_overzicht_tabel.pack(side='left', padx=5)
        self.combo_overzicht_tabel.bind("<<ComboboxSelected>>", lambda e: self.view.controller.laad_overzicht_tabel())
        
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tree_overzicht = ttk.Treeview(list_frame)
        self.tree_overzicht.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_overzicht.yview)
        self.tree_overzicht.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')


class VervoersmiddelenAnalyseFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Stats list card
        list_card = ttk.LabelFrame(self, text="Verdeling Vervoerskeuzes")
        list_card.pack(fill='x', padx=15, pady=10)

        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill='x', padx=10, pady=10)

        self.tree_vervoer_stat = ttk.Treeview(tree_frame, columns=("Vervoersmiddel", "Aantal Ritten", "Percentage"), show="headings", height=4)
        for h in ("Vervoersmiddel", "Aantal Ritten", "Percentage"):
            self.tree_vervoer_stat.heading(h, text=h)
            self.tree_vervoer_stat.column(h, anchor="center", width=150)
        self.tree_vervoer_stat.pack(side='left', fill='both', expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_vervoer_stat.yview)
        self.tree_vervoer_stat.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        
        # Toggle button and Canvas Card
        chart_card = ttk.LabelFrame(self, text="Visuele Grafiek")
        chart_card.pack(fill='both', expand=True, padx=15, pady=(5, 15))

        btn_frame = ttk.Frame(chart_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_vervoer = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('vervoer'))
        self.btn_toggle_vervoer.pack(side='right')

        # Clean canvas
        self.canvas_vervoer = tk.Canvas(chart_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_vervoer.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class AfstandAnalyseFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Stats card
        list_card = ttk.LabelFrame(self, text="Afstandsgegevens per Vervoermiddel")
        list_card.pack(fill='x', padx=15, pady=10)

        info_frame = ttk.Frame(list_card)
        info_frame.pack(fill='x', padx=10, pady=5)
        self.lbl_gem_afstand_totaal = ttk.Label(info_frame, text="Algemene gemiddelde afstand tot school: -- km", font=("Arial", 10, "bold"))
        self.lbl_gem_afstand_totaal.pack(anchor='w')
        
        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill='x', padx=10, pady=(5, 10))

        self.tree_afstand_stat = ttk.Treeview(tree_frame, columns=("Vervoersmiddel", "Gemiddelde Afstand (km)", "Totaal Aantal km"), show="headings", height=4)
        for h in ("Vervoersmiddel", "Gemiddelde Afstand (km)", "Totaal Aantal km"):
            self.tree_afstand_stat.heading(h, text=h)
            self.tree_afstand_stat.column(h, anchor="center", width=150)
        self.tree_afstand_stat.pack(side='left', fill='both', expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_afstand_stat.yview)
        self.tree_afstand_stat.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        
        # Chart Card
        chart_card = ttk.LabelFrame(self, text="Visuele Grafiek")
        chart_card.pack(fill='both', expand=True, padx=15, pady=(5, 15))

        btn_frame = ttk.Frame(chart_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_afstand = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('afstand'))
        self.btn_toggle_afstand.pack(side='right')

        self.canvas_afstand = tk.Canvas(chart_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_afstand.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class KlassenAnalyseFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Stats list card
        list_card = ttk.LabelFrame(self, text="Verplaatsingsgedrag per Klas")
        list_card.pack(fill='x', padx=15, pady=10)

        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill='x', padx=10, pady=10)

        self.tree_klassen_stat = ttk.Treeview(tree_frame, columns=("Klas", "Aantal Leerlingen", "Gemiddelde Afstand (km)", "Verdeling Vervoersmiddelen"), show="headings", height=4)
        for h in ("Klas", "Aantal Leerlingen", "Gemiddelde Afstand (km)", "Verdeling Vervoersmiddelen"):
            self.tree_klassen_stat.heading(h, text=h)
            if h == "Verdeling Vervoersmiddelen":
                self.tree_klassen_stat.column(h, width=280, anchor="w")
            else:
                self.tree_klassen_stat.column(h, width=110, anchor="center")
        self.tree_klassen_stat.pack(side='left', fill='both', expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_klassen_stat.yview)
        self.tree_klassen_stat.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        
        # Chart Card
        chart_card = ttk.LabelFrame(self, text="Visuele Grafiek")
        chart_card.pack(fill='both', expand=True, padx=15, pady=(5, 15))

        btn_frame = ttk.Frame(chart_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_klassen = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('klassen'))
        self.btn_toggle_klassen.pack(side='right')

        self.canvas_klassen = tk.Canvas(chart_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_klassen.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class CategorieAnalyseFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Stats list card
        list_card = ttk.LabelFrame(self, text="Vervoer per Afstandscategorie")
        list_card.pack(fill='x', padx=15, pady=10)

        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill='x', padx=10, pady=10)

        self.tree_categorie_stat = ttk.Treeview(tree_frame, columns=("Categorie", "Totaal Ritten", "Populairste Vervoer", "Verdeling"), show="headings", height=4)
        for h in ("Categorie", "Totaal Ritten", "Populairste Vervoer", "Verdeling"):
            self.tree_categorie_stat.heading(h, text=h)
            self.tree_categorie_stat.column(h, width=120, anchor="center")
        self.tree_categorie_stat.column("Verdeling", width=250, anchor="w")
        self.tree_categorie_stat.pack(side='left', fill='both', expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_categorie_stat.yview)
        self.tree_categorie_stat.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        
        # Chart Card
        chart_card = ttk.LabelFrame(self, text="Visuele Grafiek")
        chart_card.pack(fill='both', expand=True, padx=15, pady=(5, 15))

        btn_frame = ttk.Frame(chart_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_categorie = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('categorie'))
        self.btn_toggle_categorie.pack(side='right')

        self.canvas_categorie = tk.Canvas(chart_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_categorie.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class CO2AnalyseFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Filters Box
        filter_frame = ttk.LabelFrame(self, text="Filters voor Eco Analyse")
        filter_frame.pack(fill='x', padx=15, pady=10)

        ttk.Label(filter_frame, text="Klas:").grid(row=0, column=0, padx=5, pady=8, sticky="e")
        self.combo_filter_klas = ttk.Combobox(filter_frame, state="readonly", width=12)
        self.combo_filter_klas.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        ttk.Label(filter_frame, text="Vervoer:").grid(row=0, column=2, padx=5, pady=8, sticky="e")
        self.combo_filter_vervoer = ttk.Combobox(filter_frame, state="readonly", width=12)
        self.combo_filter_vervoer.grid(row=0, column=3, padx=5, pady=8, sticky="w")

        ttk.Label(filter_frame, text="Afstand:").grid(row=0, column=4, padx=5, pady=8, sticky="e")
        self.combo_filter_afstand = ttk.Combobox(filter_frame, values=["Alle", "Kort (0-5 km)", "Middel (5.1-10 km)", "Lang (>10 km)"], state="readonly", width=18)
        self.combo_filter_afstand.set("Alle")
        self.combo_filter_afstand.grid(row=0, column=5, padx=5, pady=8, sticky="w")

        ttk.Button(filter_frame, text="⚡ Bereken CO₂ Uitstoot", command=lambda: self.view.controller.update_co2_analyse()).grid(row=0, column=6, padx=15, pady=8)

        # List card & Chart container
        results_frame = ttk.Frame(self)
        results_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        results_frame.columnconfigure(0, weight=4)
        results_frame.columnconfigure(1, weight=6)
        results_frame.rowconfigure(0, weight=1)

        # Left Card: List
        left_card = ttk.LabelFrame(results_frame, text="CO₂ Impact Tabel")
        left_card.grid(row=0, column=0, padx=(0, 5), pady=0, sticky='nsew')

        tree_frame = ttk.Frame(left_card)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tree_co2_stat = ttk.Treeview(tree_frame, columns=("Vervoersmiddel", "Aantal Ritten", "Totale CO2 (gram)"), show="headings", height=4)
        for h in ("Vervoersmiddel", "Aantal Ritten", "Totale CO2 (gram)"):
            self.tree_co2_stat.heading(h, text=h)
            self.tree_co2_stat.column(h, anchor="center", width=100)
        self.tree_co2_stat.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_co2_stat.yview)
        self.tree_co2_stat.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        # Right Card: Chart
        right_card = ttk.LabelFrame(results_frame, text="Visuele CO₂ Analyse")
        right_card.grid(row=0, column=1, padx=(5, 0), pady=0, sticky='nsew')

        btn_frame = ttk.Frame(right_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_co2 = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('co2'))
        self.btn_toggle_co2.pack(side='right')

        self.canvas_co2 = tk.Canvas(right_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_co2.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class GezondheidAnalyseFrame(ttk.Frame):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Stats list card
        list_card = ttk.LabelFrame(self, text="Gezondheidsindex per Klas")
        list_card.pack(fill='x', padx=15, pady=10)

        tree_frame = ttk.Frame(list_card)
        tree_frame.pack(fill='x', padx=10, pady=10)

        self.tree_gezondheid_stat = ttk.Treeview(tree_frame, columns=("Klas", "Actieve Ritten", "Passieve Ritten", "Gezondheidsindex (%)"), show="headings", height=4)
        for h in ("Klas", "Aantal Ritten", "Percentage"): # Wait! The header text:
            pass
        self.tree_gezondheid_stat.heading("Klas", text="Klas")
        self.tree_gezondheid_stat.heading("Actieve Ritten", text="Actieve Ritten (Fiets/Voet)")
        self.tree_gezondheid_stat.heading("Passieve Ritten", text="Passieve Ritten (Auto/Bus)")
        self.tree_gezondheid_stat.heading("Gezondheidsindex (%)", text="Gezondheidsindex (%)")
        
        for col in ("Klas", "Actieve Ritten", "Passieve Ritten", "Gezondheidsindex (%)"):
            self.tree_gezondheid_stat.column(col, anchor="center", width=140)
            
        self.tree_gezondheid_stat.pack(side='left', fill='both', expand=True)
        
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_gezondheid_stat.yview)
        self.tree_gezondheid_stat.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        
        # Chart Card
        chart_card = ttk.LabelFrame(self, text="Visuele Milieuanalyse (Actief vs. Passief)")
        chart_card.pack(fill='both', expand=True, padx=15, pady=(5, 15))

        btn_frame = ttk.Frame(chart_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_gezondheid = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('gezondheid'))
        self.btn_toggle_gezondheid.pack(side='right')

        self.canvas_gezondheid = tk.Canvas(chart_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_gezondheid.pack(fill='both', expand=True, padx=10, pady=(5, 10))
