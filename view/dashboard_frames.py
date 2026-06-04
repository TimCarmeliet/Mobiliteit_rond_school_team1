"""
view/dashboard_frames.py — De Dashboard Sub-Frames (Analyse Componenten).

Dit bestand bevat zeven klassen, elk verantwoordelijk voor één analyse-tabblad
in het Dashboard. Elke klasse volgt hetzelfde bouwpatroon:

  1. Een LabelFrame met een Treeview (statistiekentabel)
  2. Een LabelFrame met een "Wissel Grafiektype"-knop en een tk.Canvas

De frames bevatten GEEN logica — ze zijn pure 'containers'. Alle berekeningen
gebeuren in de Controller, die de resultaten via populate_tree() en
update_grafiek() naar deze frames stuurt.

Overzicht van de 7 analyse-frames:
  OverzichtDataFrame             → Ruwe databasetabellen bekijken
  VervoersmiddelenAnalyseFrame   → Verdeling van vervoerskeuzes
  AfstandAnalyseFrame            → Gemiddelde afstanden per vervoersmiddel
  KlassenAnalyseFrame            → Vergelijking per schoolklas
  CategorieAnalyseFrame          → Eigen analyse: kort/middel/lang
  CO2AnalyseFrame                → Uitbreiding 1: milieu-impact met filters
  GezondheidAnalyseFrame         → Uitbreiding 2: actief vs. passief vervoer
"""

import tkinter as tk
from tkinter import ttk

class OverzichtDataFrame(ttk.Frame):
    """
    Dashboard-tab voor het bekijken van ruwe databasetabellen.

    Bevat een Combobox waarmee de gebruiker kan kiezen welke tabel
    hij wil bekijken (Students, Transport, of Mobility_log).
    Bij selectie wordt de Controller aangesproken om de juiste headers
    en data in te laden.
    """

    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Kies te bekijken tabel:").pack(side='left', padx=5)
        self.combo_overzicht_tabel = ttk.Combobox(top_frame, values=['Students', 'Transport', 'Mobility_log'], state='readonly', width=15)
        self.combo_overzicht_tabel.set('Students')
        self.combo_overzicht_tabel.pack(side='left', padx=5)
        # Bij elke selectiewijziging wordt laad_overzicht_tabel() aangeroepen
        # via een event-binding op het <<ComboboxSelected>> event
        self.combo_overzicht_tabel.bind("<<ComboboxSelected>>", lambda e: self.view.controller.laad_overzicht_tabel())
        
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tree_overzicht = ttk.Treeview(list_frame)
        self.tree_overzicht.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree_overzicht.yview)
        self.tree_overzicht.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')


class VervoersmiddelenAnalyseFrame(ttk.Frame):
    """
    Dashboard-tab: Vervoersmiddelenverdeling.

    Toont een tabel met het aantal ritten en percentage per vervoersmiddel,
    plus een grafiek (standaard cirkeldiagram) die visueel de verdeling toont.
    De gebruiker kan wisselen tussen staaf- en cirkeldiagram.
    """

    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # ── Bovenste kaart: Statistiekentabel ──
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
        
        # ── Onderste kaart: Grafiek met wisselknop ──
        chart_card = ttk.LabelFrame(self, text="Visuele Grafiek")
        chart_card.pack(fill='both', expand=True, padx=15, pady=(5, 15))

        btn_frame = ttk.Frame(chart_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_vervoer = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('vervoer'))
        self.btn_toggle_vervoer.pack(side='right')

        # Canvas is het "schildersdoek" waarop charts.py de grafiek tekent
        self.canvas_vervoer = tk.Canvas(chart_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_vervoer.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class AfstandAnalyseFrame(ttk.Frame):
    """
    Dashboard-tab: Afstandsanalyse.

    Toont bovenaan de algemene gemiddelde woon-school-afstand, gevolgd door
    een tabel met gemiddelde en totale afstand per vervoersmiddel.
    De bijbehorende grafiek visualiseert deze gemiddelden.
    """

    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # Stats card
        list_card = ttk.LabelFrame(self, text="Afstandsgegevens per Vervoermiddel")
        list_card.pack(fill='x', padx=15, pady=10)

        # Informatielabel dat dynamisch wordt bijgewerkt door de Controller
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
    """
    Dashboard-tab: Klassenanalyse.

    Vergelijkt klassen onderling op:
      • Aantal leerlingen
      • Gemiddelde woon-school-afstand
      • Verdeling van vervoersmiddelen (als tekst-samenvatting)

    De grafiek toont de gemiddelde afstand per klas, wat interessante
    patronen kan onthullen (bijv. "Klas 6B woont gemiddeld verder").
    """

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
    """
    Dashboard-tab: Vervoerskeuze per Afstandscategorie (Eigen Analyse).

    Dit is een ZELF BEDACHTE analyse die de relatie onderzoekt tussen
    de woonafstand van een student en zijn/haar vervoerskeuze:
      • Kort (0-5 km):   Verwachting: veel fiets en te voet
      • Middel (5-10 km): Verwachting: mix van fiets en bus
      • Lang (>10 km):    Verwachting: veel auto en bus

    De grafiek toont het totale aantal ritten per categorie.
    """

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
    """
    Dashboard-tab: CO₂ Analyse (Uitbreiding 1).

    Dit tabblad biedt een INTERACTIEVE milieu-analyse met drie filters:
      • Filter op Klas (bijv. alleen 6A bekijken)
      • Filter op Vervoersmiddel (bijv. alleen auto's)
      • Filter op Afstandscategorie (bijv. alleen korte ritten)

    Na het klikken op "Bereken CO₂ Uitstoot" berekent de Controller
    de totale CO₂ per vervoersmiddel op basis van:
      CO₂ (gram) = afstand_student × uitstoot_per_km

    De layout is hier anders: de tabel en grafiek staan NAAST elkaar
    (grid-layout) in plaats van boven elkaar, voor een overzichtelijker geheel.
    """

    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # ── Filterbalk ──
        # Drie Comboboxen + een berekenknop op één horizontale rij
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

        # ── Resultaten: Tabel links, Grafiek rechts (Grid Layout) ──
        results_frame = ttk.Frame(self)
        results_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        # columnconfigure bepaalt de verhouding: 4:6 (tabel krijgt 40%, grafiek 60%)
        results_frame.columnconfigure(0, weight=4)
        results_frame.columnconfigure(1, weight=6)
        results_frame.rowconfigure(0, weight=1)

        # Linkerkaart: CO₂ Impact Tabel
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

        # Rechterkaart: Visuele CO₂ Grafiek
        right_card = ttk.LabelFrame(results_frame, text="Visuele CO₂ Analyse")
        right_card.grid(row=0, column=1, padx=(5, 0), pady=0, sticky='nsew')

        btn_frame = ttk.Frame(right_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_co2 = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('co2'))
        self.btn_toggle_co2.pack(side='right')

        self.canvas_co2 = tk.Canvas(right_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_co2.pack(fill='both', expand=True, padx=10, pady=(5, 10))


class GezondheidAnalyseFrame(ttk.Frame):
    """
    Dashboard-tab: Gezondheidsindex (Uitbreiding 2 — Actief vs. Passief Vervoer).

    Dit tabblad visualiseert hoe "gezond" de vervoerskeuzes zijn:
      Actief vervoer  = Fiets, Te voet  (fysieke inspanning, 0g CO₂)
      Passief vervoer = Auto, Bus       (gemotoriseerd)

    De tabel toont per klas:
      • Aantal actieve ritten
      • Aantal passieve ritten
      • Gezondheidsindex (%) = actieve ritten / totaal × 100

    De grafiek wisselt tussen:
      • Cirkeldiagram: schoolbreed overzicht (Actief vs. Passief totaal)
      • Staafdiagram: per-klas gezondheidsindex (%)
    """

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


class LoggingAnalyseFrame(ttk.Frame):
    """
    Dashboard-tab: Logging Analyse (Uitbreiding 3 — Gebruikersacties Audit Trail).

    Dit tabblad visualiseert het gebruik van de applicatie zelf:
      • Hoeveel acties heeft elke gebruiker uitgevoerd?
      • Welke actie-types komen het meest voor (login, create, update, delete)?
      • Wie is de meest actieve gebruiker?

    Links staan drie compacte Treeview-tabellen, rechts een grafiek
    die de verdeling per actietype toont als cirkel- of staafdiagram.
    """

    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view

        # ── Linkerzijde: Drie analyse-tabellen onder elkaar ──
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=4)
        main_frame.columnconfigure(1, weight=6)
        main_frame.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=(0, 5), sticky='nsew')

        # Tabel 1: Acties per Gebruiker
        card1 = ttk.LabelFrame(left_frame, text="Acties per Gebruiker")
        card1.pack(fill='x', padx=5, pady=(0, 5))

        tf1 = ttk.Frame(card1)
        tf1.pack(fill='x', padx=5, pady=5)

        self.tree_logging_user = ttk.Treeview(tf1, columns=("Gebruiker", "Aantal Acties"), show="headings", height=3)
        self.tree_logging_user.heading("Gebruiker", text="Gebruiker")
        self.tree_logging_user.heading("Aantal Acties", text="Aantal Acties")
        self.tree_logging_user.column("Gebruiker", anchor="center", width=120)
        self.tree_logging_user.column("Aantal Acties", anchor="center", width=100)
        self.tree_logging_user.pack(side='left', fill='both', expand=True)

        sb1 = ttk.Scrollbar(tf1, orient="vertical", command=self.tree_logging_user.yview)
        self.tree_logging_user.configure(yscrollcommand=sb1.set)
        sb1.pack(side='right', fill='y')

        # Tabel 2: Acties per Type
        card2 = ttk.LabelFrame(left_frame, text="Acties per Type")
        card2.pack(fill='x', padx=5, pady=5)

        tf2 = ttk.Frame(card2)
        tf2.pack(fill='x', padx=5, pady=5)

        self.tree_logging_type = ttk.Treeview(tf2, columns=("Actietype", "Aantal"), show="headings", height=3)
        self.tree_logging_type.heading("Actietype", text="Actietype")
        self.tree_logging_type.heading("Aantal", text="Aantal")
        self.tree_logging_type.column("Actietype", anchor="center", width=120)
        self.tree_logging_type.column("Aantal", anchor="center", width=100)
        self.tree_logging_type.pack(side='left', fill='both', expand=True)

        sb2 = ttk.Scrollbar(tf2, orient="vertical", command=self.tree_logging_type.yview)
        self.tree_logging_type.configure(yscrollcommand=sb2.set)
        sb2.pack(side='right', fill='y')

        # Tabel 3: Meest Actieve Gebruiker(s)
        card3 = ttk.LabelFrame(left_frame, text="🏆 Meest Actieve Gebruiker(s)")
        card3.pack(fill='x', padx=5, pady=(5, 0))

        tf3 = ttk.Frame(card3)
        tf3.pack(fill='x', padx=5, pady=5)

        self.tree_logging_actief = ttk.Treeview(tf3, columns=("Gebruiker", "Aantal Acties"), show="headings", height=2)
        self.tree_logging_actief.heading("Gebruiker", text="Gebruiker")
        self.tree_logging_actief.heading("Aantal Acties", text="Aantal Acties")
        self.tree_logging_actief.column("Gebruiker", anchor="center", width=120)
        self.tree_logging_actief.column("Aantal Acties", anchor="center", width=100)
        self.tree_logging_actief.pack(side='left', fill='both', expand=True)

        sb3 = ttk.Scrollbar(tf3, orient="vertical", command=self.tree_logging_actief.yview)
        self.tree_logging_actief.configure(yscrollcommand=sb3.set)
        sb3.pack(side='right', fill='y')

        # ── Rechterzijde: Grafiek met wisselknop ──
        right_card = ttk.LabelFrame(main_frame, text="Visuele Logging Analyse")
        right_card.grid(row=0, column=1, padx=(5, 0), sticky='nsew')

        btn_frame = ttk.Frame(right_card)
        btn_frame.pack(fill='x', padx=10, pady=(5, 0))
        self.btn_toggle_logging = ttk.Button(btn_frame, text="Wissel Grafiektype", command=lambda: self.view.toggle_grafiek('logging'))
        self.btn_toggle_logging.pack(side='right')

        self.canvas_logging = tk.Canvas(right_card, bg='white', bd=1, highlightthickness=0, relief="solid")
        self.canvas_logging.pack(fill='both', expand=True, padx=10, pady=(5, 10))

