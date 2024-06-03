
TIME_UNIT = 3
STIME_UNIT = 2


class SetupTime:
    
    def __init__(self, setup_values):
        self.setup_values = [value * STIME_UNIT for value in setup_values]  # Apply time units
           

class ProcessingTime:
    

    def __init__(self, process_values):
        self.process_values = [value * TIME_UNIT for value in process_values]
     


    
    
    
    
class Resource:
   # Class variable to store all resources

  def __init__(self, rid, setup_values, process_values):
    self.rid = rid
    self.name = f"R{rid}"
    self.setup_time = SetupTime(setup_values).setup_values
    self.processing_time = ProcessingTime(process_values).process_values
    

   

  def __str__(self):
    return f"RID: {self.rid}, Name: {self.name}, Setup Time: {self.setup_time}, Processing Time: {self.processing_time}"


def Represent():
  Resource.resources.clear()

