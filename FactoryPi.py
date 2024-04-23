from Resource import Resource  
from CELL import Cell 
from Process import Process

class FactoryPi:
    def __init__(self, fid, cells, family):
        self.fid = fid
        self.cells = cells
        self.family = []
    
    
    def addFamily(self, cell: Cell):
        cell_ids = [cell.cell_id for cell in self.cells]
        self.family.append(cell_ids)
        print(" Family: " + str(self.family))
    
    
    def to_dict(self):
        cell_dicts = [cell.to_dict() for cell in self.cells]  
        return {
            "FactoryPi": {
                "FId": self.fid,
                "Cells": cell_dicts
            }
        }
    
    
    
    
    

    def __str__(self):
        cell_info = [str(cell) for cell in self.cells]
        return f"FactoryPi FID: {self.fid}, Cells: {cell_info}"
    
    
        
        
'''
cell5 = Cell(1)
cell = [cell5]

factorypi = FactoryPi(1,cell,family=[])
factorypi.addFamily(cell5)
factorypi.printfamily()
'''



def create_cells_and_resources():
    # Create cells and add resources directly in the Cell class
    cell1 = Cell(1)
    cell2 = Cell(2)
    cell3 = Cell(3)
    cell1.add_resource([5,4,3,8,7], [7,9,4,6,1])  # Example resource creation
    cell1.add_resource([7,10,5,6,7], [9,1,2,4,5])  # Example resource creation
    cell2.add_resource([6,4,3,8,7], [5,9,4,6,1])  # Example resource creation
    cell2.add_resource([8,9,4,6,1], [11,4,3,8,7])
    cell3.add_resource([7,10,5,6,7], [9,1,2,4,5])
    cell3.add_resource([7,10,3,2,7], [3,1,2,4,5])
    CELL = [cell1, cell2, cell3]
    return cell1, cell2, cell3, CELL


    

        
        

def main():
    cell1, cell2, cell3, cells = create_cells_and_resources()
    cells = [cell1, cell2, cell3]
      

    factory_pi = FactoryPi("F_5F3C6M" , cells, family=[])  # Create a FactoryPi instance with cells
    
    factory_pi.addFamily(cells)

    # Convert FactoryPi to JSON
    import json  # Import json module
    json_data = factory_pi.to_dict()
    json_string = json.dumps(json_data, indent=4)  # Add indentation for readability
    
    with open('factory_pi.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)
    
    print(json_string)


if __name__ == "__main__":
    main()
    
  
