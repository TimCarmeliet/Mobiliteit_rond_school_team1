import tkinter as tk
from tkinter import ttk, messagebox

# Importeer de gedecoupleerde sub-componenten en chart utilities
from view.beheer_frames import StudentenBeheerFrame, VervoersmiddelenFrame, VerplaatsingenFrame
from view.dashboard_frames import (
    OverzichtDataFrame, VervoersmiddelenAnalyseFrame, AfstandAnalyseFrame,
    KlassenAnalyseFrame, CategorieAnalyseFrame, CO2AnalyseFrame, GezondheidAnalyseFrame
)
import view.charts as charts

class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobiliteit rond de School - Project")
        self.geometry("1100x850") 
        self.controller = None
        
        # Geheugen voor de status van de grafieken
        self.chart_states = {
            'vervoer': {'type': 'pie', 'data': {}, 'titel': ""},
            'afstand': {'type': 'bar', 'data': {}, 'titel': ""},
            'klassen': {'type': 'bar', 'data': {}, 'titel': ""},
            'categorie': {'type': 'pie', 'data': {}, 'titel': ""},
            'co2': {'type': 'bar', 'data': {}, 'titel': ""},
            'gezondheid': {'type': 'pie', 'data': {}, 'titel': ""}
        }

        # Thema definities (Dark & Light tokens)
        self.themes = {
            'light': {
                'bg': "#f4f5f8",          # Crisp light grey
                'card_bg': "#ffffff",     # Clean white card surface
                'text': "#2c3e50",        # Dark charcoal text
                'text_muted': "#5a6b7c",  # Muted slate text
                'border': "#dcdfe6",      # Light border
                'accent': "#4a90e2",      # Steel blue accent
                'danger': "#e74c3c",      # Red
                'alternate_row': "#f8f9fa",
                'chart_text': "#2c3e50",  # Dark text inside canvas
                'chart_grid': "#e8eaed"   # Subtle grid line
            },
            'dark': {
                'bg': "#0f172a",          # Deep slate-900 background
                'card_bg': "#1e293b",     # Slate-800 card background
                'text': "#f8fafc",        # High contrast white-slate text
                'text_muted': "#94a3b8",  # Slate-400
                'border': "#334155",      # Dark border
                'accent': "#6366f1",      # Indigo accent
                'danger': "#f87171",      # Light red
                'alternate_row': "#1e293b",
                'chart_text': "#f8fafc",  # Readable text inside canvas
                'chart_grid': "#334155"   # Dark grid line
            }
        }
        self.current_theme = 'light' # Standaard light mode om origineel uiterlijk te behouden

        # Bouw top header bar (Voor thema knop, boven notebooks)
        self.header_bar = tk.Frame(self, pady=10)
        self.header_bar.pack(fill='x', padx=10)
        
        self.app_title_lbl = tk.Label(self.header_bar, text="🎒 Mobiliteit rond de School", font=('Arial', 14, 'bold'))
        self.app_title_lbl.pack(side='left', padx=10)

        self.btn_toggle_theme = ttk.Button(self.header_bar, text="🌓 Wissel Kleurenthema", command=self.toggle_theme)
        self.btn_toggle_theme.pack(side='right', padx=10)

        # Hoofd Notebook (Original Structure)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(5, 10))
        
        self.tab_beheer = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_beheer, text='Data Beheer (CRUD)')
        self.notebook.add(self.tab_dashboard, text='Dashboard & Analyses')
        
        # Bouw de gedecoupleerde sub-componenten
        self._build_beheer_tab()
        self._build_dashboard_tab()

        # Map alle sub-widget eigenschappen naar MainView (Voor perfecte Controller backwards compatibility!)
        self._map_sub_properties()

        # Activeer themastyling
        self.apply_theme()

    def active_theme(self):
        return self.themes[self.current_theme]

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()

    def apply_theme(self):
        theme = self.active_theme()
        bg = theme['bg']
        card_bg = theme['card_bg']
        text = theme['text']
        text_muted = theme['text_muted']
        border = theme['border']
        accent = theme['accent']
        danger = theme['danger']
        alternate = theme['alternate_row']
        
        # Configureer TTK Style
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Algemene configuraties
        style.configure('.', background=bg, foreground=text, font=('Arial', 10))
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg, foreground=text)
        style.configure('TLabelframe', font=('Arial', 10, 'bold'), bordercolor=border, borderwidth=1, background=bg)
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'), background=bg, foreground=text)
        
        # Notebook styling
        style.configure('TNotebook', background=bg, borderwidth=1, bordercolor=border)
        style.configure('TNotebook.Tab', background="#e4e7ed" if self.current_theme == 'light' else "#0b0f19", foreground=text, font=('Arial', 10, 'bold'), padding=(15, 6))
        style.map('TNotebook.Tab',
            background=[('selected', card_bg)],
            foreground=[('selected', accent)]
        )

        # Buttons (Clean flat met duidelijke contrasten in beide thema's)
        style.configure('TButton', font=('Arial', 10, 'bold'), borderwidth=1, bordercolor=border, padding=5)
        style.map('TButton',
            background=[('active', '#e4e7ed' if self.current_theme == 'light' else '#334155'), ('!disabled', card_bg)],
            foreground=[('active', accent), ('!disabled', text)]
        )
        style.configure('Danger.TButton', font=('Arial', 10, 'bold'), borderwidth=1, bordercolor=border, padding=5)
        style.map('Danger.TButton',
            background=[('active', '#fde8e8' if self.current_theme == 'light' else '#7f1d1d'), ('!disabled', card_bg)],
            foreground=[('active', danger), ('!disabled', danger)]
        )

        # Form Inputs & Comboboxes (Perfect contrast, no white-on-white)
        style.configure('TEntry', fieldbackground=card_bg, foreground=text, bordercolor=border, insertcolor=text, relief='flat')
        style.configure('TCombobox', fieldbackground=card_bg, background=card_bg, foreground=text, bordercolor=border, arrowcolor=text_muted)
        style.map('TCombobox', 
            fieldbackground=[('readonly', card_bg)], 
            background=[('readonly', card_bg)], 
            foreground=[('readonly', text)]
        )

        # Treeview (Neat high contrast tables)
        style.configure('Treeview', font=('Arial', 10), rowheight=26, background=card_bg, fieldbackground=card_bg, foreground=text, bordercolor=border, borderwidth=1)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background="#e4e7ed" if self.current_theme == 'light' else "#0b0f19", foreground=text, relief='flat', borderwidth=0)
        style.map('Treeview', 
            background=[('selected', accent)], 
            foreground=[('selected', '#ffffff')],
            alternatebackground=[('!selected', alternate)]
        )

        # Configureer Tkinter basis componenten
        self.config(bg=bg)
        self.header_bar.config(bg=bg)
        self.app_title_lbl.config(bg=bg, fg=accent)

        # Configureer alle canvases en dwing een grafiek repaint af in de nieuwe themakleuren
        for chart_id in self.chart_states:
            canvas = getattr(self, f"canvas_{chart_id}")
            canvas.config(bg=card_bg, highlightbackground=border)
            self.update_grafiek(chart_id)

    # ==========================================
    # SUB-COMPONENT FRAME BUILDERS
    # ==========================================
    def _build_beheer_tab(self):
        self.beheer_notebook = ttk.Notebook(self.tab_beheer)
        self.beheer_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Instantiëren van de gedecoupleerde sub-frames
        self.studenten_frame = StudentenBeheerFrame(self.beheer_notebook, self)
        self.vervoer_frame = VervoersmiddelenFrame(self.beheer_notebook, self)
        self.logs_frame = VerplaatsingenFrame(self.beheer_notebook, self)

        # Toevoegen aan sub-notebook
        self.beheer_notebook.add(self.studenten_frame, text='Studenten Beheren')
        self.beheer_notebook.add(self.vervoer_frame, text='Vervoersmiddelen')
        self.beheer_notebook.add(self.logs_frame, text='Verplaatsingen (Logs)')

    def _build_dashboard_tab(self):
        self.dashboard_notebook = ttk.Notebook(self.tab_dashboard)
        self.dashboard_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Instantiëren van de gedecoupleerde sub-frames
        self.overzicht_frame = OverzichtDataFrame(self.dashboard_notebook, self)
        self.vervoer_analyse_frame = VervoersmiddelenAnalyseFrame(self.dashboard_notebook, self)
        self.afstand_analyse_frame = AfstandAnalyseFrame(self.dashboard_notebook, self)
        self.klassen_analyse_frame = KlassenAnalyseFrame(self.dashboard_notebook, self)
        self.categorie_analyse_frame = CategorieAnalyseFrame(self.dashboard_notebook, self)
        self.co2_analyse_frame = CO2AnalyseFrame(self.dashboard_notebook, self)
        self.tab_gezondheid_analyse = GezondheidAnalyseFrame(self.dashboard_notebook, self)

        # Toevoegen aan sub-notebook
        self.dashboard_notebook.add(self.overzicht_frame, text='Overzicht Data')
        self.dashboard_notebook.add(self.vervoer_analyse_frame, text='Vervoersmiddelen')
        self.dashboard_notebook.add(self.afstand_analyse_frame, text='Afstand Analyse')
        self.dashboard_notebook.add(self.klassen_analyse_frame, text='Klassenanalyse')
        self.dashboard_notebook.add(self.categorie_analyse_frame, text='Afstandscategorieën (Extra)')
        self.dashboard_notebook.add(self.co2_analyse_frame, text='CO₂ Analyse (Uitbreiding)')
        self.dashboard_notebook.add(self.tab_gezondheid_analyse, text='Gezondheidsindex')

    def _map_sub_properties(self):
        """Mapt alle sub-component eigenschappen direct op self om controller.py intact te houden."""
        # Studenten Beheer
        self.entry_naam = self.studenten_frame.entry_naam
        self.entry_klas = self.studenten_frame.entry_klas
        self.entry_afstand = self.studenten_frame.entry_afstand
        self.tree_students = self.studenten_frame.tree_students

        # Vervoer Beheer
        self.entry_vervoer_type = self.vervoer_frame.entry_vervoer_type
        self.tree_trans = self.vervoer_frame.tree_trans

        # Logs Beheer
        self.combo_student = self.logs_frame.combo_student
        self.combo_vervoer = self.logs_frame.combo_vervoer
        self.entry_datum = self.logs_frame.entry_datum
        self.tree_logs = self.logs_frame.tree_logs

        # Dashboard Overzicht
        self.combo_overzicht_tabel = self.overzicht_frame.combo_overzicht_tabel
        self.tree_overzicht = self.overzicht_frame.tree_overzicht

        # Dashboard Vervoer
        self.tree_vervoer_stat = self.vervoer_analyse_frame.tree_vervoer_stat
        self.btn_toggle_vervoer = self.vervoer_analyse_frame.btn_toggle_vervoer
        self.canvas_vervoer = self.vervoer_analyse_frame.canvas_vervoer

        # Dashboard Afstand
        self.lbl_gem_afstand_totaal = self.afstand_analyse_frame.lbl_gem_afstand_totaal
        self.tree_afstand_stat = self.afstand_analyse_frame.tree_afstand_stat
        self.btn_toggle_afstand = self.afstand_analyse_frame.btn_toggle_afstand
        self.canvas_afstand = self.afstand_analyse_frame.canvas_afstand

        # Dashboard Klassen
        self.tree_klassen_stat = self.klassen_analyse_frame.tree_klassen_stat
        self.btn_toggle_klassen = self.klassen_analyse_frame.btn_toggle_klassen
        self.canvas_klassen = self.klassen_analyse_frame.canvas_klassen

        # Dashboard Afstandscategorieën
        self.tree_categorie_stat = self.categorie_analyse_frame.tree_categorie_stat
        self.btn_toggle_categorie = self.categorie_analyse_frame.btn_toggle_categorie
        self.canvas_categorie = self.categorie_analyse_frame.canvas_categorie

        # CO2 Analyse Filters
        self.combo_filter_klas = self.co2_analyse_frame.combo_filter_klas
        self.combo_filter_vervoer = self.co2_analyse_frame.combo_filter_vervoer
        self.combo_filter_afstand = self.co2_analyse_frame.combo_filter_afstand
        self.tree_co2_stat = self.co2_analyse_frame.tree_co2_stat
        self.btn_toggle_co2 = self.co2_analyse_frame.btn_toggle_co2
        self.canvas_co2 = self.co2_analyse_frame.canvas_co2

        # Gezondheid Analyse Mappings
        self.tree_gezondheid_stat = self.tab_gezondheid_analyse.tree_gezondheid_stat
        self.btn_toggle_gezondheid = self.tab_gezondheid_analyse.btn_toggle_gezondheid
        self.canvas_gezondheid = self.tab_gezondheid_analyse.canvas_gezondheid


    # ==========================================
    # CRISP FLAT DRAWINGS (BRIDGED TO CHARTS MODULE)
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
        
        # Extract correct subset if there are distinct datasets for pie vs bar (like Health index)
        if isinstance(state['data'], dict) and 'pie' in state['data'] and 'bar' in state['data']:
            chart_data = state['data']['pie'] if state['type'] == 'pie' else state['data']['bar']
        else:
            chart_data = state['data']
            
        theme = self.active_theme()
        
        # Roep de gedeelde module charts.py aan om de visualisatie op te bouwen
        if state['type'] == 'pie':
            charts.teken_cirkeldiagram(canvas, chart_data, state['titel'], theme)
            btn.config(text=" Wissel naar Staafdiagram ")
        else:
            charts.teken_grafiek(canvas, chart_data, state['titel'], theme)
            btn.config(text=" Wissel naar Cirkeldiagram ")

    def toggle_grafiek(self, chart_id):
        """Flipt de state tussen staaf- en cirkeldiagram en roept update_grafiek aan."""
        current_type = self.chart_states[chart_id]['type']
        self.chart_states[chart_id]['type'] = 'bar' if current_type == 'pie' else 'pie'
        self.update_grafiek(chart_id)


    # ==========================================
    # DATA HELPER BINDS & ORCHESTRATION METHODS
    # ==========================================
    def set_controller(self, controller): 
        self.controller = controller

    def show_error(self, message): 
        messagebox.showerror("Fout", message)

    def show_info(self, message): 
        messagebox.showinfo("Info", message)

    def get_student_form_data(self): 
        return {
            "naam": self.entry_naam.get().strip(), 
            "klas": self.entry_klas.get().strip(), 
            "afstand": self.entry_afstand.get().strip()
        }

    def clear_student_form(self): 
        for e in (self.entry_naam, self.entry_klas, self.entry_afstand):
            e.delete(0, tk.END)

    def _on_select_student(self, event):
        selected = self.tree_students.selection()
        if selected:
            v = self.tree_students.item(selected[0])['values']
            self.clear_student_form()
            self.entry_naam.insert(0, v[1])
            self.entry_klas.insert(0, v[2])
            self.entry_afstand.insert(0, str(v[3]))

    def populate_tree(self, tree, data):
        for item in tree.get_children(): 
            tree.delete(item)
        for row in data: 
            tree.insert("", tk.END, values=row)

    def get_selected_id(self, tree):
        selected = tree.selection()
        return tree.item(selected[0])['values'][0] if selected else None

    def setup_overzicht_tree(self, headers, data):
        self.tree_overzicht["columns"] = headers
        self.tree_overzicht["show"] = "headings"
        for h in headers:
            self.tree_overzicht.heading(h, text=h)
            self.tree_overzicht.column(h, width=150, anchor="center")
        self.populate_tree(self.tree_overzicht, data)

    def teken_grafiek(self, canvas, data_dict, titel):
        charts.teken_grafiek(canvas, data_dict, titel, self.active_theme())

    def teken_cirkeldiagram(self, canvas, data_dict, titel):
        charts.teken_cirkeldiagram(canvas, data_dict, titel, self.active_theme())