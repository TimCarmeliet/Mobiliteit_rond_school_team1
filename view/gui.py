import tkinter as tk
from tkinter import ttk, messagebox

# Importeer de gedecoupleerde sub-componenten en chart utilities
from view.beheer_frames import StudentenBeheerFrame, VervoersmiddelenFrame, VerplaatsingenFrame
from view.dashboard_frames import (
    OverzichtDataFrame, VervoersmiddelenAnalyseFrame, AfstandAnalyseFrame,
    KlassenAnalyseFrame, CategorieAnalyseFrame, CO2AnalyseFrame
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
            'co2': {'type': 'bar', 'data': {}, 'titel': ""}
        }

        # 1. Clean, High-Contrast Light Styling Configuration
        style = ttk.Style(self)
        style.theme_use('clam')
        
        bg_window = "#f4f5f8"      # Light grey background
        bg_card = "#ffffff"        # Pure white background
        fg_text = "#2c3e50"        # High contrast charcoal text
        fg_muted = "#5a6b7c"       # Muted slate text
        border_color = "#dcdfe6"   # Clean borders
        accent_color = "#4a90e2"   # Professional blue
        danger_color = "#e74c3c"   # Clean red for delete
        alternate_row = "#f8f9fa"  # Alternate list rows

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

        # Buttons (Clean flat with clear contrast)
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

        # Form Inputs & Comboboxes (Perfect contrast, no white-on-white)
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

        # Treeview (Neat high contrast tables)
        style.configure('Treeview', font=('Arial', 10), rowheight=26, background=bg_card, fieldbackground=bg_card, foreground=fg_text, bordercolor=border_color, borderwidth=1)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background="#e4e7ed", foreground=fg_text, relief='flat', borderwidth=0)
        style.map('Treeview', 
            background=[('selected', accent_color)], 
            foreground=[('selected', '#ffffff')],
            alternatebackground=[('!selected', alternate_row)]
        )

        self.config(bg=bg_window)

        # 2. Hoofd Notebook (Original Structure)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_beheer = ttk.Frame(self.notebook)
        self.tab_dashboard = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_beheer, text='Data Beheer (CRUD)')
        self.notebook.add(self.tab_dashboard, text='Dashboard & Analyses')
        
        # 3. Bouw de gedecoupleerde sub-componenten
        self._build_beheer_tab()
        self._build_dashboard_tab()

        # 4. Map alle sub-widget eigenschappen naar MainView (Voor perfecte Controller backwards compatibility!)
        self._map_sub_properties()

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

        # Toevoegen aan sub-notebook
        self.dashboard_notebook.add(self.overzicht_frame, text='Overzicht Data')
        self.dashboard_notebook.add(self.vervoer_analyse_frame, text='Vervoersmiddelen')
        self.dashboard_notebook.add(self.afstand_analyse_frame, text='Afstand Analyse')
        self.dashboard_notebook.add(self.klassen_analyse_frame, text='Klassenanalyse')
        self.dashboard_notebook.add(self.categorie_analyse_frame, text='Afstandscategorieën (Extra)')
        self.dashboard_notebook.add(self.co2_analyse_frame, text='CO₂ Analyse (Uitbreiding)')

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
        
        # Roep de gedeelde module charts.py aan om de visualisatie op te bouwen
        if state['type'] == 'pie':
            charts.teken_cirkeldiagram(canvas, state['data'], state['titel'])
            btn.config(text=" Wissel naar Staafdiagram ")
        else:
            charts.teken_grafiek(canvas, state['data'], state['titel'])
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
        charts.teken_grafiek(canvas, data_dict, titel)

    def teken_cirkeldiagram(self, canvas, data_dict, titel):
        charts.teken_cirkeldiagram(canvas, data_dict, titel)