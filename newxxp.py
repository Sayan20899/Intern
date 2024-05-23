import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json


class FactoryAgent:
    def __init__(self, factory_data, process_data):
        self.factory_data = factory_data
        self.process_data = process_data

    def get_factory_details(self):
        return "FactoryPi"


class CellAgent:
    def __init__(self, cell_id, process_data):
        self.cell_id = cell_id
        self.process_data = process_data

    def get_families_for_cell(self):
        families = []
        manufacturing_process = self.process_data.get("Manufacturing Process", {})
        for family, cells in manufacturing_process.items():
            if self.cell_id in cells:
                families.append(family)
        return families


class ResourceAgent:
    def __init__(self, resource_id, cell_id, resource_data):
        self.resource_id = resource_id
        self.cell_id = cell_id
        self.resource_data = resource_data

    def get_resource_details(self):
        return {
            "Resource ID": self.resource_id,
            "Cell ID": self.cell_id,
            "Name": self.resource_data['name'],
            "Setup Times": self.resource_data['setup_time'],
            "Processing Times": self.resource_data['processing_time'],
        }


class FactoryGUI:
    def __init__(self, root, factory_data, process_data):
        self.root = root
        self.factory_data = factory_data
        self.process_data = process_data
        self.factory_agent = FactoryAgent(factory_data, process_data)
        self.cell_agents = self.create_cell_agents(factory_data, process_data)
        self.resource_agents = self.create_resource_agents(factory_data)

        # Factory Selector
        self.factory_label = ttk.Label(root, text="Select Factory:")
        self.factory_label.grid(row=0, column=0)
        self.factory_combobox = ttk.Combobox(root, values=["FactoryPi"])
        self.factory_combobox.grid(row=0, column=1)
        self.factory_combobox.current(0)

        # Process Selector
        self.process_label = ttk.Label(root, text="Select Process:")
        self.process_label.grid(row=1, column=0)
        self.process_combobox = ttk.Combobox(root, values=["P_FFS_5F3C"])
        self.process_combobox.grid(row=1, column=1)
        self.process_combobox.current(0)

        # Next Button
        self.next_button = ttk.Button(root, text="Next", command=self.show_agent_data)
        self.next_button.grid(row=2, column=0, columnspan=2)

    def create_cell_agents(self, factory_data, process_data):
        factory_details = factory_data.get("FactoryPi", {})
        cell_agents = []
        for cell in factory_details.get("Cells", []):
            cell_agents.append(CellAgent(cell["CID"], process_data))
        return cell_agents

    def create_resource_agents(self, factory_data):
        factory_details = factory_data.get("FactoryPi", {})
        resource_agents = []
        for cell in factory_details.get("Cells", []):
            for resource in cell.get("Resources", []):
                resource_agents.append(ResourceAgent(resource['rid'], cell['CID'], resource))
        return resource_agents

    def show_agent_data(self):
        factory_details = self.factory_agent.get_factory_details()
        agent_data = f"Factory Agent: {factory_details}\n\n"

        manufacturing_process = self.process_data.get("Manufacturing Process", {})
        for cell_agent in self.cell_agents:
            cell_id = cell_agent.cell_id
            families = cell_agent.get_families_for_cell()

            for family in families:
                family_resources = []
                for resource in self.factory_data["FactoryPi"]["Cells"][cell_id - 1]["Resources"]:
                    resource_id = resource["rid"]
                    name = resource["name"]
                    setup_time = resource["setup_time"][int(family[-1]) - 1]
                    processing_time = resource["processing_time"][int(family[-1]) - 1]
                    family_resources.append(f"R{resource_id} [Name: {name}, Setup Time: {setup_time}, Processing Time: {processing_time}]")

                agent_data += f"Cell Agent (Cell ID: {cell_id}), Family: {family}:\n"
                agent_data += "\n".join(family_resources) + "\n\n"

        agent_window = tk.Toplevel(self.root)
        agent_window.title("Agent Data")
        
        agent_text = tk.Text(agent_window, wrap="word", width=80, height=20)
        agent_text.pack(side="left", fill="both", expand=True)

    
        scrollbar = ttk.Scrollbar(agent_window, orient="vertical", command=agent_text.yview)
        scrollbar.pack(side="right", fill="y")

   
        agent_text.configure(yscrollcommand=scrollbar.set)
    
   
        agent_text.insert("1.0", agent_data)


        #agent_label = ttk.Label(agent_window, text=agent_data)
        #agent_label.pack()


def load_json_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print("Failed to fetch JSON data from GitHub. Status code:", response.status_code)
        return None


# Load JSON data from GitHub
factory_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/factory_pi.json"
process_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/process.json"
factory_json_data = load_json_from_github(factory_json_url)
process_json_data = load_json_from_github(process_json_url)

if factory_json_data and process_json_data:
    root = tk.Tk()
    root.title("Factory GUI")
    factory_gui = FactoryGUI(root, factory_json_data, process_json_data)
    root.mainloop()