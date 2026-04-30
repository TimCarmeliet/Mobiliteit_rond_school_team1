from model.database import DatabaseModel
from view.gui import MainView
from controller.controller import Controller

def main():
    # 1. Initialiseer het Model (de database)
    # Zorg dat je eerst utils/import_data.py hebt gedraaid zodat mobiliteit.db bestaat!
    model = DatabaseModel('mobiliteit.db')
    
    # 2. Initialiseer de View (de Tkinter GUI)
    view = MainView()
    
    # 3. Initialiseer de Controller en verbind Model en View
    app_controller = Controller(model, view)
    
    # 4. Start de applicatie
    app_controller.start()

if __name__ == "__main__":
    main()