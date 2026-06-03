import tkinter as tk
from tkinter import ttk, messagebox

# Importeer de gedecoupleerde sub-componenten en chart utilities
from view.beheer_frames import StudentenBeheerFrame, VervoersmiddelenFrame, VerplaatsingenFrame
from view.dashboard_frames import (
    OverzichtDataFrame, VervoersmiddelenAnalyseFrame, AfstandAnalyseFrame,
    KlassenAnalyseFrame, CategorieAnalyseFrame, CO2AnalyseFrame, GezondheidAnalyseFrame
)
import view.charts as charts

# ==========================================
# NIEUWE SUB-FRAMES VOOR AANWEZIGHEDEN (In dezelfde stijl)
# ==========================================
class AanwezighedenBeheerFrame(ttk.Frame):
    def __init__(self, parent, main_view):
        super().__init__(parent)
        self.main_view = main_view
        
        # Splitter Layout (Links invoer, Rechts de tabel)
        main_splitter = ttk.PanedWindow(self, orient='horizontal')
        main_splitter.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Linker paneel: Formulier
        left_frame = ttk.Frame(main_splitter)
        main_splitter.add(left_frame, weight=1)
        
        form_frame = ttk.LabelFrame(left_frame, text=" Aanwezigheid Registreren ", padding=15)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Selecteer Student:").pack(anchor='w', pady=(0, 2))
        self.combo_student = ttk.Combobox(form_frame, state="readonly")
        self.combo_student.pack(fill='x', pady=(0, 10))
        
        ttk.Label(form_frame, text="Datum (JJJJ-MM-DD):").pack(anchor='w', pady=(0, 2))
        self.entry_datum = ttk.Entry(form_frame)
        self.entry_datum.pack(fill='x', pady=(0, 10))
        
        ttk.Label(form_frame, text="Status:").pack(anchor='w', pady=(0, 2))
        self.combo_status = ttk.Combobox(form_frame, values=["Aanwezig", "Afwezig", "Te laat"], state="readonly")
        self.combo_status.set("Aanwezig")
        self.combo_status.pack(fill='x', pady=(0, 15))
        
        # Actieknoppen
        btn_add = ttk.Button(form_frame, text=" Opslaan ", command=lambda: self.main_view.controller.add_aanwezigheid())
        btn_add.pack(fill='x', pady=5)
        
        btn_del = ttk.Button(form_frame, text=" Selectie Verwijderen ", style='Danger.TButton', command=lambda: self.main_view.controller.delete_aanwezigheid())
        btn_del.pack(fill='x', pady=5)
        
        # Rechter paneel: Overzichtstabel
        right_frame = ttk.Frame(main_splitter)
        main_splitter.add(right_frame, weight=3)
        
        table_frame = ttk.LabelFrame(right_frame, text=" Historie Aanwezigheidsregistraties ", padding=10)
        table_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        headers = ("ID", "Student (ID & Naam)", "Datum", "Status")
        self.tree_aanw = ttk.Treeview(table_frame, columns=headers, show="headings")
        
        for h in headers:
            self.tree_aanw.heading(h, text=h)
            self.tree_aanw.column(h, anchor="center", width=120)
            
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_aanw.yview)
        self.tree_aanw.configure(yscrollcommand=scroll.set)
        
        self.tree_aanw.pack(side='left', expand=True, fill='both')
        scroll.pack(side='right', fill='y')


class AanwezigheidsAnalyseFrame(ttk.Frame):
    def __init__(self, parent, main_view):
        super().__init__(parent)
        self.main_view = main_view
        
        # Bovenste gedeelte: Filter / Type Analyse selectie
        top_frame = ttk.LabelFrame(self, text=" Kies Analyse-invalshoek ", padding=10)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Selecteer statistiek: ").pack(side='left', padx=5)
        self.combo_analyse = ttk.Combobox(top_frame, values=[
            "Aantal afwezigheden per klas", 
            "Percentage aanwezig per klas", 
            "Vervoersmiddel vs Aanwezigheid"
        ], state="readonly", width=35)
        self.combo_analyse.set("Aantal afwezigheden per klas")
        self.combo_analyse.pack(side='left', padx=5)
        
        btn_update = ttk.Button(top_frame, text=" Berekenen & Tonen ", command=lambda: self.main_view.controller.update_aanwezigheid_analyse())
        top_frame.bind("<Visibility>", lambda e: self.main_view.controller.update_aanwezigheid_analyse())
        self.combo_analyse.bind("<<ComboboxSelected>>", lambda e: self.main_view.controller.update_aanwezigheid_analyse())
        btn_update.pack(side='left', padx=10)
        
        # Onderste gedeelte split: Links tabel, Rechts grafiek
        data_splitter = ttk.PanedWindow(self, orient='horizontal')
        data_splitter.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Links: De data tabel
        tabel_wrapper = ttk.LabelFrame(data_splitter, text=" Analytische Uitkomst ", padding=10)
        data_splitter.add(tabel_wrapper, weight=1)
        
        self.tree_aanw_analyse = ttk.Treeview(tabel_wrapper, show="headings")
        self.tree_aanw_analyse.pack(expand=True, fill='both')
        
        # Rechts: De Grafiek + Wisselknop
        grafiek_wrapper = ttk.LabelFrame(data_splitter, text=" Visuele Weergave ", padding=10)
        data_splitter.add(grafiek_wrapper, weight=1)
        
        self.btn_toggle_aanwezigheid = ttk.Button(grafiek_wrapper, text=" Wissel naar Cirkeldiagram ", command=lambda: self.main_view.toggle_grafiek('aanwezigheid'))
        self.btn_toggle_aanwezigheid.pack(anchor='ne', pady=(0, 5))
        
        self.canvas_aanwezigheid = tk.Canvas(grafiek_wrapper, bg="white", highlightthickness=0)
        self.canvas_aanwezigheid.pack(expand=True, fill='both')


# ==========================================
# NIEUWE SUB-FRAMES VOOR REISTIJDEN (In dezelfde stijl)
# ==========================================
class ReistijdAnalyseFrame(ttk.Frame):
    def __init__(self, parent, main_view):
        super().__init__(parent)
        self.main_view = main_view
        
        # Splitter Layout (Links tabellen, Rechts grafiek)
        main_splitter = ttk.PanedWindow(self, orient='horizontal')
        main_splitter.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Links: Data tabellen wrapper
        left_frame = ttk.Frame(main_splitter)
        main_splitter.add(left_frame, weight=1)
        
        tabel1_wrapper = ttk.LabelFrame(left_frame, text=" Gemiddelde Reistijd per Vervoersmiddel ", padding=5)
        tabel1_wrapper.pack(expand=True, fill='both', padx=5, pady=5)
        
        headers_vervoer = ("Vervoersmiddel", "Gem. Reistijd (min)")
        self.tree_reistijd_vervoer = ttk.Treeview(tabel1_wrapper, columns=headers_vervoer, show="headings")
        for h in headers_vervoer:
            self.tree_reistijd_vervoer.heading(h, text=h)
            self.tree_reistijd_vervoer.column(h, anchor="center", width=120)
        self.tree_reistijd_vervoer.pack(expand=True, fill='both')
        
        tabel2_wrapper = ttk.LabelFrame(left_frame, text=" Klassen & Reistijden ", padding=5)
        tabel2_wrapper.pack(expand=True, fill='both', padx=5, pady=5)
        
        headers_klas = ("Klas", "Reistijd (min)")
        self.tree_reistijd_klas = ttk.Treeview(tabel2_wrapper, columns=headers_klas, show="headings")
        for h in headers_klas:
            self.tree_reistijd_klas.heading(h, text=h)
            self.tree_reistijd_klas.column(h, anchor="center", width=120)
        self.tree_reistijd_klas.pack(expand=True, fill='both')
        
        # Rechts: De Grafiek + Wisselknop
        grafiek_wrapper = ttk.LabelFrame(main_splitter, text=" Visuele Weergave Reistijden ", padding=10)
        main_splitter.add(grafiek_wrapper, weight=1)
        
        self.btn_toggle_reistijd = ttk.Button(grafiek_wrapper, text=" Wissel naar Cirkeldiagram ", command=lambda: self.main_view.toggle_grafiek('reistijd'))
        self.btn_toggle_reistijd.pack(anchor='ne', pady=(0, 5))
        
        self.canvas_reistijd = tk.Canvas(grafiek_wrapper, bg="white", highlightthickness=0)
        self.canvas_reistijd.pack(expand=True, fill='both')
        
        self.bind("<Visibility>", lambda e: self.main_view.controller.update_reistijd_analyse() if self.main_view.controller else None)


# ==========================================
# HOOFD INTERFACE (MainView)
# ==========================================
class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobiliteit rond de School - Project")
        self.geometry("1100x850") 
        self.controller = None
        
        # Geheugen voor de status van de grafieken (AANGEVULD MET AANWEZIGHED & REISTIJD)
        self.chart_states = {
            'vervoer': {'type': 'pie', 'data': {}, 'titel': ""},
            'afstand': {'type': 'bar', 'data': {}, 'titel': ""},
            'klassen': {'type': 'bar', 'data': {}, 'titel': ""},
            'categorie': {'type': 'pie', 'data': {}, 'titel': ""},
            'co2': {'type': 'bar', 'data': {}, 'titel': ""},
            'gezondheid': {'type': 'pie', 'data': {}, 'titel': ""},
            'aanwezigheid': {'type': 'bar', 'data': {}, 'titel': ""},
            'reistijd': {'type': 'bar', 'data': {}, 'titel': ""} # <-- NIEUW
        }

        # 1. Clean, High-Contrast Light Styling Configuration
        style = ttk.Style(self)
        style.theme_use('clam')
        
        bg_window = "#f4f5f8"      
        bg_card = "#ffffff"        
        fg_text = "#2c3e50"        
        fg_muted = "#5a6b7c"       
        border_color = "#dcdfe6"   
        accent_color = "#4a90e2"   
        danger_color = "#e74c3c"   
        alternate_row = "#f8f9fa"  

        # Algemene stijl instellingen
        style.configure('.', background=bg_window, foreground=fg_text, font=('Arial', 10))
        style.configure('TFrame', background=bg_window)
        style.configure('TLabel', background=bg_window, foreground=fg_text, font=('Arial', 10))
        
        # Hoofd Notebook styling
        style.configure('TNotebook', background=bg_window, borderwidth=1, bordercolor=border_color)
        style.configure('TNotebook.Tab', background="#e4e7ed", foreground=fg_text, font=('Arial', 10, 'bold'), padding=(15, 6))
        style.map('TNotebook.Tab',
            background=[('selected', bg_card)],
            foreground=[('selected', accent_color)]
        )

        # Buttons
        style.configure('TButton', font=('Arial', 10, 'bold'), borderwidth=1, bordercolor=border_color, padding=5)
        style.map('TButton',
            background=[('active', '#e4e7ed'), ('!disabled', '#ffffff')],
            foreground=[('active', accent_color), ('!disabled', fg_text)]
        )
        style.configure('Danger.TButton', font=('Arial', 10, 'bold'), borderwidth=1, bordercolor=border_color, padding=5)
        style.map('Danger.TButton',
            background=[('active', '#fde8e8'), ('!disabled', '#ffffff')],
            foreground=[('active', danger_color), ('!disabled', danger_color)]
        )

        # Form Inputs & Comboboxes
        style.configure('TEntry', fieldbackground="#ffffff", foreground=fg_text, bordercolor=border_color, insertcolor=fg_text, relief='flat')
        style.configure('TCombobox', fieldbackground="#ffffff", background="#ffffff", foreground=fg_text, bordercolor=border_color, arrowcolor=fg_muted)
        style.map('TCombobox', 
            fieldbackground=[('readonly', '#ffffff')], 
            background=[('readonly', '#ffffff')], 
            foreground=[('readonly', fg_text)]
        )

        # LabelFrame
        style.configure('TLabelframe', font=('Arial', 10, 'bold'), bordercolor=border_color, borderwidth=1, background=bg_window)
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'), background=bg_window, foreground=fg_text)

        # Treeview
        style.configure('Treeview', font=('Arial', 10), rowheight=26, background=bg_card, fieldbackground=bg_card, foreground=fg_text, bordercolor=border_color, borderwidth=1)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background="#e4e7ed", foreground=fg_text, relief='flat', borderwidth=0)
        style.map('Treeview', 
            background=[('selected', accent_color)], 
            foreground=[('selected', '#ffffff')],
            alternatebackground=[('!selected', alternate_row)]
        )

        self.config(bg=bg_window)

        # 2. Hoofd Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_beheer = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_beheer, text='Data Beheer (CRUD)')
        self.notebook.add(self.tab_dashboard, text='Dashboard & Analyses')
        
        # 3. Bouw de sub-componenten
        self._build_beheer_tab()
        self._build_dashboard_tab()

        # 4. Map alle sub-widget eigenschappen naar MainView
        self._map_sub_properties()

    # ==========================================
    # SUB-COMPONENT FRAME BUILDERS
    # ==========================================
    def _build_beheer_tab(self):
        self.beheer_notebook = ttk.Notebook(self.tab_beheer)
        self.beheer_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.studenten_frame = StudentenBeheerFrame(self.beheer_notebook, self)
        self.vervoer_frame = VervoersmiddelenFrame(self.beheer_notebook, self)
        self.logs_frame = VerplaatsingenFrame(self.beheer_notebook, self)
        self.aanwezigheid_beheer_frame = AanwezighedenBeheerFrame(self.beheer_notebook, self) # <-- NIEUW

        self.beheer_notebook.add(self.studenten_frame, text='Studenten Beheren')
        self.beheer_notebook.add(self.vervoer_frame, text='Vervoersmiddelen')
        self.beheer_notebook.add(self.logs_frame, text='Verplaatsingen (Logs)')
        self.beheer_notebook.add(self.aanwezigheid_beheer_frame, text='Aanwezigheden Beheren (Nieuw)') # <-- NIEUW

    def _build_dashboard_tab(self):
        self.dashboard_notebook = ttk.Notebook(self.tab_dashboard)
        self.dashboard_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.overzicht_frame = OverzichtDataFrame(self.dashboard_notebook, self)
        self.vervoer_analyse_frame = VervoersmiddelenAnalyseFrame(self.dashboard_notebook, self)
        self.afstand_analyse_frame = AfstandAnalyseFrame(self.dashboard_notebook, self)
        self.klassen_analyse_frame = KlassenAnalyseFrame(self.dashboard_notebook, self)
        self.categorie_analyse_frame = CategorieAnalyseFrame(self.dashboard_notebook, self)
        self.co2_analyse_frame = CO2AnalyseFrame(self.dashboard_notebook, self)
        self.tab_gezondheid_analyse = GezondheidAnalyseFrame(self.dashboard_notebook, self)
        self.aanwezigheid_analyse_frame = AanwezigheidsAnalyseFrame(self.dashboard_notebook, self) # <-- NIEUW
        self.reistijd_analyse_frame = ReistijdAnalyseFrame(self.dashboard_notebook, self) # <-- NIEUW

        self.dashboard_notebook.add(self.overzicht_frame, text='Overzicht Data')
        self.dashboard_notebook.add(self.vervoer_analyse_frame, text='Vervoersmiddelen')
        self.dashboard_notebook.add(self.afstand_analyse_frame, text='Afstand Analyse')
        self.dashboard_notebook.add(self.klassen_analyse_frame, text='Klassenanalyse')
        self.dashboard_notebook.add(self.categorie_analyse_frame, text='Afstandscategorieën (Extra)')
        self.dashboard_notebook.add(self.co2_analyse_frame, text='CO₂ Analyse (Uitbreiding)')
        self.dashboard_notebook.add(self.tab_gezondheid_analyse, text='Gezondheidsindex')
        self.dashboard_notebook.add(self.aanwezigheid_analyse_frame, text='Aanwezigheidsanalyse (Nieuw)') # <-- NIEUW
        self.dashboard_notebook.add(self.reistijd_analyse_frame, text='Reistijd Analyse (Nieuw)') # <-- NIEUW

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

        # Aanwezigheden Beheer Mappings
        self.tree_aanw = self.aanwezigheid_beheer_frame.tree_aanw

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

        # Aanwezigheid Analyse Mappings
        self.btn_toggle_aanwezigheid = self.aanwezigheid_analyse_frame.btn_toggle_aanwezigheid
        self.canvas_aanwezigheid = self.aanwezigheid_analyse_frame.canvas_aanwezigheid

        # Reistijd Analyse Mappings <-- NIEUW
        self.tree_reistijd_vervoer = self.reistijd_analyse_frame.tree_reistijd_vervoer
        self.tree_reistijd_klas = self.reistijd_analyse_frame.tree_reistijd_klas
        self.btn_toggle_reistijd = self.reistijd_analyse_frame.btn_toggle_reistijd
        self.canvas_reistijd = self.reistijd_analyse_frame.canvas_reistijd


    # ==========================================
    # CRISP FLAT DRAWINGS (BRIDGED TO CHARTS MODULE)
    # ==========================================
    def update_grafiek(self, chart_id, data=None, titel=None):
        if data is not None:
            self.chart_states[chart_id]['data'] = data
        if titel is not None:
            self.chart_states[chart_id]['titel'] = titel
            
        state = self.chart_states[chart_id]
        canvas = getattr(self, f"canvas_{chart_id}")
        btn = getattr(self, f"btn_toggle_{chart_id}")
        
        if isinstance(state['data'], dict) and 'pie' in state['data'] and 'bar' in state['data']:
            chart_data = state['data']['pie'] if state['type'] == 'pie' else state['data']['bar']
        else:
            chart_data = state['data']
            
        if state['type'] == 'pie':
            charts.teken_cirkeldiagram(canvas, chart_data, state['titel'])
            btn.config(text=" Wissel naar Staafdiagram ")
        else:
            charts.teken_grafiek(canvas, chart_data, state['titel'])
            btn.config(text=" Wissel naar Cirkeldiagram ")

    def toggle_grafiek(self, chart_id):
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
        charts.teken_grafiek(canvas, data_dict, titel)

    def teken_cirkeldiagram(self, canvas, data_dict, titel):
        charts.teken_cirkeldiagram(canvas, data_dict, titel)