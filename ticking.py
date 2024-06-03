import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import requests

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
    def __init__(self, root, factory_data, process_data, batch_jobs):
        self.root = root
        self.factory_data = factory_data
        self.process_data = process_data
        self.batch_jobs = batch_jobs
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
        self.next_button = ttk.Button(root, text="Next", command=self.run_fifo_flowshop)
        self.next_button.grid(row=2, column=0, columnspan=2)

        self.next_button = ttk.Button(root, text="Mapping", command=self.show_agent_data)
        self.next_button.grid(row=3, column=0, columnspan=2)

        self.next_button = ttk.Button(root, text="GANTT", command=self.draw_gantt_chart)
        self.next_button.grid(row=4, column=0, columnspan=2)

        self.next_button = ttk.Button(root, text="TEST", command=self.schedule_jobs)
        self.next_button.grid(row=5, column=0, columnspan=2)

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
                resource_agents.append(ResourceAgent(resource["rid"], cell["CID"], resource))
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
                    family_resources.append(
                        f"R{resource_id} [Name: {name}, Setup Time: {setup_time}, Processing Time: {processing_time}]")

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


    def schedule_jobs(self):

        family_processing_time = []
        family_setup_time = []
        for cell in self.cell_agents:
            cell_id = cell.cell_id
            family = cell.get_families_for_cell()



            for families in family:

                for resource in self.factory_data["FactoryPi"]["Cells"][cell_id - 1]["Resources"]:
                    name = resource["name"]
                    processing_time = resource["processing_time"][int(families[-1]) - 1]
                    setup_time = resource["setup_time"][int(families[-1]) - 1]
                    family_processing_time.append(f"Family: {families} [Name: {name}, Processing Time: {processing_time}]")
                    family_setup_time.append(f"Family: {families} [Name: {name}, Setup Time: {setup_time}]")

        print( "\n\n".join(family_processing_time))
        print( "\n\n".join(family_setup_time))












    def run_fifo_flowshop(self):
        # Output the sequence of jobs
        sequence_output = "Sequence of Jobs (FIFO Flowshop):\n"
        for job in self.batch_jobs:
            sequence_output += f"Job {job[1]}\n"

        # Calculate the makespan
        makespan = sum(job[0] for job in self.batch_jobs)
        sequence_output += f"\nMakespan: {makespan}"

        messagebox.showinfo("FIFO Flowshop Result", sequence_output)

    def draw_gantt_chart(self):
        sorted_jobs = sorted(self.batch_jobs, key=lambda x: x[0], reverse=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_title('Gantt Chart for Jobs')
        ax.set_xlabel('Time')
        ax.set_ylabel('Jobs')
        ax.grid(True)

        yticks = []
        yticklabels = []

        for i, job in enumerate(sorted_jobs):
            start_time = sum(job[0] for job in sorted_jobs[:i])
            ax.broken_barh([(start_time, job[0])], (i, 0.4), facecolors='blue')
            yticks.append(i + 0.2)
            yticklabels.append(f'Job {job[1]}')

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels)

        plt.show()


# Example batch jobs
batch_jobs = [
    (1, 1, 5, 10),
    (1, 2, 2, 2),
    (3, 3, 2, 9),
    (3, 4, 2, 4),
    (5, 5, 5, 10),
    (6, 6, 2, 9),
    (7, 7, 1, 8),
    (13, 8, 5, 1),
    (15, 9, 4, 8),
    (15, 10, 3, 3),
    (16, 11, 2, 2)
]



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
    factory_gui = FactoryGUI(root, factory_json_data, process_json_data, batch_jobs)
    root.mainloop()

