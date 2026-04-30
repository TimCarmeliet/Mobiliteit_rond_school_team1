class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.refresh_all_tables()

    def refresh_all_tables(self):
        """Haalt alle data op en vult de schermen en comboboxes."""
        studenten = self.model.get_all_students()
        transports = self.model.get_all_transports()
        logs = self.model.get_all_logs()

        self.view.populate_tree(self.view.tree_students, studenten)
        self.view.populate_tree(self.view.tree_trans, transports)
        self.view.populate_tree(self.view.tree_logs, logs)

        # Vul de dropdown menu's (Comboboxes) op de Logs-pagina
        self.view.combo_student['values'] = [f"{s[0]} - {s[1]}" for s in studenten]
        self.view.combo_vervoer['values'] = [f"{t[0]} - {t[1]}" for t in transports]

    # --- Studenten ---
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

    # --- Vervoer ---
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

    # --- Logs ---
    def add_log(self):
        student_val = self.view.combo_student.get()
        vervoer_val = self.view.combo_vervoer.get()
        datum = self.view.entry_datum.get()

        if not student_val or not vervoer_val or not datum:
            return self.view.show_error("Vul alle log-velden in!")

        # Haal de ID's uit de string (bv "1 - Jan Peeters" -> 1)
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