class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        self.view.set_controller(self)
        self.load_initial_data()

    def load_initial_data(self):
        """Laadt de data in bij het opstarten."""
        self.refresh_student_table()

    def refresh_student_table(self):
        """Haalt de studenten op uit de DB en toont ze in de tabel."""
        studenten = self.model.get_all_students()
        self.view.populate_student_tree(studenten)

    # --- Studenten CRUD Acties ---
    def add_student(self):
        data = self.view.get_student_form_data()
        
        # Validatie: Controleer of alle velden zijn ingevuld
        if not data['naam'] or not data['klas'] or not data['afstand']:
            self.view.show_error("Vul a.u.b. alle velden in!")
            return
        
        try:
            # Vervang eventueel een komma door een punt en zet om naar kommagetal
            afstand = float(data['afstand'].replace(',', '.'))
            
            # Opslaan in de database
            self.model.add_student(data['naam'], data['klas'], afstand)
            
            # View updaten
            self.view.clear_student_form()
            self.refresh_student_table()
            self.view.show_info(f"Student '{data['naam']}' is toegevoegd.")
        except ValueError:
            self.view.show_error("De afstand moet een geldig getal zijn.")

    def update_student(self):
        student_id = self.view.get_selected_student_id()
        if not student_id:
            self.view.show_error("Selecteer eerst een student uit de tabel om aan te passen.")
            return

        data = self.view.get_student_form_data()
        if not data['naam'] or not data['klas'] or not data['afstand']:
            self.view.show_error("Vul a.u.b. alle velden in!")
            return
        
        try:
            afstand = float(data['afstand'].replace(',', '.'))
            self.model.update_student(student_id, data['naam'], data['klas'], afstand)
            
            self.view.clear_student_form()
            self.refresh_student_table()
            self.view.show_info(f"Studentgegevens aangepast.")
        except ValueError:
            self.view.show_error("De afstand moet een geldig getal zijn.")

    def delete_student(self):
        student_id = self.view.get_selected_student_id()
        if not student_id:
            self.view.show_error("Selecteer eerst een student uit de tabel om te verwijderen.")
            return
        
        self.model.delete_student(student_id)
        self.view.clear_student_form()
        self.refresh_student_table()
        self.view.show_info("Student succesvol verwijderd. Alle bijbehorende logs zijn ook verwijderd om dataconsistentie te garanderen.")

    def start(self):
        self.view.mainloop()