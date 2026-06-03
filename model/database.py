import sqlite3
from contextlib import contextmanager

class DatabaseModel:
    def __init__(self, db_path='mobiliteit.db'):
        self.db_path = db_path
        # Zorg dat alle uitbreidingen direct klaarstaan bij het opstarten
        self.setup_co2_uitbreiding()
        self.setup_aanwezigheden_uitbreiding()
        self.setup_reistijd_uitbreiding()

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
        """Maakt de nieuwe aanwezigheden tabel aan conform de restricties."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS aanwezigheden (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                student_id INTEGER NOT NULL,
                                datum TEXT NOT NULL,
                                status TEXT NOT NULL CHECK(status IN ('aanwezig', 'afwezig', 'te laat')),
                                FOREIGN KEY (student_id) REFERENCES Students(id) ON DELETE CASCADE)''')

    def add_aanwezigheid(self, student_id, datum, status):
        """Slaat een nieuwe aanwezigheid of afwezigheid op via de contextmanager."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO aanwezigheden (student_id, datum, status) 
                VALUES (?, ?, ?)
            """, (student_id, datum, status.lower()))

    def get_all_aanwezigheden(self):
        """Haalt alle registraties op gekoppeld aan ID en Naam voor de interface."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT a.id, s.id || ' - ' || s.naam, a.datum, a.status 
                FROM aanwezigheden a
                JOIN Students s ON a.student_id = s.id
                ORDER BY a.datum DESC, s.naam ASC
            """)
            return cursor.fetchall()

    def delete_aanwezigheid(self, aanw_id):
        """Verwijdert een specifieke aanwezigheidsregistratie."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM aanwezigheden WHERE id = ?", (aanw_id,))

    # =========================================================================
    # UITBREIDING 3: REISTIJD ANALYSE SETUP & QUERIES
    # =========================================================================
    def setup_reistijd_uitbreiding(self):
        """Zorgt ervoor dat de tabel Mobility_log een kolom 'reistijd' heeft en berekent deze."""
        with self._get_cursor(commit=True) as cursor:
            try:
                # Voegt veilig de kolom reistijd toe als die er nog niet in zit
                cursor.execute("ALTER TABLE Mobility_log ADD COLUMN reistijd INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                # Kolom bestaat al, we hoeven niks te doen!
                pass
        
        # FIX: Bereken en vul direct de lege vakjes voor de ritten die er al in staan!
        self.reken_en_fix_bestaande_reistijden()

    def reken_en_fix_bestaande_reistijden(self):
        """Berekent met terugwerkende kracht de reistijd voor alle lege/0 records."""
        studenten = self.get_all_students()
        transports = self.get_all_transports()
        
        stud_afstand = {s[0]: float(s[3]) for s in studenten}
        trans_snelheid = {}
        snelheids_mapping = {'fiets': 15.0, 'bus': 30.0, 'auto': 45.0, 'te voet': 5.0}
        
        for t in transports:
            t_id = t[0]
            t_type = str(t[1]).lower().strip()
            trans_snelheid[t_id] = snelheids_mapping.get(t_type, 20.0) # 20 km/u als fallback
            
        with self._get_cursor(commit=True) as cursor:
            # Haal alle logs op waar de reistijd nog 0 of onbekend is
            cursor.execute("SELECT id, student_id, transport_id FROM Mobility_log WHERE reistijd = 0 OR reistijd IS NULL")
            logs_to_fix = cursor.fetchall()
            
            for log in logs_to_fix:
                log_id, s_id, t_id = log
                afstand = stud_afstand.get(s_id, 0.0)
                snelheid = trans_snelheid.get(t_id, 20.0)
                
                if snelheid > 0:
                    berekende_tijd = round((afstand / snelheid) * 60)
                else:
                    berekende_tijd = 0
                    
                cursor.execute("UPDATE Mobility_log SET reistijd = ? WHERE id = ?", (berekende_tijd, log_id))

    def query_reistijd_per_vervoer(self):
        """Analyseert en berekent de gemiddelde reistijd per vervoersmiddel."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT t.type, ROUND(AVG(m.reistijd), 1) as gem_reistijd
                FROM Mobility_log m
                JOIN Transport t ON m.transport_id = t.id
                GROUP BY t.type
                ORDER BY t.type ASC
            """)
            return cursor.fetchall()

    def query_reistijd_per_klas(self):
        """Analyseert en berekent de gemiddelde reistijd per klas."""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT s.klas, ROUND(AVG(m.reistijd), 1) as gem_reistijd
                FROM Mobility_log m
                JOIN Students s ON m.student_id = s.id
                GROUP BY s.klas
                ORDER BY s.klas ASC
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
            cursor.execute("SELECT id, student_id, transport_id, datum, reistijd FROM Mobility_log")
            return cursor.fetchall()

    def add_log(self, student_id, transport_id, datum, reistijd=0):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Mobility_log (student_id, transport_id, datum, reistijd) VALUES (?, ?, ?, ?)", (student_id, transport_id, datum, reistijd))

    def delete_log(self, log_id):
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE id = ?", (log_id,))