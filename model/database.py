"""
model/database.py — De Model-laag (Data Access Layer).

Dit bestand is de ENIGE plek in het hele project die rechtstreeks met de
SQLite-databank communiceert. Geen enkel ander bestand importeert 'sqlite3'.

Waarom is dat belangrijk?
  → Als we morgen besluiten om van SQLite naar PostgreSQL te wisselen,
    hoeven we ALLEEN dit bestand aan te passen. De rest van het project
    merkt daar niets van, want de Controller roept dezelfde methoden aan
    (get_all_students, add_student, ...) ongeacht de onderliggende technologie.

De klasse DatabaseModel biedt een schone CRUD-interface:
  C = Create  → add_student(), add_transport(), add_log()
  R = Read    → get_all_students(), get_all_transports(), get_all_logs()
  U = Update  → update_student()
  D = Delete  → delete_student(), delete_transport(), delete_log()
"""

import sqlite3
from contextlib import contextmanager

class DatabaseModel:
    """
    Het hart van de Model-laag.

    Deze klasse beheert de volledige levenscyclus van databaseverbindingen
    en biedt een veilige, herbruikbare interface voor alle SQL-operaties.

    Elke publieke methode (zonder underscore) is een operatie die de
    Controller mag aanroepen. Private methoden (_connect, _get_cursor)
    zijn interne hulpmiddelen.
    """

    def __init__(self, db_path='mobiliteit.db'):
        self.db_path = db_path

    def _connect(self):
        """Opent een NIEUWE verbinding naar de SQLite-databank.
        
        We houden bewust geen permanente verbinding open, omdat SQLite
        een 'file-level lock' gebruikt — een open connectie kan andere
        schrijfoperaties blokkeren.
        """
        return sqlite3.connect(self.db_path)

    @contextmanager
    def _get_cursor(self, commit=False):
        """Context manager die een veilige cursor levert met automatische opruiming.

        Hoe werkt dit?
        ─────────────────────────────────────────────────
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO ...")
        ─────────────────────────────────────────────────

        Achter de schermen gebeurt het volgende:
        1. Een nieuwe verbinding wordt geopend (_connect).
        2. Een cursor wordt aangemaakt en teruggegeven via 'yield'.
        3. Als commit=True, worden wijzigingen opgeslagen (conn.commit).
        4. In de 'finally'-blok wordt de verbinding ALTIJD gesloten —
           zelfs als er een fout optreedt. Dit voorkomt datalekken.

        Door @contextmanager van de contextlib-module te gebruiken,
        vermijden we het handmatig schrijven van een __enter__/__exit__ klasse.
        """
        conn = self._connect()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            conn.close()

    # =========================================================================
    # UITBREIDING: CO2 Normen
    # Deze tabel werd later toegevoegd aan het project om de milieu-impact
    # van verschillende vervoersmiddelen te berekenen.
    # =========================================================================
    # --- UITBREIDING CO2 ---
    def setup_co2_uitbreiding(self):
        """Maakt de nieuwe CO2 tabel aan (bestaande tabellen blijven ongewijzigd) en vult basisdata.
        
        We gebruiken 'CREATE TABLE IF NOT EXISTS' zodat deze methode
        veilig herhaaldelijk kan worden aangeroepen zonder fouten.
        
        INSERT OR IGNORE voorkomt dubbele rijen als de data al eerder
        is ingevoegd — idempotent ontwerp.
        """
        with self._get_cursor(commit=True) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS CO2_Normen (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                transport_type TEXT UNIQUE,
                                co2_per_km REAL)''')
            
            # Standaard CO2-uitstoot in gram per kilometer:
            # Fiets en te voet = 0g (geen uitstoot)
            # Bus = 50g/km (gedeeld vervoer, relatief efficiënt)
            # Auto = 120g/km (individueel vervoer, hoogste uitstoot)
            # Voeg de standaard uitstoot toe (gebruik IGNORE om dubbele data te voorkomen als het al bestaat)
            standaard_normen = [("fiets", 0), ("bus", 50), ("auto", 120), ("te voet", 0)]
            for norm in standaard_normen:
                cursor.execute("INSERT OR IGNORE INTO CO2_Normen (transport_type, co2_per_km) VALUES (?, ?)", norm)

    def get_co2_normen(self):
        """Haalt de CO2 normen op uit de nieuwe tabel.
        
        Retourneert een lijst van tuples: [('fiets', 0.0), ('bus', 50.0), ...]
        De Controller zal deze omzetten naar een dictionary voor snelle lookups.
        """
        with self._get_cursor() as cursor:
            cursor.execute("SELECT transport_type, co2_per_km FROM CO2_Normen")
            return cursor.fetchall()

    # =========================================================================
    # CRUD voor Students
    # Elke methode volgt hetzelfde patroon:
    #   1. Open een cursor via de context manager
    #   2. Voer de SQL-query uit met parameterized queries (?)
    #   3. Retourneer het resultaat (bij leesoperaties)
    #
    # Parameterized queries (de vraagtekens ?) beschermen tegen
    # SQL-injectie: kwaadaardige invoer wordt automatisch ge-escaped.
    # =========================================================================
    # --- CRUD voor Students ---
    def get_all_students(self):
        """Haalt ALLE studenten op als lijst van tuples: [(id, naam, klas, afstand), ...]"""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, naam, klas, afstand FROM Students")
            return cursor.fetchall()

    def add_student(self, naam, klas, afstand):
        """Voegt een nieuwe student toe aan de Students-tabel."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Students (naam, klas, afstand) VALUES (?, ?, ?)", (naam, klas, afstand))

    def update_student(self, student_id, naam, klas, afstand):
        """Wijzigt een bestaande student op basis van het unieke ID."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("UPDATE Students SET naam = ?, klas = ?, afstand = ? WHERE id = ?", (naam, klas, afstand, student_id))

    def delete_student(self, student_id):
        """Verwijdert een student EN alle bijbehorende ritten uit Mobility_log.
        
        We verwijderen eerst de gerelateerde logs om referentiële integriteit
        te bewaren — anders zouden er 'wees-rijen' achterblijven in de log-tabel
        die verwijzen naar een niet-bestaande student.
        """
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))

    # =========================================================================
    # CRUD voor Transport
    # Zelfde patroon als Students. Bij verwijdering worden ook hier
    # alle gekoppelde log-rijen eerst opgeruimd.
    # =========================================================================
    # --- CRUD voor Transport ---
    def get_all_transports(self):
        """Haalt alle vervoersmiddelen op als lijst van tuples: [(id, type), ...]"""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, type FROM Transport")
            return cursor.fetchall()

    def add_transport(self, transport_type):
        """Voegt een nieuw vervoersmiddel toe (bijv. 'step', 'skateboard')."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Transport (type) VALUES (?)", (transport_type,))

    def delete_transport(self, transport_id):
        """Verwijdert een vervoersmiddel en alle bijbehorende log-rijen."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE transport_id = ?", (transport_id,))
            cursor.execute("DELETE FROM Transport WHERE id = ?", (transport_id,))

    # =========================================================================
    # CRUD voor Mobility_log
    # De log-tabel is de kern van het project: elke rij is één verplaatsing
    # van één student op één datum met één vervoersmiddel.
    # =========================================================================
    # --- CRUD voor Mobility_log ---
    def get_all_logs(self):
        """Haalt alle verplaatsingsregistraties op: [(id, student_id, transport_id, datum), ...]"""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, student_id, transport_id, datum FROM Mobility_log")
            return cursor.fetchall()

    def add_log(self, student_id, transport_id, datum):
        """Registreert een nieuwe verplaatsing: welke student, welk vervoer, welke datum."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO Mobility_log (student_id, transport_id, datum) VALUES (?, ?, ?)", (student_id, transport_id, datum))

    def delete_log(self, log_id):
        """Verwijdert één specifieke verplaatsingsregistratie."""
        with self._get_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Mobility_log WHERE id = ?", (log_id,))

    # =========================================================================
    # UITBREIDING 3: Action Logging
    # Deze tabel slaat een audit-trail op van alle gebruikersacties in de
    # applicatie. Elke keer dat een gebruiker een CRUD-operatie uitvoert
    # (of inlogt), wordt dit geregistreerd met een tijdstempel.
    # =========================================================================
    def setup_logging_table(self):
        """Maakt de Action_Logs tabel aan als die nog niet bestaat.
        
        Kolommen:
          id           — unieke primaire sleutel (auto-increment)
          user_id      — de naam/ID van de ingelogde gebruiker
          action_type  — het type actie (bijv. 'login', 'create', 'update', 'delete')
          timestamp    — datum en tijdstip van de actie (ISO 8601 formaat)
        """
        with self._get_cursor(commit=True) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS Action_Logs (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id TEXT NOT NULL,
                                action_type TEXT NOT NULL,
                                timestamp TEXT NOT NULL)''')

    def add_action_log(self, user_id, action_type, timestamp):
        """Registreert een nieuwe gebruikersactie in de Action_Logs tabel.
        
        Parameters:
          user_id     — wie voerde de actie uit (bijv. 'Jan')
          action_type — wat werd er gedaan (bijv. 'create', 'delete', 'login')
          timestamp   — wanneer (bijv. '2025-06-04 09:15:23')
        """
        with self._get_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO Action_Logs (user_id, action_type, timestamp) VALUES (?, ?, ?)",
                (user_id, action_type, timestamp)
            )

    def get_all_action_logs(self):
        """Haalt alle geregistreerde acties op, gesorteerd van nieuwste naar oudste.
        
        Retourneert: [(id, user_id, action_type, timestamp), ...]
        """
        with self._get_cursor() as cursor:
            cursor.execute("SELECT id, user_id, action_type, timestamp FROM Action_Logs ORDER BY id DESC")
            return cursor.fetchall()