from Resource import Resource  # Import Resource class

class Cell:
  
    
  def __init__(self, cell_id):
    self.cell_id = cell_id
    self.resources = []  # List to store resources in the cell

  def add_resource(self, setup_values, process_values, **kwargs):
    
    if isinstance(setup_values, list) and isinstance(process_values, list):
      resource = Resource(len(self.resources) + 1, setup_values, process_values, **kwargs)  # Assign unique ID
      self.resources.append(resource)
    else:
      print(f"Error: Invalid setup or process values provided for cell {self.cell_id}")
      
  def to_dict(self):
        resource_info = []
        for resource in self.resources:
            resource_info.append(resource.__dict__)  # Leverage __dict__ for serialization
        return {
            "CID": self.cell_id,
            "Resources": resource_info
        }
    
  
  
  def __str__(self):
    resource_info = [str(resource) for resource in self.resources]
    return f"CID: {self.cell_id}, Resources: {resource_info}"


