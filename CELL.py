from Resource import Resource  # Import Resource class
desired_num_resources_per_cell = 2
class Cell:
  
    
  def __init__(self, cell_id):
    self.cell_id = cell_id
    self.resources = []  # List to store resources in the cell

  def add_resource(self, setup_values, process_values, **kwargs):

      if isinstance(setup_values, list) and isinstance(process_values, list):
    # Get the next resource ID based on the number of existing resources
        next_rid = len(self.resources)

    # Mapping for resource names based on CID (conditional logic)
        if self.cell_id == 1:
          resource_names = ["R1", "R2"]
        elif self.cell_id == 2:
          resource_names = ["R3", "R4"]
        elif self.cell_id == 3:
          resource_names = ["R5", "R6"]
        else:
          print(f"Error: No resource names defined for CID {self.cell_id}")
          return

    # Loop based on desired number and use CID mapping for names
        desired_num_resources = min(desired_num_resources_per_cell, len(resource_names))  # Limit by available names
        for i in range(desired_num_resources):
          resource_name = resource_names[i]
          resource = Resource(next_rid + i, setup_values, process_values, name=resource_name)
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


