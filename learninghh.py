import json
import requests
import threading
import time
from flask import Flask, request, jsonify

# Job scheduling data
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
    1: '192.168.249.86',
    2: '192.168.249.218',
    3: '192.168.249.85'
}

app = Flask(__name__)

job_completion_status = {job['job_id']: False for job in jobs}
job_queue = []
job_queue_lock = threading.Lock()

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

def process_single_job(job):
    family_type = job['family_type'] - 1  # Adjusting index for 0-based indexing

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
            if resource_jobs.get(selected_resource["rid"]):
                last_job = resource_jobs[selected_resource["rid"]][-1]
                if last_job['family_type'] != job['family_type']:
                    start_time = last_job['finish_time'] + selected_resource["setup_time"][family_type]
                else:
                    start_time = max(last_job['finish_time'], job['arrival_time'])
                finish_time = start_time + selected_resource["processing_time"][family_type]
            else:
                start_time = job['arrival_time']
                finish_time = start_time + selected_resource["processing_time"][family_type]

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
                "main_script_ip": '192.168.249.52'
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

@app.route('/job_complete', methods=['POST'])
def job_complete_route():
    data = request.json
    job_id = data['job_id']
    status = data['status']

    if status == 'complete':
        job_completion_status[job_id] = True

    return jsonify({"status": "acknowledged"}), 200

if __name__ == '__main__':
    threading.Thread(target=assign_jobs_to_cells).start()
    app.run(host='0.0.0.0', port=5000)
