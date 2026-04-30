import sqlite3
from contextlib import contextmanager

class DatabaseModel:
    def __init__(self, db_path='mobiliteit.db'):
        self.db_path = db_path

    def _connect(self):
        """Maakt een connectie met de database."""
        return sqlite3.connect(self.db_path)

    @contextmanager
    def _get_cursor(self, commit=False):
        """Beheert de database connectie, geeft een cursor terug, en sluit netjes af."""
        conn = self._connect()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            conn.close()

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
            cursor.execute("DELETE FROM Mobility_log WHERE student_id = ?", (student_id,)) # Bewaak consistentie
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
            cursor.execute("DELETE FROM Mobility_log WHERE transport_id = ?", (transport_id,)) # Bewaak consistentie
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