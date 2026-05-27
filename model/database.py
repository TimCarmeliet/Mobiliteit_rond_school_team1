import sqlite3
from contextlib import contextmanager

class DatabaseModel:
    def __init__(self, db_path='mobiliteit.db'):
        self.db_path = db_path
        # Zorg dat alle uitbreidingen direct klaarstaan bij het opstarten
        self.setup_co2_uitbreiding()
        self.setup_aanwezigheden_uitbreiding()

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

    # =========================================================================
    # UITBREIDING 1: CO2 NORMEN
    # =========================================================================
    def setup_co2_uitbreiding(self):
        """Maakt de nieuwe CO2 tabel aan en vult de basisdata."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS CO2_Normen (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                transport_type TEXT UNIQUE,
                                co2_per_km REAL)''')
            
            standaard_normen = [("fiets", 0), ("bus", 50), ("auto", 120), ("te voet", 0)]
            for norm in standaard_normen:
                cursor.execute("INSERT OR IGNORE INTO CO2_Normen (transport_type, co2_per_km) VALUES (?, ?)", norm)

    def get_co2_normen(self):
        """Haalt de CO2 normen op uit de nieuwe tabel."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT transport_type, co2_per_km FROM CO2_Normen")
            return cursor.fetchall()

    # =========================================================================
    # UITBREIDING 2: AANWEZIGHEDEN EN AFWEZIGHEDEN (CRUD)
    # =========================================================================
    def setup_aanwezigheden_uitbreiding(self):
        """Maakt de nieuwe Aanwezigheden tabel aan conform de restricties."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS Aanwezigheden (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                student_id INTEGER NOT NULL,
                                datum TEXT NOT NULL,
                                status TEXT NOT NULL CHECK(status IN ('Aanwezig', 'Afwezig', 'Te laat')),
                                FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE)''')

    def add_aanwezigheid(self, student_id, datum, status):
        """Slaat een nieuwe aanwezigheid of afwezigheid op via de contextmanager."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO Aanwezigheden (student_id, datum, status) 
                VALUES (?, ?, ?)
            """, (student_id, datum, status))

    def get_all_aanwezigheden(self):
        """Haalt alle registraties op gekoppeld aan ID en Naam voor de interface."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT a.id, s.id || ' - ' || s.naam, a.datum, a.status 
                FROM Aanwezigheden a
                JOIN Students s ON a.student_id = s.id
                ORDER BY a.datum DESC, s.naam ASC
            """)
            return cursor.fetchall()

    def delete_aanwezigheid(self, aanw_id):
        """Verwijdert een specifieke aanwezigheidsregistratie."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Aanwezigheden WHERE id = ?", (aanw_id,))

    # =========================================================================
    # ANALYTISCHE QUERIES VOOR DE GRAFIEKEN
    # =========================================================================
    def query_afwezigheden_per_klas(self):
        """Analyse 1: Telt het aantal 'Afwezig' registraties per klas."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT s.klas, COUNT(a.id) as aantal_afwezig
                FROM Students s
                JOIN Aanwezigheden a ON s.id = a.student_id
                WHERE a.status = 'Afwezig'
                GROUP BY s.klas
                ORDER BY s.klas ASC
            """)
            return cursor.fetchall()

    def query_percentage_aanwezig_per_klas(self):
        """Analyse 2: Berekent de procentuele aanwezigheidsscore per klas."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT s.klas, 
                       ROUND(COUNT(CASE WHEN a.status = 'Aanwezig' THEN 1 END) * 100.0 / COUNT(a.id), 1)
                FROM Students s
                JOIN Aanwezigheden a ON s.id = a.student_id
                GROUP BY s.klas
                ORDER BY s.klas ASC
            """)
            return cursor.fetchall()

    def query_vervoer_vs_aanwezigheid(self):
        """Analyse 3: Combineert de verplaatsingslogs met de aanwezigheid op dezelfde dag."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT t.type, a.status, COUNT(a.id) as aantal
                FROM Aanwezigheden a
                JOIN Students s ON a.student_id = s.id
                JOIN Mobility_log m ON m.student_id = s.id AND m.datum = a.datum
                JOIN Transport t ON m.transport_id = t.id
                GROUP BY t.type, a.status
                ORDER BY t.type ASC, a.status ASC
            """)
            return cursor.fetchall()

    # =========================================================================
    # BESTAANDE CRUD METHODEN (STUDENTS, TRANSPORT, LOGS)
    # =========================================================================
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