import tkinter as tk
from tkinter import filedialog, messagebox
import json
import csv
import threading
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
import requests
from flask import Flask, request, jsonify

# Set matplotlib backend to work with tkinter
matplotlib.use('TkAgg')

# IP addresses of Raspberry Pi cell agents
raspberry_pi_ips = {
    1: '192.168.15.85',
    2: '192.168.15.218',
    3: '192.168.15.86'
}

# Initialize Flask app
app = Flask(__name__)

# Job completion status tracking
job_completion_status = {}
job_queue = []
job_queue_lock = threading.Lock()

# Global variables to store data
factory_data = None
process_data = None
jobs = []

# Job processing information for each resource
resource_jobs = {}

# Event to signal the completion of job processing
processing_done_event = threading.Event()

# Dictionary to keep track of the last end time for each job
job_end_times = {}

# GUI elements
class JobProcessingGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Processing Dashboard")

        # Load factory data button
        self.load_factory_button = tk.Button(master, text="Load Factory Data", command=self.load_factory_data)
        self.load_factory_button.pack(pady=10)

        # Load process data button
        self.load_process_button = tk.Button(master, text="Load Process Data", command=self.load_process_data)
        self.load_process_button.pack(pady=10)

        # Load jobs data button
        self.load_jobs_button = tk.Button(master, text="Load Jobs Data", command=self.load_jobs_data)
        self.load_jobs_button.pack(pady=10)

        # Start job processing button
        self.start_button = tk.Button(master, text="Start Job Processing", command=self.start_job_processing,
                                      state=tk.DISABLED)
        self.start_button.pack(pady=10)

        # Gantt chart button
        self.gantt_button = tk.Button(master, text="View Gantt Chart", command=self.generate_gantt_chart,
                                      state=tk.DISABLED)
        self.gantt_button.pack(pady=10)

        # Gantt chart figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.gantt_canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.gantt_canvas.get_tk_widget().pack()

    def load_factory_data(self):
        filename = filedialog.askopenfilename(title="Select Factory Data JSON File",
                                              filetypes=[("JSON Files", "*.json")])
        if not filename:
            messagebox.showwarning("Warning", "No file selected.")
            return

        try:
            with open(filename, 'r') as file:
                global factory_data
                factory_data = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load factory data:\n{str(e)}")
            return

        messagebox.showinfo("Success", "Factory data loaded successfully.")

    def load_process_data(self):
        filename = filedialog.askopenfilename(title="Select Process Data JSON File",
                                              filetypes=[("JSON Files", "*.json")])
        if not filename:
            messagebox.showwarning("Warning", "No file selected.")
            return

        try:
            with open(filename, 'r') as file:
                global process_data
                process_data = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load process data:\n{str(e)}")
            return

        messagebox.showinfo("Success", "Process data loaded successfully.")

    def load_jobs_data(self):
        filename = filedialog.askopenfilename(title="Select Jobs Data CSV File", filetypes=[("CSV Files", "*.csv")])
        if not filename:
            messagebox.showwarning("Warning", "No file selected.")
            return

        try:
            jobs_data = []
            with open(filename, 'r') as file:
                csv_reader = csv.reader(file, delimiter=';')
                for row in csv_reader:
                    job = {
                        "arrival_time": int(row[0]),
                        "job_id": int(row[1]),
                        "family_type": int(row[2]),
                        "priority": int(row[3])
                    }
                    jobs_data.append(job)

            global jobs
            jobs = jobs_data
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load jobs data:\n{str(e)}")
            return

        messagebox.showinfo("Success", "Jobs data loaded successfully.")
        self.start_button.config(state=tk.NORMAL)
        self.generate_gantt_chart()

    def start_job_processing(self):
        threading.Thread(target=self.process_jobs).start()
        self.start_button.config(state=tk.DISABLED)

    def process_jobs(self):
        assign_jobs_to_cells()
        processing_done_event.set()
        self.master.after(0, self.enable_gantt_button)

    def enable_gantt_button(self):
        self.gantt_button.config(state=tk.NORMAL)

    def generate_gantt_chart(self):
        global resource_jobs
        self.ax.clear()

        colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFCC99", "#FF6666"]
        resource_labels = {}
        y_pos = 0

        for rid, jobs in sorted(resource_jobs.items()):
            resource_labels[rid] = y_pos
            for i, job in enumerate(jobs):
                # Plot the setup time in gray if it's not the first job and family type is different from previous job
                if i > 0 and jobs[i - 1]['family_type'] != job['family_type'] and job['setup_time'] > 0:
                    self.ax.barh(y_pos, job['setup_time'], left=job['start_time'] - job['setup_time'],
                                 color='gray', edgecolor='black')
                # Plot the processing time in the corresponding family color
                self.ax.barh(y_pos, job['finish_time'] - job['start_time'], left=job['start_time'],
                             color=colors[job['family_type'] - 1], edgecolor='black')
                self.ax.text(job['start_time'] + (job['finish_time'] - job['start_time']) / 2, y_pos,
                             f"Job {job['job_id']}", va='center', ha='center', color='black')
            y_pos += 1

        # Set labels and grid
        self.ax.set_yticks(list(resource_labels.values()))
        self.ax.set_yticklabels([f"Resource {rid}" for rid in resource_labels.keys()])
        self.ax.set_xlabel("Time")
        self.ax.set_title("Gantt Chart for Job Scheduling in Factory")
        self.ax.grid(True)

        # Add legend outside the plot
        patches = [mpatches.Patch(color=colors[i], label=f'Family {i + 1}') for i in range(len(colors))]
        patches.append(mpatches.Patch(color='gray', label='Setup Time'))
        self.ax.legend(handles=patches, loc='upper center', bbox_to_anchor=(1.15, 1), borderaxespad=0.)

        plt.tight_layout()

        # Draw canvas
        self.gantt_canvas.draw()

    def run_gui(self):
        self.master.mainloop()


# Job assignment and processing functions
def assign_jobs_to_cells():
    sorted_jobs = sorted(jobs, key=lambda x: x['arrival_time'])

    for job in sorted_jobs:
        job_queue_lock.acquire()
        job_queue.append(job)
        job_queue_lock.release()

    process_job_queue()


def process_job_queue():
    while True:
        job_queue_lock.acquire()
        if not job_queue:
            job_queue_lock.release()
            time.sleep(1)
            continue
        job = job_queue.pop(0)
        job_queue_lock.release()

        process_single_job(job)

        if not job_queue:
            break


def process_single_job(job):
    global job_end_times  # Ensure we use the global job_end_times dictionary
    family_type = job['family_type'] - 1  # Adjusting index for 0-based indexing

    # Initialize the last end time for the job if it doesn't exist
    if job['job_id'] not in job_end_times:
        job_end_times[job['job_id']] = job['arrival_time']

    for cell in process_data["Manufacturing Process"][str(job['family_type'])]:
        resources = factory_data["FactoryPi"]["Cells"][cell - 1]["Resources"]

        min_time = float('inf')
        selected_resource = None

        for resource in resources:
            total_time = resource["setup_time"][family_type] + resource["processing_time"][family_type]
            if total_time < min_time:
                min_time = total_time
                selected_resource = resource

        if selected_resource:
            if selected_resource["rid"] in resource_jobs:
                last_job = resource_jobs[selected_resource["rid"]][-1]
                if last_job['family_type'] != job['family_type']:
                    start_time = max(last_job['finish_time'], job_end_times[job['job_id']]) + selected_resource["setup_time"][family_type]
                else:
                    start_time = max(last_job['finish_time'], job_end_times[job['job_id']])
                finish_time = start_time + selected_resource["processing_time"][family_type]
            else:
                start_time = job_end_times[job['job_id']]
                finish_time = start_time + selected_resource["processing_time"][family_type]

            job_info = {
                "job_id": job["job_id"],
                "family_type": job["family_type"],
                "start_time": start_time,
                "finish_time": finish_time,
                "setup_time": selected_resource["setup_time"][family_type]
            }

            # Update the end time of the job
            job_end_times[job['job_id']] = finish_time

            if selected_resource["rid"] in resource_jobs:
                resource_jobs[selected_resource["rid"]].append(job_info)
            else:
                resource_jobs[selected_resource["rid"]] = [job_info]

            cell_ip = raspberry_pi_ips[cell]
            url = f"http://{cell_ip}:5000/process_job"
            payload = {
                "job": job,
                "selected_resource": {
                    "rid": selected_resource["rid"],
                    "name": selected_resource["name"],
                    "start_time": job_info["start_time"],
                    "finish_time": job_info["finish_time"],
                    "setup_time": selected_resource["setup_time"][family_type]
                },
                "main_script_ip": '192.168.15.75'
            }

            print(f"Sending job to cell {cell}: {payload}")
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send job {job['job_id']} to cell {cell}")
            else:
                while not job_completed(job["job_id"]):
                    if time.time() > job_info['finish_time'] + 60:
                        print(f"Job {job['job_id']} timed out on cell {cell}")
                        break
                    time.sleep(1)

def job_completed(job_id):
    return job_completion_status.get(job_id, False)


# Flask route for job completion
@app.route('/job_complete', methods=['POST'])
def job_complete_route():
    data = request.json
    job_id = data['job_id']
    status = data['status']

    if status == 'complete':
        job_completion_status[job_id] = True

    return jsonify({"status": "acknowledged"}), 200


def run_flask_server():
    app.run(host='0.0.0.0', port=5000, debug=False)


def main():
    root = tk.Tk()
    gui = JobProcessingGUI(root)
    threading.Thread(target=run_flask_server).start()
    gui.run_gui()


if __name__ == '__main__':
    main()
