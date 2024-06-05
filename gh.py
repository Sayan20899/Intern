import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import requests
from matplotlib.patches import Patch


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
        self.tcount = 0
        self.ct = len(batch_jobs)
        self.schedule = []

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
        self.next_button = ttk.Button(root, text="Next", command=self.run_hybrid_flowshop)
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

    def run_hybrid_flowshop(self):
        self.schedule_jobs()
        self.draw_gantt_chart()

    def schedule_jobs(self):
        self.tcount = 0
        current_time = 0
        job_completion = {}

        while self.ct > 0:
            print(f"Time count: {self.tcount}, Jobs left: {self.ct}")  # Debug print
    
            for job in self.batch_jobs:
                arrival_time, job_id, family_num, processing_time = job
                family = str(family_num)  # Convert family type from number to string
                if job_id not in job_completion and arrival_time <= self.tcount:
                    job_completion[job_id] = current_time
                    self.process_job(job_id, family, current_time,
                                     processing_time)  # Ensure family is treated as a string
                    self.ct -= 1

            self.tcount += 1
            current_time += 1  # Increment current time after each tcount

        print("Job Schedule:", self.schedule)  # Debug print

    # Print resources chosen for each family
        print("\nResources chosen for each family:")
        for task in self.schedule:
            _, family, cell_id, resource_id, _, _ = task
            print(f"Family {family}: Resource {resource_id} in Cell {cell_id}")

    # Print jobs assigned to each resource along with their family type
        print("\nJobs assigned to each resource along with their family type:")
        resource_jobs = {}
        for task in self.schedule:
            job_id, family, _, resource_id, _, _ = task
            if resource_id not in resource_jobs:
                resource_jobs[resource_id] = []
            resource_jobs[resource_id].append((job_id, family))

        for resource_id, jobs in resource_jobs.items():
            print(f"Resource {resource_id}:")
            for job, family in jobs:
                print(f"  Job {job} - Family {family}")


    def process_job(self, job_id, family, current_time, job_processing_time):
        manufacturing_process = self.process_data.get("Manufacturing Process", {})

    # Check if all the family keys exist in the manufacturing process data
        required_families = ["1", "2", "3", "4", "5"]
        if all(family_key in manufacturing_process for family_key in required_families):
        # If all the family keys exist, continue processing the job
            for cell_id in manufacturing_process[family]:
                cell = next((cell for cell in self.factory_data["FactoryPi"]["Cells"] if cell["CID"] == cell_id), None)
                if cell:
                    resources = cell["Resources"]
                    chosen_resource = None
                    min_processing_time = float('inf')

                    for resource in resources:
                        if resource["processing_time"][int(family) - 1] < min_processing_time:
                            min_processing_time = resource["processing_time"][int(family) - 1]
                            chosen_resource = resource

                    if chosen_resource:
                        setup_time = chosen_resource["setup_time"][int(family) - 1]
                        processing_time = chosen_resource["processing_time"][int(family) - 1]
                    
                    # Define start_time before conditionals
                        start_time = 0  

                    # Check if it's the first job assigned to this resource
                        if not any(task[3] == chosen_resource["rid"] for task in self.schedule):
                        # If it's the first job, ensure it starts at current time
                            start_time = current_time + setup_time
                        else:
                        # If not the first job, consider sequence and setup time
                            next_job_same_family = any(task[1] == family and task[3] == chosen_resource["rid"]
                                                   for task in self.schedule)
                            if not next_job_same_family:
                            # Find the end time of the previous job on this resource
                                previous_job_end_time = max(task[5] for task in self.schedule if task[3] == chosen_resource["rid"])
                                start_time = previous_job_end_time + setup_time
                            else:
                            # Find the end time of the previous job on this resource
                                previous_job_end_time = max(task[5] for task in self.schedule if task[3] == chosen_resource["rid"])
                                start_time = previous_job_end_time

                        end_time = start_time + processing_time
                    
                        self.schedule.append(
                            (job_id, str(family), cell_id, chosen_resource["rid"], start_time, end_time))
                        self.tcount = end_time  # Update tcount to track end time of current job
                        print(
                            f"Processed job {job_id} on resource {chosen_resource['rid']} of family {family} from {start_time} to {end_time}")  # Debug print
                    else:
                        print(f"No suitable resource found for job {job_id} of family {family}")
                else:
                    print(f"Cell {cell_id} not found.")
                    break  # Exit the loop if the cell is not found
        else:
            print(
                f"Not all required families found in manufacturing process. Unable to process job {job_id}.")



    def draw_gantt_chart(self):
        fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size as needed

        resource_labels = sorted(set(task[3] for task in self.schedule))  # Extract unique resource IDs and sort them

        # Define a dictionary to store colors for each job ID
        job_colors = {}
        color_index = 0  # Index to cycle through the colors

        for task in self.schedule:
            job_id, family, _, _, start_time, end_time = task
            if job_id not in job_colors:
                job_colors[job_id] = f'C{color_index}'  # Assign a new color to each job ID
                color_index += 1  # Increment the color index

            # Plot each task on the Gantt chart
            for i, resource_id in enumerate(resource_labels):
                if task[3] == resource_id:
                    ax.broken_barh([(start_time, end_time - start_time)], (i, 0.5),
                                   facecolors=(job_colors[job_id]), edgecolor='black', linewidth=1)

        ax.set_xlabel('Time', fontsize=12)  # Set x-axis label and font size
        ax.set_ylabel('Resource ID', fontsize=12)  # Set y-axis label and font size
        ax.set_yticks(range(len(resource_labels)))  # Set y-axis ticks to match resource IDs
        ax.set_yticklabels([f'Resource {resource_id}' for resource_id in resource_labels],
                           fontsize=10)  # Set y-axis tick labels to match resource IDs
        ax.grid(True, axis='y', linestyle='--', color='gray', alpha=0.5)  # Add gridlines on y-axis

        # Add legend for job colors
        legend_labels = [f'Job {job_id}' for job_id in job_colors.keys()]
        legend_handles = [Patch(facecolor=color, label=label) for label, color in
                          zip(legend_labels, job_colors.values())]
        ax.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

        # Set title
        ax.set_title('Gantt Chart for Job Schedule', fontsize=14)

        plt.tight_layout()  # Adjust layout to prevent overlapping labels
        plt.show()


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

if factory_json_data and process_json_data:
    root = tk.Tk()
    root.title("Factory GUI")
    factory_gui = FactoryGUI(root, factory_json_data, process_json_data, batch_jobs)
    root.mainloop()