import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json


class FactoryAgent:
    def __init__(self, factory_data):
        self.factory_data = factory_data

    def get_factory_details(self):
        return "FactoryPi"


class CellAgent:
    def __init__(self, factory_data):
        self.factory_data = factory_data

    def get_cells(self):
        factory_details = self.factory_data.get("FactoryPi", {})
        return [f"Cell{i + 1}" for i in range(len(factory_details.get("Cells", [])))]


class ResourceAgent:
    def __init__(self, factory_data):
        self.factory_data = factory_data

    def get_resources(self):
        factory_details = self.factory_data.get("FactoryPi", {})
        cells = factory_details.get("Cells", [])
        resources = []
        for i, cell in enumerate(cells, start=1):
            for j in range(1, 3):  # Assuming each cell has two resources
                resources.append(f"Resource {i * 2 - 2 + j}")
        return resources


class FactoryGUI:
    def __init__(self, root, factory_data):
        self.root = root
        self.factory_data = factory_data
        self.factory_agent = FactoryAgent(factory_data)
        self.cell_agent = CellAgent(factory_data)
        self.resource_agent = ResourceAgent(factory_data)

        # Factory Selector
        self.factory_label = ttk.Label(root, text="Select Factory:")
        self.factory_label.grid(row=0, column=0)
        self.factory_combobox = ttk.Combobox(root, values=["FactoryPi"])
        self.factory_combobox.grid(row=0, column=1)

        # Next Button
        self.next_button = ttk.Button(root, text="Next", command=self.show_agent_data)
        self.next_button.grid(row=1, column=0, columnspan=2)

    def show_agent_data(self):
        factory_details = self.factory_agent.get_factory_details()
        factory_cells = self.cell_agent.get_cells()
        resources = self.resource_agent.get_resources()

        agent_data = f"Factory Agent: {factory_details}\n\nCell Agent: {', '.join(factory_cells)}\n\nResource Agent: {', '.join(resources)}"

        agent_window = tk.Toplevel(self.root)
        agent_window.title("Agent Data")

        agent_label = ttk.Label(agent_window, text=agent_data)
        agent_label.pack()


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
factory_json_data = load_json_from_github(factory_json_url)

if factory_json_data:
    root = tk.Tk()
    root.title("Factory GUI")
    factory_gui = FactoryGUI(root, factory_json_data)
    root.mainloop()
