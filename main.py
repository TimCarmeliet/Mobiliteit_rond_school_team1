"""
main.py — Het startpunt van de hele applicatie (Entry Point).

Dit bestand is de "dirigent" van ons project. Het brengt de drie lagen van
het MVC-patroon (Model-View-Controller) samen en start de applicatie.

MVC in een notendop:
  - Model:      De databanklaag — weet HOE data wordt opgeslagen en opgehaald.
  - View:       De visuele interface — weet HOE dingen eruitzien op het scherm.
  - Controller: De coördinator — de ENIGE plek waar bedrijfslogica leeft.
                Hij vertelt het Model wat te doen en de View wat te tonen.

Door deze scheiding kan elke laag onafhankelijk worden aangepast
zonder de andere lagen te breken.
"""

from model.database import DatabaseModel
from view.gui import MainView
from controller.controller import Controller

def main():
    # =========================================================================
    # STAP 1: Initialiseer het Model (de database)
    # We maken een DatabaseModel-object aan dat weet hoe het met onze
    # SQLite-databank 'mobiliteit.db' moet praten. Het Model bevat GEEN
    # kennis over de interface — het weet alleen van tabellen en queries.
    # Zorg dat je eerst utils/import_data.py hebt gedraaid zodat mobiliteit.db bestaat!
    # =========================================================================
    model = DatabaseModel('mobiliteit.db')
    
    # =========================================================================
    # STAP 2: Initialiseer de View (de Tkinter GUI)
    # MainView erft van tk.Tk — het IS het hoofdvenster van onze applicatie.
    # Op dit moment wordt het hele scherm opgebouwd: tabbladen, invoervelden,
    # tabellen en lege canvassen voor grafieken. Maar er zit nog geen data in!
    # =========================================================================
    view = MainView()
    
    # =========================================================================
    # STAP 3: Initialiseer de Controller en verbind Model en View
    # De Controller ontvangt BEIDE objecten. Hierdoor kan hij:
    #   - Data opvragen bij het Model  (self.model.get_all_students())
    #   - Die data doorsturen naar de View  (self.view.populate_tree(...))
    # Bij constructie roept de Controller meteen refresh_all_tables() aan,
    # waardoor alle schermen gevuld worden met actuele databasegegevens.
    # =========================================================================
    app_controller = Controller(model, view)
    
    # =========================================================================
    # STAP 4: Start de Tkinter event-loop
    # mainloop() is een oneindige lus die wacht op gebruikersacties
    # (klikken, typen, scrollen). Pas wanneer het venster wordt gesloten,
    # stopt deze lus en eindigt het programma.
    # =========================================================================
    app_controller.start()

if __name__ == "__main__":
    main()