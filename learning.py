import json
import requests

# Job scheduling data (same as provided previously)
factory_data = {
    "FactoryPi": {
        "FId": "F_5F3C6M",
        "Cells": [
            {
                "CID": 1,
                "Resources": [
                    {
                        "rid": 1,
                        "name": "R1",
                        "setup_time": [10, 8, 6, 16, 14],
                        "processing_time": [20, 20, 15, 18, 17]
                    },
                    {
                        "rid": 2,
                        "name": "R2",
                        "setup_time": [14, 20, 10, 12, 14],
                        "processing_time": [27, 13, 16, 12, 15]
                    }
                ]
            },
            {
                "CID": 2,
                "Resources": [
                    {
                        "rid": 3,
                        "name": "R3",
                        "setup_time": [12, 18, 15, 16, 14],
                        "processing_time": [15, 27, 12, 18, 17]
                    },
                    {
                        "rid": 4,
                        "name": "R4",
                        "setup_time": [16, 18, 8, 12, 2],
                        "processing_time": [33, 12, 19, 24, 21]
                    }
                ]
            },
            {
                "CID": 3,
                "Resources": [
                    {
                        "rid": 5,
                        "name": "R5",
                        "setup_time": [14, 20, 10, 12, 14],
                        "processing_time": [27, 13, 16, 10, 15]
                    },
                    {
                        "rid": 6,
                        "name": "R6",
                        "setup_time": [14, 20, 6, 4, 14],
                        "processing_time": [19, 15, 14, 12, 13]
                    }
                ]
            }
        ]
    }
}

process_data = {
    "Process Name": "P_FFS_5F3C",
    "Manufacturing Process": {
        "1": [1, 2, 3],
        "2": [1, 2, 3],
        "3": [1, 2, 3],
        "4": [1, 2, 3],
        "5": [1, 2, 3]
    }
}

jobs = [
    {"arrival_time": 1, "job_id": 1, "family_type": 5, "priority": 10},
    {"arrival_time": 1, "job_id": 2, "family_type": 2, "priority": 2},
    {"arrival_time": 3, "job_id": 3, "family_type": 2, "priority": 9},
    {"arrival_time": 3, "job_id": 4, "family_type": 2, "priority": 4},
    {"arrival_time": 5, "job_id": 5, "family_type": 5, "priority": 10},
    {"arrival_time": 6, "job_id": 6, "family_type": 2, "priority": 9},
    {"arrival_time": 7, "job_id": 7, "family_type": 1, "priority": 8},
    {"arrival_time": 13, "job_id": 8, "family_type": 5, "priority": 1},
    {"arrival_time": 15, "job_id": 9, "family_type": 4, "priority": 8},
    {"arrival_time": 15, "job_id": 10, "family_type": 3, "priority": 3},
    {"arrival_time": 16, "job_id": 11, "family_type": 2, "priority": 2}
]

# Job processing information for each resource
resource_jobs = {}

# IP addresses of Raspberry Pi cell agents
raspberry_pi_ips = {
    1: '192.168.166.85',
    2: '192.168.166.218',
    3: '192.168.166.86'
}

# Assign jobs to cell agents
def assign_jobs_to_cells():
    for job in sorted(jobs, key=lambda x: x['arrival_time']):
        family_type = job['family_type'] - 1  # Adjusting index for 0-based indexing

        for cell in process_data["Manufacturing Process"][str(job['family_type'])]:
            # Get the resources associated with this cell
            resources = factory_data["FactoryPi"]["Cells"][cell - 1]["Resources"]

            # Select the optimal resource based on setup and processing times
            min_time = float('inf')
            selected_resource = None

            for resource in resources:
                total_time = resource["setup_time"][family_type] + resource["processing_time"][family_type]
                if total_time < min_time:
                    min_time = total_time
                    selected_resource = resource

            if selected_resource:
                # Check and adjust start and finish times based on last job family type
                if resource_jobs.get(selected_resource["rid"]):
                    last_job = resource_jobs[selected_resource["rid"]][-1]
                    if last_job['family_type'] != job['family_type']:
                        start_time = last_job['finish_time'] if 'finish_time' in last_job else job['arrival_time']
                        setup_time = selected_resource["setup_time"][family_type]
                        processing_time = selected_resource["processing_time"][family_type]
                        start_time += setup_time
                        finish_time = start_time + processing_time
                    else:
                        start_time = job['arrival_time']
                        finish_time = start_time + processing_time

                else:
                    start_time = job['arrival_time']
                    finish_time = start_time + selected_resource["processing_time"][family_type]

                # Store job information for the selected resource
                job_info = {
                    "job_id": job["job_id"],
                    "family_type": job["family_type"],
                    "start_time": start_time,
                    "finish_time": finish_time
                }

                if selected_resource["rid"] in resource_jobs:
                    resource_jobs[selected_resource["rid"]].append(job_info)
                else:
                    resource_jobs[selected_resource["rid"]] = [job_info]

                # Now selected_resource contains the optimal resource for this job and cell

                # Send job to corresponding Raspberry Pi cell agent
                cell_ip = raspberry_pi_ips[cell]
                url = f"http://{cell_ip}:5000/process_job"
                payload = {
                    "job": job,
                    "selected_resource": {
                        "rid": selected_resource["rid"],
                        "name": selected_resource["name"],
                        "setup_time": selected_resource["setup_time"][family_type],
                        "processing_time": selected_resource["processing_time"][family_type]
                    }
                }
                print("The Details:", payload)
                response = requests.post(url, json=payload)
                if response.status_code != 200:
                    print(f"Failed to send job {job['job_id']} to cell {cell}")

if __name__ == "__main__":
    assign_jobs_to_cells()
