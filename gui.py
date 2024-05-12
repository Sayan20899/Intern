import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json






class FactoryGUI:
    def __init__(self, root, factory_data, process_data):
        self.root = root
        self.factory_data = factory_data
        self.process_data = process_data
        self.factory_agent = None

        # Factory Selector
        self.factory_label = ttk.Label(root, text="Select Factory:")
        self.factory_label.grid(row=0, column=0)
        self.factory_combobox = ttk.Combobox(root, values=list(factory_data.keys()))
        self.factory_combobox.grid(row=0, column=1)
        self.factory_combobox.bind("<<ComboboxSelected>>", self.update_cells)

        # Cell Selector
        self.cell_label = ttk.Label(root, text="Select Cell:")
        self.cell_label.grid(row=1, column=0)
        self.cell_combobox = ttk.Combobox(root)
        self.cell_combobox.grid(row=1, column=1)
        self.cell_combobox.bind("<<ComboboxSelected>>", self.update_resources)

        # Resource Selector
        self.resource_label = ttk.Label(root, text="Select Resource:")
        self.resource_label.grid(row=2, column=0)
        self.resource_combobox = ttk.Combobox(root)
        self.resource_combobox.grid(row=2, column=1)
        self.resource_combobox.bind("<<ComboboxSelected>>", self.update_times)

        # Family Selector
        self.family_label = ttk.Label(root, text="Select Family:")
        self.family_label.grid(row=3, column=0)
        self.family_combobox = ttk.Combobox(root)
        self.family_combobox.grid(row=3, column=1)
        self.family_combobox.bind("<<ComboboxSelected>>", self.display_family_steps)

        # Setup Time Input
        self.setup_time_label = ttk.Label(root, text="Setup Time:")
        self.setup_time_label.grid(row=4, column=0)
        self.setup_time_entry = ttk.Entry(root)
        self.setup_time_entry.grid(row=4, column=1)

        # Processing Time Input
        self.processing_time_label = ttk.Label(root, text="Processing Time:")
        self.processing_time_label.grid(row=5, column=0)
        self.processing_time_entry = ttk.Entry(root)
        self.processing_time_entry.grid(row=5, column=1)

        # Load families into Family Combobox
        self.load_families()

    def load_families(self):
        families = list(self.process_data["Manufacturing Process"].keys())
        self.family_combobox.config(values=families)

    def update_cells(self, event):
        factory = self.factory_combobox.get()
        cells = [str(cell["CID"]) for cell in self.factory_data[factory]["Cells"]]
        self.cell_combobox.config(values=cells)

    def update_resources(self, event):
        factory = self.factory_combobox.get()
        cell_id = int(self.cell_combobox.get())
        resources = [resource["name"] for cell in self.factory_data[factory]["Cells"] if cell["CID"] == cell_id for resource in cell["Resources"]]
        self.resource_combobox.config(values=resources)

    def update_times(self, event):
        factory = self.factory_combobox.get()
        cell_id = int(self.cell_combobox.get())
        resource_name = self.resource_combobox.get()
        for cell in self.factory_data[factory]["Cells"]:
            if cell["CID"] == cell_id:
                for resource in cell["Resources"]:
                    if resource["name"] == resource_name:
                        self.setup_time_entry.delete(0, tk.END)
                        self.setup_time_entry.insert(0, ", ".join(map(str, resource["setup_time"])))
                        self.processing_time_entry.delete(0, tk.END)
                        self.processing_time_entry.insert(0, ", ".join(map(str, resource["processing_time"])))

    def display_family_steps(self, event):
        selected_family = self.family_combobox.get()
        steps = self.process_data["Manufacturing Process"].get(selected_family, [])
        #messagebox.showinfo("Steps for Family", f"Family: {selected_family}\nSteps: {', '.join(map(str, steps))}")


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
