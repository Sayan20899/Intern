import requests
import json
from collections import defaultdict
import pandas as pd
from io import StringIO

# Define the IP addresses of the Raspberry Pis as cell agents
cell_ips = ['192.168.166.85', '192.168.166.218', '192.168.166.86']

# Map the factory cells to Raspberry Pis
cell_to_pi = {
    1: '192.168.166.85',
    2: '192.168.166.218',
    3: '192.168.166.86'
}

# Map the resources to the Arduinos under each Raspberry Pi by unique identifier
cell_to_resources = {
    1: {'R1': 'R1', 'R2': 'R2'},
    2: {'R3': 'R3', 'R4': 'R4'},
    3: {'R5': 'R5', 'R6': 'R6'}
}

# Function to send commands to the Raspberry Pis
def send_command_to_device(ip, arduino_id, command):
    try:
        url = f"http://{ip}:5000/command"
        response = requests.post(url, json={'arduino_id': arduino_id, 'command': command})
        if response.status_code == 200:
            print(f"Command sent to {arduino_id} on {ip}: {command}")
        else:
            print(f"Failed to send command to {arduino_id} on {ip}: {response.status_code}")
    except Exception as e:
        print(f"Error sending command to {arduino_id} on {ip}: {e}")

# Function to schedule jobs and send commands to devices
def schedule_jobs(factory, process, batch):
    resource_jobs = defaultdict(list)
    resource_availability = defaultdict(lambda: 0)
    job_details = defaultdict(list)

    for job in sorted(batch.to_dict('records'), key=lambda x: x['arrival_time']):
        arrival_time = job['arrival_time']
        job_id = job['job_id']
        family_type = job['family_type'] - 1  # Adjusting index for 0-based indexing

        current_time = arrival_time
        family_type_str = str(job['family_type'])

        if family_type_str in process["Manufacturing Process"]:
            for cell in process["Manufacturing Process"][family_type_str]:
                min_time = float('inf')
                selected_resource = None

                for resource in factory["FactoryPi"]["Cells"][cell - 1]["Resources"]:
                    total_time = resource["setup_time"][family_type] + resource["processing_time"][family_type]
                    if total_time < min_time:
                        min_time = total_time
                        selected_resource = resource

                start_time = max(current_time, resource_availability[selected_resource["rid"]])
                finish_time = start_time + selected_resource["processing_time"][family_type]

                if resource_jobs[selected_resource["rid"]]:
                    last_job = resource_jobs[selected_resource["rid"]][-1]
                    if last_job['family_type'] != job['family_type']:
                        start_time += selected_resource["setup_time"][family_type]
                        finish_time = start_time + selected_resource["processing_time"][family_type]

                resource_availability[selected_resource["rid"]] = finish_time
                resource_jobs[selected_resource["rid"]].append({
                    "job_id": job_id,
                    "family_type": job['family_type'],
                    "start_time": start_time,
                    "finish_time": finish_time
                })

                job_details[job_id].append(f"Cell {cell} - Resource {selected_resource['name']} - Start: {start_time} - End: {finish_time}")

                pi_ip = cell_to_pi[cell]
                resource_name = selected_resource['name']
                arduino_id = cell_to_resources[cell][resource_name]
                processing_time = selected_resource["processing_time"][family_type]
                command = f"Start Job {job_id} - Family {job['family_type']} - Processing Time: {processing_time}"
                send_command_to_device(pi_ip, arduino_id, command)

                current_time = finish_time
        else:
            print(f"Family type {job['family_type']} not found in the manufacturing process.")

    print("\nJob Details:")
    for job_id, details in job_details.items():
        print(f"Job {job_id}:")
        for detail in details:
            print(f" {detail}")

    print("\nResource Allocation:")
    for rid, jobs in resource_jobs.items():
        print(f"Resource {rid}:")
        for job in jobs:
            print(f" Job {job['job_id']} (Family {job['family_type']}) from {job['start_time']} to {job['finish_time']}")

# Function to fetch and parse the JSON data from URLs
def fetch_and_parse_json(url):
    response = requests.get(url)
    return response.json()

# Function to fetch and convert CSV data from URL
def fetch_and_convert_csv(url):
    response = requests.get(url)
    csv_data = response.content.decode('utf-8')
    csv_buffer = StringIO(csv_data)
    df = pd.read_csv(csv_buffer, sep=';', header=None, names=[
                "arrival_time", "job_id", "family_type", "priority"
            ], usecols=range(4))
    return df

# URLs to the JSON and CSV data
factory_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/factory_pi.json"
process_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/process.json"
batch_data_url = "https://raw.githubusercontent.com/Sayan20899/OpenData4Manufacturing/master/OpenData4Manufacturing/Batches/10P5F_20T1U_2/A1.csv"

# Fetch and parse the data
factory_data = fetch_and_parse_json(factory_json_url)
process_data = fetch_and_parse_json(process_json_url)
batch_data = fetch_and_convert_csv(batch_data_url)

print("The Factory Data:", json.dumps(factory_data, indent=4))
print("\n\nThe Processing Data:", json.dumps(process_data, indent=4))
print("\n\nThe Batch To Be Processed:")
print(batch_data)

# Schedule jobs if data is available
if factory_data and process_data and batch_data is not None:
    schedule_jobs(factory_data, process_data, batch_data)
