import requests
import json


class FactoryPi:
    def __init__(self, url):
       self.url = url
        
    def representation(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            json_data = json.dumps(data, indent=4)
            return json_data
        else:
            print("Failed to fetch Data:", response.status_code )
            return None
        
factory_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/factory_pi.json"
process_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/process.json"

factory_data = FactoryPi(factory_json_url)
process_data = FactoryPi(process_json_url)
data = factory_data.representation()

process = process_data.representation()

print("The Factory Data:", data)

print("\n\nThe Processing Data:", process)






        
        
        