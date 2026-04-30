import sqlite3

class DatabaseModel:
    def __init__(self, db_path='mobiliteit.db'):
        self.db_path = db_path

    def _connect(self):
        """Maakt een connectie met de database."""
        return sqlite3.connect(self.db_path)

    # --- CRUD voor Students ---
    def get_all_students(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, naam, klas, afstand FROM Students")
        records = cursor.fetchall()
        conn.close()
        return records

    def add_student(self, naam, klas, afstand):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Students (naam, klas, afstand) VALUES (?, ?, ?)", (naam, klas, afstand))
        conn.commit()
        conn.close()

    def update_student(self, student_id, naam, klas, afstand):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE Students SET naam = ?, klas = ?, afstand = ? WHERE id = ?", (naam, klas, afstand, student_id))
        conn.commit()
        conn.close()

    def delete_student(self, student_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Mobility_log WHERE student_id = ?", (student_id,)) # Bewaak consistentie
        cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()

    # --- CRUD voor Transport ---
    def get_all_transports(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type FROM Transport")
        records = cursor.fetchall()
        conn.close()
        return records

    def add_transport(self, transport_type):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Transport (type) VALUES (?)", (transport_type,))
        conn.commit()
        conn.close()

    def delete_transport(self, transport_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Mobility_log WHERE transport_id = ?", (transport_id,)) # Bewaak consistentie
        cursor.execute("DELETE FROM Transport WHERE id = ?", (transport_id,))
        conn.commit()
        conn.close()

    # --- CRUD voor Mobility_log ---
    def get_all_logs(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_id, transport_id, datum FROM Mobility_log")
        records = cursor.fetchall()
        conn.close()
        return records

    def add_log(self, student_id, transport_id, datum):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Mobility_log (student_id, transport_id, datum) VALUES (?, ?, ?)", (student_id, transport_id, datum))
        conn.commit()
        conn.close()

    def delete_log(self, log_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Mobility_log WHERE id = ?", (log_id,))
        conn.commit()
        conn.close()