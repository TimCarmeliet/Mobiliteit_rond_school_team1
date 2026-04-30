import sqlite3
import csv
import os

# Pad naar de database (komt in de hoofdmap terecht als je dit script vanuit de hoofdmap runt)
DB_PATH = 'mobiliteit.db'
DATA_DIR = 'data'

def create_tables(cursor):
    """Maakt de verplichte tabellen aan."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT NOT NULL,
            klas TEXT NOT NULL,
            afstand REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mobility_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            transport_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Students(id),
            FOREIGN KEY (transport_id) REFERENCES Transport(id)
        )
    ''')

def import_csv_to_table(cursor, filename, table_name, insert_query):
    """Leest een CSV bestand in en voegt de data toe aan de opgegeven tabel."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Let op: Bestand {filename} niet gevonden in {DATA_DIR}/")
        return

    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader) # Sla de header-rij over
        for row in reader:
            cursor.execute(insert_query, row)
    print(f"Data uit {filename} succesvol geïmporteerd in '{table_name}'.")

def insert_team_data(cursor):
    """Voegt de testgegevens van het projectteam toe."""
    # VUL HIER JULLIE EIGEN GEGEVENS IN
    team_leden = [
        ("Test Student 1", "6ADB", 4.5),
        ("Test Student 2", "6ADB", 12.0),
        ("Test Student 3", "6ADB", 2.5)
    ]
    
    for lid in team_leden:
        cursor.execute('INSERT INTO Students (naam, klas, afstand) VALUES (?, ?, ?)', lid)
    
    print("Testgegevens van het projectteam zijn toegevoegd.")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_tables(cursor)

    # Importeer de CSV bestanden. Pas de bestandsnamen aan indien ze anders heten op Smartschool.
    import_csv_to_table(cursor, 'Students.csv', 'Students', 'INSERT INTO Students (id, naam, klas, afstand) VALUES (?, ?, ?, ?)')
    import_csv_to_table(cursor, 'Transports.csv', 'Transport', 'INSERT INTO Transport (id, type) VALUES (?, ?)')
    import_csv_to_table(cursor, 'Mobility_logs.csv', 'Mobility_log', 'INSERT INTO Mobility_log (id, student_id, transport_id, datum) VALUES (?, ?, ?, ?)')

    insert_team_data(cursor)

    conn.commit()
    conn.close()
    print("Database succesvol opgezet en gevuld!")

if __name__ == '__main__':
    # Zorg dat je dit script runt vanuit de hoofdmap van je project, 
    # zodat de databank 'mobiliteit.db' in de hoofdmap wordt aangemaakt.
    main()