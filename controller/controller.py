import tkinter as tk
from tkinter import ttk

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.refresh_all_tables()

    def refresh_all_tables(self):
        """Haalt alle data op en vult de schermen, dropdowns, dashboards én CO2 tabblad."""
        # 1. Zorg dat de CO2 en Aanwezigheden tabellen bestaan in de database
        self.model.setup_co2_uitbreiding()
        if hasattr(self.model, 'setup_aanwezigheden_uitbreiding'):
            self.model.setup_aanwezigheden_uitbreiding()

        # 2. Haal alle basisdata op uit de database
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()

        # 3. Update de standaard beheer-treeviews
        self.view.populate_tree(self.view.tree_students, studenten)
        self.view.populate_tree(self.view.tree_trans, transports)
        self.view.populate_tree(self.view.tree_logs, logs)

        # 4. Vul de dropdown menu's (Comboboxes) op de Logs-pagina
        self.view.combo_student['values'] = [f"{s[0]} - {s[1]}" for s in studenten]
        self.view.combo_vervoer['values'] = [f"{t[0]} - {t[1]}" for t in transports]
        
        # 5. Bereken en update alle analyses voor het standaard Dashboard
        self.update_dashboard_analyses(studenten, transports, logs)

        # 6. --- UITBREIDING 1: CO2 ---
        klassen = list(set([str(s[2]).strip() for s in studenten]))
        vervoersmiddelen = [str(t[1]).strip() for t in transports]
        
        self.view.combo_filter_klas['values'] = ["Alle"] + klassen
        if not self.view.combo_filter_klas.get(): 
            self.view.combo_filter_klas.set("Alle")
            
        self.view.combo_filter_vervoer['values'] = ["Alle"] + vervoersmiddelen
        if not self.view.combo_filter_vervoer.get(): 
            self.view.combo_filter_vervoer.set("Alle")
            
        self.update_co2_analyse()
        self.update_gezondheid_analyse(studenten, transports, logs)

        # 7. --- UITBREIDING 2: AANWEZIGHEDEN (RECHTSTREEKS VIA FRAME) ---
        if hasattr(self.view, 'aanwezigheid_beheer_frame'):
            # Vul de tabel met opgeslagen aanwezigheden
            try:
                aanw_data = self.model.get_all_aanwezigheden()
                self.view.populate_tree(self.view.tree_aanw, aanw_data)
            except Exception as e:
                print(f"Opmerking: Aanwezigheidstabel nog leeg of {e}")

            # Vul de studenten dropdown in het Aanwezigheden frame naar jouw nieuwe component
            student_lijst = [f"{s[0]} - {s[1]}" for s in studenten]
            self.view.aanwezigheid_beheer_frame.combo_student['values'] = student_lijst

    def laad_overzicht_tabel(self):
        """Laadt de ruwe databasetabel gekozen in het dashboard tabblad."""
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
        """Berekent alle statistieken met Python-logica (ZONDER SQL JOINs)."""
        stud_dict = {s[0]: {"naam": s[1], "klas": str(s[2]).strip(), "afstand": float(s[3])} for s in studenten}
        trans_dict = {t[0]: str(t[1]).strip() for t in transports}
        
        self.laad_overzicht_tabel()
        
        # 2. Vervoersmiddelen Analyse
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
        self.view.update_grafiek('vervoer', vervoer_grafiek_data, "Procentuele Verdeling per Vervoersmiddel")

        # 3. Afstand Analyse
        totale_afstand_all = sum(s[3] for s in studenten)
        gem_afstand_all = round(totale_afstand_all / len(studenten), 2) if studenten else 0
        self.view.lbl_gem_afstand_totaal.config(text=f"Algemene gemiddelde afstand: {gem_afstand_all} km")
        
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

        # 4. Klassenanalyse
        klas_studenten = {}
        for s in studenten:
            klas = str(s[2]).strip()
            if klas not in klas_studenten:
                klas_studenten[klas] = []
            klas_studenten[klas].append(s)
            
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
            
            v_dict = klas_vervoer.get(klas, {})
            verdeling_str = ", ".join([f"{k}: {v}" for k, v in v_dict.items() if v > 0])
            if not verdeling_str:
                verdeling_str = "Geen geregistreerde ritten"
                
            klassen_rows.append((klas, aantal_stud, gem_afst_klas, verdeling_str))
            klassen_grafiek_data[klas] = gem_afst_klas
            
        self.view.populate_tree(self.view.tree_klassen_stat, klassen_rows)
        self.view.update_grafiek('klassen', klassen_grafiek_data, "Gemiddelde afstand per klas (km)")

        # 5. EXTRA EIGEN ANALYSE: Vervoerskeuze per Afstandscategorie
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
                populair = max(v_counts, key=v_counts.get)
                verdeling = ", ".join([f"{k}: {v}" for k, v in v_counts.items() if v > 0])
            else:
                populair = "-"
                verdeling = "Geen ritten"
            
            cat_rows.append((cat, totaal_ritten, populair, verdeling))
            cat_grafiek_data[cat] = totaal_ritten
            
        self.view.populate_tree(self.view.tree_categorie_stat, cat_rows)
        self.view.update_grafiek('categorie', cat_grafiek_data, "Totaal aantal ritten per afstandscategorie")

    # --- Uitbreiding 1: CO2 Analyse ---
    def update_co2_analyse(self):
        """Uitbreiding 1: Berekent de CO2 uitstoot met kogelvrije filters en fallbacks."""
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()
        
        db_normen = dict(self.model.get_co2_normen())
        fallback_normen = {'fiets': 0.0, 'bus': 50.0, 'auto': 120.0, 'te voet': 0.0}

        f_klas = self.view.combo_filter_klas.get().strip()
        f_vervoer = self.view.combo_filter_vervoer.get().strip()
        f_afstand = self.view.combo_filter_afstand.get().strip()

        stud_dict = {s[0]: {"klas": str(s[2]).strip(), "afstand": float(s[3])} for s in studenten}
        trans_dict = {t[0]: str(t[1]).strip() for t in transports}

        co2_per_vervoer = {t_type: {"ritten": 0, "co2": 0.0} for t_type in trans_dict.values()}

        for log in logs:
            s_id = log[1]
            t_id = log[2]

            if s_id in stud_dict and t_id in trans_dict:
                klas = stud_dict[s_id]["klas"]
                afstand = stud_dict[s_id]["afstand"]
                t_type = trans_dict[t_id]

                if f_klas != "Alle" and klas != f_klas:
                    continue
                if f_vervoer != "Alle" and t_type != f_vervoer:
                    continue
                if f_afstand != "Alle":
                    if f_afstand == "Kort (0-5 km)" and afstand > 5.0:
                        continue
                    elif f_afstand == "Middel (5.1-10 km)" and (afstand <= 5.0 or afstand > 10.0):
                        continue
                    elif f_afstand == "Lang (>10 km)" and afstand <= 10.0:
                        continue

                zoek_naam = t_type.lower()
                if zoek_naam in db_normen:
                    uitstoot_per_km = db_normen[zoek_naam]
                else:
                    uitstoot_per_km = fallback_normen.get(zoek_naam, 0.0)
                
                totale_co2_rit = afstand * uitstoot_per_km

                co2_per_vervoer[t_type]["ritten"] += 1
                co2_per_vervoer[t_type]["co2"] += totale_co2_rit

        co2_rows = []
        co2_grafiek_data = {}
        for t_type, data in co2_per_vervoer.items():
            ritten = data["ritten"]
            co2 = round(data["co2"], 1)
            
            co2_rows.append((t_type, ritten, co2))
            co2_grafiek_data[t_type] = co2

        self.view.populate_tree(self.view.tree_co2_stat, co2_rows)
        self.view.update_grafiek('co2', co2_grafiek_data, "Totale CO₂ Uitstoot (Gram) o.b.v. Filters")

    def update_gezondheid_analyse(self, studenten, transports, logs):
        """Berekent de Gezondheidsindex (Actief vs. Passief) per klas."""
        stud_klas = {s[0]: str(s[2]).strip() for s in studenten}
        trans_type = {t[0]: str(t[1]).strip().lower() for t in transports}
        
        classes = sorted(list(set(stud_klas.values())))
        class_active = {klas: 0 for klas in classes}
        class_passive = {klas: 0 for klas in classes}
        
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
        
        totaal_actief = sum(class_active.values())
        totaal_passief = sum(class_passive.values())
        
        pie_data = {
            "Actief Vervoer (Fiets, Voet)": totaal_actief,
            "Passief Vervoer (Auto, Bus)": totaal_passief
        }
        
        self.view.update_grafiek(
            'gezondheid', 
            {'pie': pie_data, 'bar': bar_data}, 
            "Gezondheidsindex (Actief vs. Passief)"
        )

    # --- RECHTSTREEKSE INTERACTIE MET HET AANWEZIGHEDEN FRAME ---
    def add_aanwezigheid(self):
        """Voegt een nieuwe aanwezigheidsregistratie toe."""
        frame = self.view.aanwezigheid_beheer_frame
        stud_val = frame.combo_student.get()
        datum = frame.entry_datum.get().strip()
        status = frame.combo_status.get()

        if not stud_val or not datum or not status:
            return self.view.show_error("Vul alle velden in om te registreren!")

        try:
            student_id = int(stud_val.split(" - ")[0])
            self.model.add_aanwezigheid(student_id, datum, status)
            frame.entry_datum.delete(0, 'end')
            self.refresh_all_tables()
            self.view.show_info("Aanwezigheid succesvol geregistreerd.")
        except Exception as e:
            self.view.show_error(f"Fout bij opslaan: {str(e)}")

    def delete_aanwezigheid(self):
        """Verwijdert de geselecteerde registratie."""
        frame = self.view.aanwezigheid_beheer_frame
        aanw_id = self.view.get_selected_id(frame.tree_aanw)
        
        if not aanw_id:
            return self.view.show_error("Selecteer eerst een rij uit de tabel.")

        self.model.delete_aanwezigheid(aanw_id)
        self.refresh_all_tables()
        self.view.show_info("Registratie succesvol verwijderd.")

    def update_aanwezigheid_analyse(self):
        """Genereert de gekozen analytische tabel en bijbehorende grafiek."""
        frame = self.view.aanwezigheid_analyse_frame
        analyse_type = frame.combo_analyse.get()
        tree_analyse = frame.tree_aanw_analyse
        chart_data = {}

        if analyse_type == "Aantal afwezigheden per klas":
            headers = ("Klas", "Aantal Afwezig")
            data = self.model.query_afwezigheden_per_klas()
            titel = "Aantal afwezigheden per klas"
            chart_data = {str(row[0]): row[1] for row in data}

        elif analyse_type == "Percentage aanwezig per klas":
            headers = ("Klas", "Aanwezigheid (%)")
            data = self.model.query_percentage_aanwezig_per_klas()
            titel = "Aanwezigheidspercentage per klas"
            chart_data = {str(row[0]): row[1] for row in data}

        else:  # Vervoersmiddel vs Aanwezigheid
            headers = ("Vervoersmiddel", "Status", "Aantal")
            data = self.model.query_vervoer_vs_aanwezigheid()
            titel = "Status per Vervoersmiddel"
            chart_data = {f"{row[0]} ({row[1]})": row[2] for row in data}

        tree_analyse["columns"] = headers
        tree_analyse["show"] = "headings"
        for h in headers:
            tree_analyse.heading(h, text=h)
            tree_analyse.column(h, anchor="center", width=150)

        self.view.populate_tree(tree_analyse, data)
        self.view.update_grafiek('aanwezigheid', chart_data, titel)

    # --- Standaard CRUD Acties ---
    def add_student(self):
        data = self.view.get_student_form_data()
        if not all(data.values()): return self.view.show_error("Vul alles in!")
        try:
            self.model.add_student(data['naam'], data['klas'], float(data['afstand'].replace(',', '.')))
            self.view.clear_student_form()
            self.refresh_all_tables()
            self.view.show_info("Student toegevoegd.")
        except ValueError: self.view.show_error("Ongeldige afstand.")

    def update_student(self):
        student_id = self.view.get_selected_id(self.view.tree_students)
        if not student_id: return self.view.show_error("Selecteer een student.")
        data = self.view.get_student_form_data()
        if not all(data.values()): return self.view.show_error("Vul alles in!")
        try:
            self.model.update_student(student_id, data['naam'], data['klas'], float(data['afstand'].replace(',', '.')))
            self.view.clear_student_form()
            self.refresh_all_tables()
            self.view.show_info("Student aangepast.")
        except ValueError: self.view.show_error("Ongeldige afstand.")

    def delete_student(self):
        student_id = self.view.get_selected_id(self.view.tree_students)
        if not student_id: return self.view.show_error("Selecteer een student.")
        self.model.delete_student(student_id)
        self.view.clear_student_form()
        self.refresh_all_tables()
        self.view.show_info("Student en bijbehorende logs verwijderd.")

    def add_transport(self):
        type_vervoer = self.view.entry_vervoer_type.get()
        if not type_vervoer: return self.view.show_error("Vul een type in.")
        self.model.add_transport(type_vervoer)
        self.view.entry_vervoer_type.delete(0, 'end')
        self.refresh_all_tables()
        self.view.show_info("Vervoer toegevoegd.")

    def delete_transport(self):
        trans_id = self.view.get_selected_id(self.view.tree_trans)
        if not trans_id: return self.view.show_error("Selecteer vervoer.")
        self.model.delete_transport(trans_id)
        self.refresh_all_tables()
        self.view.show_info("Vervoer en bijbehorende logs verwijderd.")

    def add_aanwezigheid(self):
        """Voegt een nieuwe aanwezigheidsregistratie toe."""
        frame = self.view.aanwezigheid_beheer_frame
        stud_val = frame.combo_student.get()
        datum = frame.entry_datum.get().strip()
        gui_status = frame.combo_status.get()

        # Mapping zorgt dat de database de juiste hoofdletters krijgt
        status_mapping = {
            "Aanwezig": "Aanwezig",
            "Afwezig": "Afwezig",
            "Te laat": "Te laat"
        }
        
        status = status_mapping.get(gui_status)

        if not stud_val or not datum or not status:
            return self.view.show_error("Vul alle velden in om te registreren!")

        try:
            student_id = int(stud_val.split(" - ")[0])
            self.model.add_aanwezigheid(student_id, datum, status)
            frame.entry_datum.delete(0, 'end')
            self.refresh_all_tables()
            self.view.show_info("Aanwezigheid succesvol geregistreerd.")
        except Exception as e:
            self.view.show_error(f"Fout bij opslaan: {str(e)}")

    def delete_log(self):
        log_id = self.view.get_selected_id(self.view.tree_logs)
        if not log_id: return self.view.show_error("Selecteer een log.")
        self.model.delete_log(log_id)
        self.refresh_all_tables()
        self.view.show_info("Log verwijderd.")

    def start(self):
        self.view.mainloop()