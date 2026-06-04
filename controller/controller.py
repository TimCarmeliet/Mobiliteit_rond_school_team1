"""
controller/controller.py — De Controller-laag (Business Logic / Coördinator).

Dit is het BREIN van de applicatie. De Controller is de enige plek waar
bedrijfslogica leeft. Hij:
  1. Ontvangt acties van de View (bijv. "gebruiker klikte op Toevoegen")
  2. Voert berekeningen uit in pure Python (geen SQL JOINs!)
  3. Stuurt resultaten terug naar de View om te tonen

Belangrijke ontwerpkeuze — Python-logica i.p.v. SQL JOINs:
──────────────────────────────────────────────────────────
In plaats van complexe JOIN-queries in de databank uit te voeren, halen we
de ruwe tabellen op als losse lijsten en verwerken we ze in Python met
dictionaries. Dit heeft twee voordelen:
  • Het is didactisch helder — je ziet exact welke stappen er gebeuren.
  • Het geeft ons meer flexibiliteit voor analyses (categorieën, filters)
    die in SQL onnodig complex zouden worden.
"""

from datetime import datetime
from tkinter import simpledialog

class Controller:
    """
    De hoofdcoördinator van de MVC-applicatie.

    Bij constructie ontvangt hij zowel het Model (database) als de View (GUI).
    Hij verbindt zichzelf met de View via set_controller(), zodat knoppen
    in de interface callbacks kunnen aanroepen op deze Controller.
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view
        # Verbind de Controller met de View zodat UI-knoppen
        # via self.view.controller.methode() acties kunnen aanroepen
        self.view.set_controller(self)

        # =====================================================================
        # UITBREIDING 3: Action Logging — Gebruikersidentificatie bij opstart
        # Bij het opstarten wordt de gebruiker gevraagd om zijn/haar naam
        # in te voeren via een popup-dialoog (simpledialog). Deze naam wordt
        # bij elke CRUD-actie meegegeven aan de Action_Logs tabel.
        # =====================================================================
        self.model.setup_logging_table()
        self.current_user = simpledialog.askstring(
            "Inloggen",
            "Voer je gebruikersnaam in:",
            parent=self.view
        )
        # Als de gebruiker op 'Annuleren' klikt, geven we een standaardnaam
        if not self.current_user:
            self.current_user = "Onbekend"

        # Registreer de login-actie met het huidige tijdstip
        self._log_action("login")

        # Vul meteen alle schermen met actuele data bij het opstarten
        self.refresh_all_tables()

    def refresh_all_tables(self):
        """Haalt alle data op en vult de schermen, dropdowns, dashboards én CO2 tabblad.
        
        Dit is de KERN-methode die na elke CRUD-operatie wordt aangeroepen.
        Het herlaadt de volledige staat van de applicatie vanuit de databank.
        
        Volgorde:
        1. Zorg dat uitbreidingstabellen bestaan (CO2)
        2. Haal alle ruwe data op
        3. Vul de beheer-treeviews (CRUD-tabbladen)
        4. Vul de dropdownmenu's voor het loggen van verplaatsingen
        5. Bereken alle dashboard-analyses (grafieken + tabellen)
        6. Bereken de uitbreidingen (CO2 en Gezondheidsindex)
        """
        # 1. Zorg dat de CO2 tabel bestaat
        self.model.setup_co2_uitbreiding()

        # 2. Haal alle data op uit de database
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()

        # 3. Update de beheer-treeviews
        # populate_tree() wist eerst alle bestaande rijen en vult dan de nieuwe data in
        self.view.populate_tree(self.view.tree_students, studenten)
        self.view.populate_tree(self.view.tree_trans, transports)
        self.view.populate_tree(self.view.tree_logs, logs)

        # 4. Vul de dropdown menu's (Comboboxes) op de Logs-pagina
        # Format: "1 - Jan Janssen" zodat we later het ID kunnen extracten via split(" - ")
        self.view.combo_student['values'] = [f"{s[0]} - {s[1]}" for s in studenten]
        self.view.combo_vervoer['values'] = [f"{t[0]} - {t[1]}" for t in transports]
        
        # 5. Bereken en update alle analyses voor het standaard Dashboard
        self.update_dashboard_analyses(studenten, transports, logs)

        # 6. --- UITBREIDING 1: CO2 ---
        # Bouw lijsten van unieke klassen en vervoersmiddelen voor de CO2-filters
        klassen = list(set([str(s[2]).strip() for s in studenten]))
        vervoersmiddelen = [str(t[1]).strip() for t in transports]
        
        # Vul de filtercomboboxen met "Alle" als standaardoptie + de beschikbare waarden
        self.view.combo_filter_klas['values'] = ["Alle"] + klassen
        if not self.view.combo_filter_klas.get(): 
            self.view.combo_filter_klas.set("Alle")
            
        self.view.combo_filter_vervoer['values'] = ["Alle"] + vervoersmiddelen
        if not self.view.combo_filter_vervoer.get(): 
            self.view.combo_filter_vervoer.set("Alle")
            
        self.update_co2_analyse()
        self.update_gezondheid_analyse(studenten, transports, logs)

        # 7. --- UITBREIDING 3: Logging Analyse ---
        self.update_logging_analyse()

    def laad_overzicht_tabel(self):
        """Laadt de ruwe databasetabel gekozen in het dashboard tabblad.
        
        De gebruiker kan in een dropdown kiezen welke tabel hij wil bekijken
        (Students, Transport, of Mobility_log). Op basis van die keuze
        worden de juiste kolomkoppen en data ingeladen.
        """
        tabel_naam = self.view.combo_overzicht_tabel.get()
        if tabel_naam == "Students":
            data = self.model.get_all_students()
            headers = ("ID", "Naam", "Klas", "Afstand (km)")
        elif tabel_naam == "Transport":
            data = self.model.get_all_transports()
            headers = ("ID", "Type")
        elif tabel_naam == "Mobility_log":
            data = self.model.get_all_logs()
            headers = ("ID", "Student ID", "Transport ID", "Datum")
        else:
            return
        self.view.setup_overzicht_tree(headers, data)

    def update_dashboard_analyses(self, studenten, transports, logs):
        """Berekent alle statistieken met Python-logica (ZONDER SQL JOINs).
        
        Dit is het analytische hart van de applicatie. We voeren hier
        4 verschillende analyses uit:
          1. Vervoersmiddelenverdeling (welk vervoer is populairst?)
          2. Afstandsanalyse (gemiddelde afstand per vervoersmiddel)
          3. Klassenanalyse (hoe verschilt vervoer per klas?)
          4. Afstandscategorieën (kort/middel/lang — eigen analyse)
        """
        # =====================================================================
        # STAP 1: Bouw lookup-dictionaries voor snelle O(1) toegang
        # In plaats van voor elke log opnieuw door de studentenlijst te zoeken,
        # maken we een dictionary: student_id → {naam, klas, afstand}
        # Dit reduceert de tijdscomplexiteit van O(N×M) naar O(N+M).
        # =====================================================================
        stud_dict = {s[0]: {"naam": s[1], "klas": str(s[2]).strip(), "afstand": float(s[3])} for s in studenten}
        trans_dict = {t[0]: str(t[1]).strip() for t in transports}
        
        self.laad_overzicht_tabel()
        
        # =====================================================================
        # ANALYSE 1: Vervoersmiddelen Verdeling
        # Telt hoe vaak elk vervoersmiddel voorkomt in alle ritten en
        # berekent het percentage. Resultaat: tabel + staaf/cirkeldiagram.
        # =====================================================================
        totaal_logs = len(logs)
        vervoer_counts = {t_type: 0 for t_type in trans_dict.values()}
        for log in logs:
            t_type = trans_dict.get(log[2])
            if t_type in vervoer_counts:
                vervoer_counts[t_type] += 1
                
        vervoer_rows = []
        vervoer_grafiek_data = {}
        for t_type, count in vervoer_counts.items():
            pct = round((count / totaal_logs) * 100, 1) if totaal_logs > 0 else 0
            vervoer_rows.append((t_type, count, f"{pct}%"))
            vervoer_grafiek_data[t_type] = count
            
        self.view.populate_tree(self.view.tree_vervoer_stat, vervoer_rows)
        # Nieuwe universele aanroep:
        self.view.update_grafiek('vervoer', vervoer_grafiek_data, "Procentuele Verdeling per Vervoersmiddel")

        # =====================================================================
        # ANALYSE 2: Afstand Analyse
        # Berekent de gemiddelde woon-school-afstand per vervoersmiddel.
        # Hierbij koppelen we elke log aan de afstand van de bijbehorende student.
        #
        # Voorbeeld: als student Jan (5 km) 3 keer fietste, draagt dat
        # 3× 5 km bij aan de fietscategorie.
        # =====================================================================
        totale_afstand_all = sum(s[3] for s in studenten)
        gem_afstand_all = round(totale_afstand_all / len(studenten), 2) if studenten else 0
        self.view.lbl_gem_afstand_totaal.config(text=f"Algemene gemiddelde afstand tot school van alle studenten: {gem_afstand_all} km")
        
        # Groepeer de afstanden per vervoersmiddel
        vervoer_afstanden = {t_type: [] for t_type in trans_dict.values()}
        for log in logs:
            s_id = log[1]
            t_type = trans_dict.get(log[2])
            if s_id in stud_dict and t_type in vervoer_afstanden:
                vervoer_afstanden[t_type].append(stud_dict[s_id]["afstand"])
                
        afstand_rows = []
        afstand_grafiek_data = {}
        for t_type, afst_lijst in vervoer_afstanden.items():
            ritten = len(afst_lijst)
            tot_km = round(sum(afst_lijst), 1)
            gem_km = round(tot_km / ritten, 2) if ritten > 0 else 0
            afstand_rows.append((t_type, gem_km, tot_km))
            afstand_grafiek_data[t_type] = gem_km
            
        self.view.populate_tree(self.view.tree_afstand_stat, afstand_rows)
        self.view.update_grafiek('afstand', afstand_grafiek_data, "Gemiddelde afstand per vervoersmiddel (km)")

        # =====================================================================
        # ANALYSE 3: Klassenanalyse
        # Groepeert studenten per klas en berekent:
        #   - Aantal leerlingen per klas
        #   - Gemiddelde afstand per klas
        #   - De verdeling van vervoersmiddelen binnen die klas
        # =====================================================================
        klas_studenten = {}
        for s in studenten:
            klas = str(s[2]).strip()
            if klas not in klas_studenten:
                klas_studenten[klas] = []
            klas_studenten[klas].append(s)
            
        # Tel per klas hoe vaak elk vervoersmiddel is gebruikt
        klas_vervoer = {klas: {t_type: 0 for t_type in trans_dict.values()} for klas in klas_studenten}
        for log in logs:
            s_id = log[1]
            if s_id in stud_dict:
                klas = stud_dict[s_id]["klas"]
                t_type = trans_dict.get(log[2])
                if klas in klas_vervoer and t_type in klas_vervoer[klas]:
                    klas_vervoer[klas][t_type] += 1
                    
        klassen_rows = []
        klassen_grafiek_data = {}
        for klas, s_lijst in klas_studenten.items():
            aantal_stud = len(s_lijst)
            tot_afst_klas = sum(stud[3] for stud in s_lijst)
            gem_afst_klas = round(tot_afst_klas / aantal_stud, 2) if aantal_stud > 0 else 0
            
            # Maak een samenvatting-string van de vervoersverdeling
            v_dict = klas_vervoer.get(klas, {})
            verdeling_str = ", ".join([f"{k}: {v}" for k, v in v_dict.items() if v > 0])
            if not verdeling_str:
                verdeling_str = "Geen geregistreerde ritten"
                
            klassen_rows.append((klas, aantal_stud, gem_afst_klas, verdeling_str))
            klassen_grafiek_data[klas] = gem_afst_klas
            
        self.view.populate_tree(self.view.tree_klassen_stat, klassen_rows)
        self.view.update_grafiek('klassen', klassen_grafiek_data, "Gemiddelde afstand per klas (km)")

        # =====================================================================
        # ANALYSE 4: Vervoerskeuze per Afstandscategorie (Eigen Analyse)
        # We categoriseren studenten in drie groepen op basis van hun afstand:
        #   Kort   = 0–5 km    (typisch: lopend of fietsend)
        #   Middel = 5.1–10 km (typisch: fiets of bus)
        #   Lang   = >10 km    (typisch: auto of bus)
        #
        # Vervolgens tellen we per categorie welk vervoersmiddel het meest
        # wordt gebruikt. Dit toont of de vervoerskeuze logisch samenhangt
        # met de woonafstand.
        # =====================================================================
        categorieen = {"Kort (0-5 km)": {}, "Middel (5.1-10 km)": {}, "Lang (>10 km)": {}}
        for log in logs:
            s_id = log[1]
            t_type = trans_dict.get(log[2])
            if s_id in stud_dict:
                afst = stud_dict[s_id]["afstand"]
                if afst <= 5.0:
                    cat = "Kort (0-5 km)"
                elif afst <= 10.0:
                    cat = "Middel (5.1-10 km)"
                else:
                    cat = "Lang (>10 km)"
                
                if t_type not in categorieen[cat]:
                    categorieen[cat][t_type] = 0
                categorieen[cat][t_type] += 1
                
        cat_rows = []
        cat_grafiek_data = {} 
        for cat, v_counts in categorieen.items():
            totaal_ritten = sum(v_counts.values())
            if totaal_ritten > 0:
                # Bepaal het populairste vervoersmiddel via max() op de tellingen
                populair = max(v_counts, key=v_counts.get)
                verdeling = ", ".join([f"{k}: {v}" for k, v in v_counts.items() if v > 0])
            else:
                populair = "-"
                verdeling = "Geen ritten"
            
            cat_rows.append((cat, totaal_ritten, populair, verdeling))
            cat_grafiek_data[cat] = totaal_ritten
            
        self.view.populate_tree(self.view.tree_categorie_stat, cat_rows)
        self.view.update_grafiek('categorie', cat_grafiek_data, "Totaal aantal ritten per afstandscategorie")

    # =========================================================================
    # Uitbreiding 1: CO2 Analyse
    # Deze analyse berekent de totale CO₂-uitstoot per vervoersmiddel,
    # met optionele filters op klas, vervoerstype en afstandscategorie.
    # =========================================================================
    def update_co2_analyse(self):
        """Uitbreiding 1: Berekent de CO2 uitstoot met kogelvrije filters en fallbacks.
        
        Formule per rit:
          CO₂ (gram) = afstand_student (km) × uitstoot_per_km (g/km)
        
        Voorbeeld:
          Een autorit van een student die 8 km van school woont:
          8 km × 120 g/km = 960 gram CO₂
        """
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()
        
        # Haal CO2-normen uit de databank en converteer naar dictionary
        # voor snelle lookup: {"fiets": 0.0, "auto": 120.0, ...}
        db_normen = dict(self.model.get_co2_normen())
        # Fallback-normen voor het geval de databank onvolledig is
        fallback_normen = {'fiets': 0.0, 'bus': 50.0, 'auto': 120.0, 'te voet': 0.0}

        # Lees de huidige filterinstellingen uit de UI
        f_klas = self.view.combo_filter_klas.get().strip()
        f_vervoer = self.view.combo_filter_vervoer.get().strip()
        f_afstand = self.view.combo_filter_afstand.get().strip()

        stud_dict = {s[0]: {"klas": str(s[2]).strip(), "afstand": float(s[3])} for s in studenten}
        trans_dict = {t[0]: str(t[1]).strip() for t in transports}

        # Initialiseer accumulatoren per vervoersmiddel
        co2_per_vervoer = {t_type: {"ritten": 0, "co2": 0.0} for t_type in trans_dict.values()}

        # ── Hoofdlus: itereer over alle ritten en pas filters toe ──
        for log in logs:
            s_id = log[1]
            t_id = log[2]

            if s_id in stud_dict and t_id in trans_dict:
                klas = stud_dict[s_id]["klas"]
                afstand = stud_dict[s_id]["afstand"]
                t_type = trans_dict[t_id]

                # Filter 1: Klas — sla deze rit over als hij niet matcht
                if f_klas != "Alle" and klas != f_klas:
                    continue
                # Filter 2: Vervoersmiddel
                if f_vervoer != "Alle" and t_type != f_vervoer:
                    continue
                # Filter 3: Afstandscategorie
                if f_afstand != "Alle":
                    if f_afstand == "Kort (0-5 km)" and afstand > 5.0:
                        continue
                    elif f_afstand == "Middel (5.1-10 km)" and (afstand <= 5.0 or afstand > 10.0):
                        continue
                    elif f_afstand == "Lang (>10 km)" and afstand <= 10.0:
                        continue

                # Zoek de uitstoot-norm: eerst in de databank, dan in de fallback
                zoek_naam = t_type.lower()
                if zoek_naam in db_normen:
                    uitstoot_per_km = db_normen[zoek_naam]
                else:
                    uitstoot_per_km = fallback_normen.get(zoek_naam, 0.0)
                
                # Bereken de CO₂ voor deze ene rit: afstand × uitstoot_per_km
                totale_co2_rit = afstand * uitstoot_per_km

                co2_per_vervoer[t_type]["ritten"] += 1
                co2_per_vervoer[t_type]["co2"] += totale_co2_rit

        # Bouw de tabelrijen en grafiekdata op
        co2_rows = []
        co2_grafiek_data = {}
        for t_type, data in co2_per_vervoer.items():
            ritten = data["ritten"]
            co2 = round(data["co2"], 1)
            
            co2_rows.append((t_type, ritten, co2))
            co2_grafiek_data[t_type] = co2

        self.view.populate_tree(self.view.tree_co2_stat, co2_rows)
        self.view.update_grafiek('co2', co2_grafiek_data, "Totale CO₂ Uitstoot (Gram) o.b.v. Filters")

    # =========================================================================
    # CRUD Acties
    # Elke methode hieronder volgt hetzelfde patroon:
    #   1. Haal invoer op uit de View (formulier of selectie)
    #   2. Valideer de invoer (niet leeg? geldig getal?)
    #   3. Voer de actie uit op het Model (toevoegen/wijzigen/verwijderen)
    #   4. Maak het formulier leeg
    #   5. Herlaad ALLE tabellen via refresh_all_tables()
    #   6. Toon een bevestigingsbericht
    #
    # Door na elke actie refresh_all_tables() aan te roepen, zijn de
    # dashboards en grafieken altijd 100% up-to-date.
    # =========================================================================
    def add_student(self):
        """Leest de formuliervelden, valideert ze, en voegt een student toe."""
        data = self.view.get_student_form_data()
        if not all(data.values()): return self.view.show_error("Vul alles in!")
        try:
            self.model.add_student(data['naam'], data['klas'], float(data['afstand'].replace(',', '.')))
            self._log_action("create")
            self.view.clear_student_form()
            self.refresh_all_tables()
            self.view.show_info("Student toegevoegd.")
        except ValueError: self.view.show_error("Ongeldige afstand.")

    def update_student(self):
        """Wijzigt de geselecteerde student met de huidige formulierwaarden."""
        student_id = self.view.get_selected_id(self.view.tree_students)
        if not student_id: return self.view.show_error("Selecteer een student.")
        data = self.view.get_student_form_data()
        if not all(data.values()): return self.view.show_error("Vul alles in!")
        try:
            self.model.update_student(student_id, data['naam'], data['klas'], float(data['afstand'].replace(',', '.')))
            self._log_action("update")
            self.view.clear_student_form()
            self.refresh_all_tables()
            self.view.show_info("Student aangepast.")
        except ValueError: self.view.show_error("Ongeldige afstand.")

    def delete_student(self):
        """Verwijdert de geselecteerde student en al zijn/haar ritten."""
        student_id = self.view.get_selected_id(self.view.tree_students)
        if not student_id: return self.view.show_error("Selecteer een student.")
        self.model.delete_student(student_id)
        self._log_action("delete")
        self.view.clear_student_form()
        self.refresh_all_tables()
        self.view.show_info("Student en bijbehorende logs verwijderd.")

    def add_transport(self):
        """Voegt een nieuw vervoersmiddel toe op basis van het invoerveld."""
        type_vervoer = self.view.entry_vervoer_type.get()
        if not type_vervoer: return self.view.show_error("Vul een type in.")
        self.model.add_transport(type_vervoer)
        self._log_action("create")
        self.view.entry_vervoer_type.delete(0, 'end')
        self.refresh_all_tables()
        self.view.show_info("Vervoer toegevoegd.")

    def delete_transport(self):
        """Verwijdert het geselecteerde vervoersmiddel en alle gekoppelde ritten."""
        trans_id = self.view.get_selected_id(self.view.tree_trans)
        if not trans_id: return self.view.show_error("Selecteer vervoer.")
        self.model.delete_transport(trans_id)
        self._log_action("delete")
        self.refresh_all_tables()
        self.view.show_info("Vervoer en bijbehorende logs verwijderd.")

    def add_log(self):
        """Registreert een nieuwe verplaatsing: student + vervoer + datum.
        
        De student- en vervoer-ID's worden uit de combobox-tekst geëxtraheerd
        door te splitsen op " - " en het eerste deel te nemen.
        """
        student_val = self.view.combo_student.get()
        vervoer_val = self.view.combo_vervoer.get()
        datum = self.view.entry_datum.get()

        if not student_val or not vervoer_val or not datum:
            return self.view.show_error("Vul alle log-velden in!")

        # Extractie van het ID uit het formaat "42 - Jan Janssen"
        student_id = int(student_val.split(" - ")[0])
        vervoer_id = int(vervoer_val.split(" - ")[0])

        self.model.add_log(student_id, vervoer_id, datum)
        self._log_action("create")
        self.view.entry_datum.delete(0, 'end')
        self.refresh_all_tables()
        self.view.show_info("Verplaatsing opgeslagen.")

    def delete_log(self):
        """Verwijdert de geselecteerde verplaatsingsregistratie."""
        log_id = self.view.get_selected_id(self.view.tree_logs)
        if not log_id: return self.view.show_error("Selecteer een log.")
        self.model.delete_log(log_id)
        self._log_action("delete")
        self.refresh_all_tables()
        self.view.show_info("Log verwijderd.")

    # =========================================================================
    # Uitbreiding 2: Gezondheidsindex (Actief vs. Passief Vervoer)
    #
    # Het concept:
    #   We classificeren elk vervoersmiddel als "Actief" (fysieke inspanning)
    #   of "Passief" (gemotoriseerd):
    #     Actief  = fiets, te voet
    #     Passief = auto, bus
    #
    #   Per klas berekenen we welk percentage van de ritten actief is.
    #   Dit noemen we de "Gezondheidsindex": hoe hoger, hoe gezonder.
    #
    # Formule:
    #   Gezondheidsindex (%) = (actieve ritten / totaal ritten) × 100
    # =========================================================================
    def update_gezondheid_analyse(self, studenten, transports, logs):
        """Berekent de Gezondheidsindex (Actief vs. Passief) per klas en voor de gehele school."""
        # Bouw lookup-tabellen: student_id → klas, transport_id → type (lowercase)
        stud_klas = {s[0]: str(s[2]).strip() for s in studenten}
        trans_type = {t[0]: str(t[1]).strip().lower() for t in transports}
        
        # Verzamel alle unieke klassen en initialiseer tellers op 0
        classes = sorted(list(set(stud_klas.values())))
        class_active = {klas: 0 for klas in classes}
        class_passive = {klas: 0 for klas in classes}
        
        # ── Classificatielus: elke rit wordt als Actief of Passief geteld ──
        for log in logs:
            student_id = log[1]
            transport_id = log[2]
            klas = stud_klas.get(student_id)
            t_type = trans_type.get(transport_id)
            
            if klas and t_type:
                if t_type in ['fiets', 'te voet']:
                    class_active[klas] += 1
                elif t_type in ['auto', 'bus']:
                    class_passive[klas] += 1
                    
        # Bouw de tabelrijen en staafdiagramdata op
        rows = []
        bar_data = {}
        for klas in classes:
            actief = class_active[klas]
            passief = class_passive[klas]
            tot = actief + passief
            pct = round((actief / tot) * 100, 1) if tot > 0 else 0.0
            
            rows.append((klas, actief, passief, f"{pct}%"))
            bar_data[klas] = pct
            
        self.view.populate_tree(self.view.tree_gezondheid_stat, rows)
        
        # Bereken ook de schoolbrede totalen voor het cirkeldiagram
        totaal_actief = sum(class_active.values())
        totaal_passief = sum(class_passive.values())
        
        # Het cirkeldiagram toont de verhouding voor de HELE school,
        # terwijl het staafdiagram de index PER KLAS toont
        pie_data = {
            "Actief Vervoer (Fiets, Voet)": totaal_actief,
            "Passief Vervoer (Auto, Bus)": totaal_passief
        }
        
        # We sturen hier een dict met twee subsets ('pie' en 'bar'),
        # zodat de View het juiste subset kan kiezen bij het wisselen
        self.view.update_grafiek(
            'gezondheid', 
            {'pie': pie_data, 'bar': bar_data}, 
            "Gezondheidsindex (Actief vs. Passief)"
        )

    # =========================================================================
    # UITBREIDING 3: Action Logging — Helper en Analyse
    #
    # _log_action():  Slaat een actie op in de Action_Logs tabel.
    # update_logging_analyse(): Berekent statistieken in pure Python:
    #   - Aantal acties per gebruiker
    #   - Aantal acties per type (login, create, update, delete)
    #   - Meest actieve gebruiker(s)
    # =========================================================================
    def _log_action(self, action_type):
        """Schrijft een actie-logregel weg naar de Action_Logs tabel.
        
        Wordt automatisch aangeroepen bij elke CRUD-operatie en bij login.
        Gebruikt datetime.now() om het exacte tijdstip vast te leggen.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.model.add_action_log(self.current_user, action_type, timestamp)

    def update_logging_analyse(self):
        """Uitbreiding 3: Berekent logging-statistieken in pure Python.
        
        Drie analyses:
          1. Acties per gebruiker — wie heeft wat gedaan?
          2. Acties per type — hoeveel creates vs. deletes?
          3. Meest actieve gebruiker(s) — wie heeft de meeste acties?
        """
        action_logs = self.model.get_all_action_logs()

        # ── Analyse 1: Acties per gebruiker ──
        acties_per_user = {}
        for log in action_logs:
            user = log[1]
            if user not in acties_per_user:
                acties_per_user[user] = 0
            acties_per_user[user] += 1

        # ── Analyse 2: Acties per type ──
        acties_per_type = {}
        for log in action_logs:
            a_type = log[2]
            if a_type not in acties_per_type:
                acties_per_type[a_type] = 0
            acties_per_type[a_type] += 1

        # ── Analyse 3: Meest actieve gebruiker(s) ──
        if acties_per_user:
            max_count = max(acties_per_user.values())
            meest_actief = [user for user, count in acties_per_user.items() if count == max_count]
        else:
            max_count = 0
            meest_actief = ["-"]

        # ── Vul de tabel "Acties per Gebruiker" ──
        user_rows = [(user, count) for user, count in acties_per_user.items()]
        self.view.populate_tree(self.view.tree_logging_user, user_rows)

        # ── Vul de tabel "Acties per Type" ──
        type_rows = [(a_type, count) for a_type, count in acties_per_type.items()]
        self.view.populate_tree(self.view.tree_logging_type, type_rows)

        # ── Vul de tabel "Meest Actief" ──
        actief_rows = [(user, acties_per_user.get(user, 0)) for user in meest_actief]
        self.view.populate_tree(self.view.tree_logging_actief, actief_rows)

        # ── Grafiek: Acties per type als cirkeldiagram ──
        self.view.update_grafiek('logging', acties_per_type, "Verdeling Acties per Type")

    def start(self):
        """Start de Tkinter mainloop — het programma draait tot het venster sluit."""
        self.view.mainloop()