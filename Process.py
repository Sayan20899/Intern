import json

class Process:
    def __init__(self):
        self.mprocess = []
        

    def add_cellid(self, cell_ids):
        self.mprocess.append(cell_ids)

    def represent(self):
        data = []  # Initialize an empty dictionary to hold the JSON data
        for i, family in enumerate(self.mprocess, start=1):  # Iterate over each family in self.family
            #json_data.append({f"Family {i}":family})  # Add the family data to the dictionary
            data.append(family)
        self.mprocess = data
        
        return data  # Return the JSON data as a dictionary

    

# Example usage
if __name__ == "__main__":
    process = Process()
    process.add_cellid([1, 2, 3]) # Family 1
    process.add_cellid([1, 2, 3])
    process.add_cellid([1, 2, 3])
    process.add_cellid([1, 2, 3])
    process.add_cellid([1, 2, 3])
    #process.add_family([2, 3])      # Family 2

    # Convert to JSON
    json_string = process.represent()
    manufacturing_process = {}
    for i, family_data in enumerate(json_string, start=1):
        manufacturing_process[f"Family{i}"] = family_data

    result = {
    "Manufacturing Process": manufacturing_process
    }
    json_output = json.dumps(result, indent='\n')
    
    with open('process.json', 'w') as outfile:
        json.dump(result, outfile, indent=4)
        
        
    print(json_output)
    #print(process.mprocess)
    #print(result)
    #print(json_string)
    # Reconstruct object from JSON
    #reconstructed_process = ManufacturingProcess.from_json(json_data)
    #print("\nReconstructed Manufacturing Process:")
    #for i, family in enumerate(reconstructed_process.family, start=1):
        #print(f"Family {i}:", family)



    
    
    

