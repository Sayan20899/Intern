import requests
import json
from collections import defaultdict

class FactoryPi:
    def __init__(self, url):
        self.url = url

    def representation(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Failed to fetch Data:", response.status_code)
            return None

    def fetch_and_convert_csv(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            print("Failed to fetch data:", response.status_code)
            return None

        csv_data = response.text.strip().split('\n')
        jobs = []
        for line in csv_data:
            fields = line.rstrip(';').split(';')
            if len(fields) == 4:
                job = {
                    "arrival_time": int(fields[0]),
                    "job_id": int(fields[1]),
                    "family_type": int(fields[2]),
                    "priority": int(fields[3])
                }
                jobs.append(job)
            else:
                print("Skipping line due to unexpected number of fields:", fields)
        return jobs

factory_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/factory_pi.json"
process_json_url = "https://raw.githubusercontent.com/Sayan20899/Intern/main/process.json"
batch_data_url = "https://raw.githubusercontent.com/Sayan20899/OpenData4Manufacturing/master/OpenData4Manufacturing/Batches/10P5F_20T1U_2/A1.csv"

factory_data = FactoryPi(factory_json_url)
process_data = FactoryPi(process_json_url)
batch_data = FactoryPi(batch_data_url)

factory = factory_data.representation()
process = process_data.representation()
batch = batch_data.fetch_and_convert_csv()

print("The Factory Data:", json.dumps(factory, indent=4))
print("\n\nThe Processing Data:", json.dumps(process, indent=4))
print("\n\nThe Batch To Be Processed:")
for job in batch:
    print(job)

resource_jobs = defaultdict(list)
resource_availability = defaultdict(lambda: 0)
job_details = defaultdict(list)

# Process each job based on arrival time
for job in sorted(batch, key=lambda x: x['arrival_time']):
    arrival_time = job['arrival_time']
    job_id = job['job_id']
    family_type = job['family_type'] - 1  # Adjusting index for 0-based indexing

    current_time = arrival_time

    # Convert family_type to string to access the process dictionary
    family_type_str = str(job['family_type'])

    # Check if the family type exists in the process
    if family_type_str in process["Manufacturing Process"]:
        # For each cell in the process for this family type
        for cell in process["Manufacturing Process"][family_type_str]:
            min_time = float('inf')
            selected_resource = None

            # Find the optimal resource in the cell
            for resource in factory["FactoryPi"]["Cells"][cell - 1]["Resources"]:
                total_time = resource["setup_time"][family_type] + resource["processing_time"][family_type]
                if total_time < min_time:
                    min_time = total_time
                    selected_resource = resource

            # Update resource availability and track jobs assigned to resources
            start_time = max(current_time, resource_availability[selected_resource["rid"]])
            finish_time = start_time + selected_resource["processing_time"][family_type]

            # Check if the previous job in the resource list is of the same family type
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

            # Update current time for the next cell
            current_time = finish_time
    else:
        print(f"Family type {job['family_type']} not found in the manufacturing process.")

print("\nJob Details:")
for job_id, details in job_details.items():
    print(f"Job {job_id}:")
    for detail in details:
        print(f"  {detail}")

print("\nResource Allocation:")
for rid, jobs in resource_jobs.items():
    print(f"Resource {rid}:")
    for job in jobs:
        print(f"  Job {job['job_id']} (Family {job['family_type']}) from {job['start_time']} to {job['finish_time']}")














