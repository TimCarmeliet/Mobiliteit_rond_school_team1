import sqlite3
from contextlib import contextmanager

class DatabaseModel:
    def __init__(self, db_path='mobiliteit.db'):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    @contextmanager
    def _get_cursor(self, commit=False):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            conn.close()

    # --- UITBREIDING CO2 ---
    def setup_co2_uitbreiding(self):
        """Maakt de nieuwe CO2 tabel aan (bestaande tabellen blijven ongewijzigd) en vult basisdata."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS CO2_Normen (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                transport_type TEXT UNIQUE,
                                co2_per_km REAL)''')
            
            # Voeg de standaard uitstoot toe (gebruik IGNORE om dubbele data te voorkomen als het al bestaat)
            standaard_normen = [("fiets", 0), ("bus", 50), ("auto", 120), ("te voet", 0)]
            for norm in standaard_normen:
                cursor.execute("INSERT OR IGNORE INTO CO2_Normen (transport_type, co2_per_km) VALUES (?, ?)", norm)

    def get_co2_normen(self):
        """Haalt de CO2 normen op uit de nieuwe tabel."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT transport_type, co2_per_km FROM CO2_Normen")
            return cursor.fetchall()

    # --- CRUD voor Students ---
    def get_all_students(self):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, naam, klas, afstand FROM Students")
            return cursor.fetchall()

    def add_student(self, naam, klas, afstand):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Students (naam, klas, afstand) VALUES (?, ?, ?)", (naam, klas, afstand))

    def update_student(self, student_id, naam, klas, afstand):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("UPDATE Students SET naam = ?, klas = ?, afstand = ? WHERE id = ?", (naam, klas, afstand, student_id))

    def delete_student(self, student_id):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))

    # --- CRUD voor Transport ---
    def get_all_transports(self):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, type FROM Transport")
            return cursor.fetchall()

    def add_transport(self, transport_type):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Transport (type) VALUES (?)", (transport_type,))

    def delete_transport(self, transport_id):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE transport_id = ?", (transport_id,))
            cursor.execute("DELETE FROM Transport WHERE id = ?", (transport_id,))

    # --- CRUD voor Mobility_log ---
    def get_all_logs(self):
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, student_id, transport_id, datum FROM Mobility_log")
            return cursor.fetchall()

    def add_log(self, student_id, transport_id, datum):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Mobility_log (student_id, transport_id, datum) VALUES (?, ?, ?)", (student_id, transport_id, datum))

    def delete_log(self, log_id):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE id = ?", (log_id,))