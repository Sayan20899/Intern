from CELL import Cell
from FactoryPi import FactoryPi


class process:
    def __init__(self, fam):
        self.fam = []
    
    def add(self, fac: FactoryPi):
        self.fam.append(fac.family)
            

def getstring(factorypi_obj: FactoryPi):
    """
    Creates cells (if not already created), adds cell IDs to the 
    family list of the provided FactoryPi object, and prints the family.
    """
    if not factorypi_obj.cells:
        factorypi_obj.cells = factorypi_obj.create_cells_and_resources()  # Create cells if needed

    for cell in factorypi_obj.cells:
        factorypi_obj.addFamily(cell.cell_id)  # Access cell_id directly
        print(f"Family: {factorypi_obj.family}")  # Use f-string for cleaner formatting

# Create an instance of FactoryPi
factorypi = FactoryPi("F_5F3C6M", cells , family= [])

# Call getstring with the FactoryPi object
getstring(factorypi)
    
    
    

