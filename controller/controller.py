class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.refresh_all_tables()

    def refresh_all_tables(self):
        """Haalt alle data op en vult de schermen, dropdowns én dashboards."""
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()

        # Update de beheer-treeviews
        self.view.populate_tree(self.view.tree_students, studenten)
        self.view.populate_tree(self.view.tree_trans, transports)
        self.view.populate_tree(self.view.tree_logs, logs)

        # Vul de dropdown menu's (Comboboxes) op de Logs-pagina
        self.view.combo_student['values'] = [f"{s[0]} - {s[1]}" for s in studenten]
        self.view.combo_vervoer['values'] = [f"{t[0]} - {t[1]}" for t in transports]
        
        # --- Bereken en update alle analyses voor het Dashboard ---
        self.update_dashboard_analyses(studenten, transports, logs)

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
        # Hulpdictionaries bouwen voor snelle lookup
        stud_dict = {s[0]: {"naam": s[1], "klas": s[2], "afstand": s[3]} for s in studenten}
        trans_dict = {t[0]: t[1] for t in transports}
        
        # 1. Update de ruwe tabelweergave
        self.laad_overzicht_tabel()
        
        # 2. Vervoersmiddelen Analyse (Aantal per type + procentuele verdeling)
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

        # 3. Afstand Analyse (Algemeen gemiddelde + gemiddelde per vervoersmiddel)
        totale_afstand_all = sum(s[3] for s in studenten)
        gem_afstand_all = round(totale_afstand_all / len(studenten), 2) if studenten else 0
        self.view.lbl_gem_afstand_totaal.config(text=f"Algemene gemiddelde afstand tot school van alle studenten: {gem_afstand_all} km")
        
        # Bereken ritten en kilometers per vervoersmiddel (Inclusief de EXTRA eigen analyse: Totaal aantal km)
        vervoer_afstanden = {t_type: [] for t_type in trans_dict.values()}
        for log in logs:
            s_id = log[1]
            t_type = trans_dict.get(log[2])
            if s_id in stud_dict and t_type in vervor_afstanden:
                vervoer_afstanden[t_type].append(stud_dict[s_id]["afstand"])
                
        afstand_rows = []
        afstand_grafiek_data = {}
        for t_type, afst_lijst in vervoer_afstanden.items():
            ritten = len(afst_lijst)
            tot_km = round(sum(afst_lijst), 1)
            gem_km = round(tot_km / ritten, 2) if ritten > 0 else 0
            # Extra analyse is de tot_km kolom
            afstand_rows.append((t_type, gem_km, tot_km))
            afstand_grafiek_data[t_type] = gem_km
            
        self.view.populate_tree(self.view.tree_afstand_stat, afstand_rows)
        self.view.teken_grafiek(self.view.canvas_afstand, afstand_grafiek_data, "Gemiddelde afstand per vervoersmiddel (km)")

        # 4. Klassenanalyse (Aantal leerlingen, gemiddelde afstand, verdeling per klas)
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

    # --- Studenten CRUD Acties (Behouden) ---
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

    # --- Vervoer CRUD Acties (Behouden) ---
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

    # --- Logs CRUD Acties (Behouden) ---
    def add_log(self):
        student_val = self.view.combo_student.get()
        vervoer_val = self.view.combo_vervoer.get()
        datum = self.view.entry_datum.get()

        if not student_val or not vervoer_val or not datum:
            return self.view.show_error("Vul alle log-velden in!")

        student_id = int(student_val.split(" - ")[0])
        vervoer_id = int(vervoer_val.split(" - ")[0])

        self.model.add_log(student_id, vervor_id, datum)
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