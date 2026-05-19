class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.refresh_all_tables()

    def refresh_all_tables(self):
        """Haalt alle data op en vult de schermen, dropdowns, dashboards én CO2 tabblad."""
        # 1. Zorg dat de CO2 tabel bestaat (Uitbreiding)
        self.model.setup_co2_uitbreiding()

        # 2. Haal alle data op uit de database
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()

        # 3. Update de beheer-treeviews
        self.view.populate_tree(self.view.tree_students, studenten)
        self.view.populate_tree(self.view.tree_trans, transports)
        self.view.populate_tree(self.view.tree_logs, logs)

        # 4. Vul de dropdown menu's (Comboboxes) op de Logs-pagina
        self.view.combo_student['values'] = [f"{s[0]} - {s[1]}" for s in studenten]
        self.view.combo_vervoer['values'] = [f"{t[0]} - {t[1]}" for t in transports]
        
        # 5. Bereken en update alle analyses voor het standaard Dashboard
        self.update_dashboard_analyses(studenten, transports, logs)

        # 6. --- UITBREIDING 1: CO2 ---
        # Vul de dropdown filters voor de CO2 tab
        klassen = list(set([s[2] for s in studenten]))
        vervoersmiddelen = [t[1] for t in transports]
        
        self.view.combo_filter_klas['values'] = ["Alle"] + klassen
        if not self.view.combo_filter_klas.get(): 
            self.view.combo_filter_klas.set("Alle")
            
        self.view.combo_filter_vervoer['values'] = ["Alle"] + vervoersmiddelen
        if not self.view.combo_filter_vervoer.get(): 
            self.view.combo_filter_vervoer.set("Alle")
            
        # Update direct de CO2 grafiek en tabel
        self.update_co2_analyse()

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
        stud_dict = {s[0]: {"naam": s[1], "klas": s[2], "afstand": s[3]} for s in studenten}
        trans_dict = {t[0]: t[1] for t in transports}
        
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
        self.view.teken_grafiek(self.view.canvas_vervoer, vervoer_grafiek_data, "Aantal verplaatsingen per type")

        # 3. Afstand Analyse
        totale_afstand_all = sum(s[3] for s in studenten)
        gem_afstand_all = round(totale_afstand_all / len(studenten), 2) if studenten else 0
        self.view.lbl_gem_afstand_totaal.config(text=f"Algemene gemiddelde afstand tot school van alle studenten: {gem_afstand_all} km")
        
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
        self.view.teken_grafiek(self.view.canvas_afstand, afstand_grafiek_data, "Gemiddelde afstand per vervoersmiddel (km)")

        # 4. Klassenanalyse
        klas_studenten = {}
        for s in studenten:
            klas = s[2]
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
        self.view.teken_grafiek(self.view.canvas_klassen, klassen_grafiek_data, "Gemiddelde afstand per klas (km)")

    # --- Uitbreiding 1: CO2 Analyse ---
    def update_co2_analyse(self):
        """Uitbreiding 1: Berekent de CO2 uitstoot met toepassing van filters."""
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()
        co2_normen = dict(self.model.get_co2_normen()) 

        # Haal actieve filters op
        f_klas = self.view.combo_filter_klas.get()
        f_vervoer = self.view.combo_filter_vervoer.get()
        f_afstand = self.view.combo_filter_afstand.get()

        stud_dict = {s[0]: {"klas": s[2], "afstand": s[3]} for s in studenten}
        trans_dict = {t[0]: t[1] for t in transports}

        co2_per_vervoer = {t_type: {"ritten": 0, "co2": 0.0} for t_type in trans_dict.values()}

        for log in logs:
            s_id = log[1]
            t_id = log[2]

            if s_id in stud_dict and t_id in trans_dict:
                klas = stud_dict[s_id]["klas"]
                afstand = stud_dict[s_id]["afstand"]
                t_type = trans_dict[t_id]

                # --- 1. Toepassen van Filters ---
                if f_klas != "Alle" and klas != f_klas:
                    continue
                if f_vervoer != "Alle" and t_type != f_vervoer:
                    continue
                if f_afstand != "Alle":
                    if f_afstand == "Kort (0-5 km)" and afstand > 5:
                        continue
                    elif f_afstand == "Middel (5.1-10 km)" and (afstand <= 5 or afstand > 10):
                        continue
                    elif f_afstand == "Lang (>10 km)" and afstand <= 10:
                        continue

                # --- 2. Berekening ---
                uitstoot_per_km = co2_normen.get(t_type.lower(), 0.0) 
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
        self.view.teken_grafiek(self.view.canvas_co2, co2_grafiek_data, "Totale CO₂ Uitstoot (Gram) o.b.v. Filters")

    # --- Studenten CRUD Acties ---
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

    # --- Vervoer CRUD Acties ---
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

    # --- Logs CRUD Acties ---
    def add_log(self):
        student_val = self.view.combo_student.get()
        vervoer_val = self.view.combo_vervoer.get()
        datum = self.view.entry_datum.get()

        if not student_val or not vervoer_val or not datum:
            return self.view.show_error("Vul alle log-velden in!")

        student_id = int(student_val.split(" - ")[0])
        vervoer_id = int(vervoer_val.split(" - ")[0])

        self.model.add_log(student_id, vervoer_id, datum)
        self.view.entry_datum.delete(0, 'end')
        self.refresh_all_tables()
        self.view.show_info("Verplaatsing opgeslagen.")

    def delete_log(self):
        log_id = self.view.get_selected_id(self.view.tree_logs)
        if not log_id: return self.view.show_error("Selecteer een log.")
        self.model.delete_log(log_id)
        self.refresh_all_tables()
        self.view.show_info("Log verwijderd.")

    def start(self):
        self.view.mainloop()