import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

# Given data
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

# Initialize resource job list and availability tracker
resource_jobs = defaultdict(list)
resource_availability = defaultdict(lambda: 0)

# Process each job based on arrival time
for job in sorted(jobs, key=lambda x: x['arrival_time']):
    arrival_time = job['arrival_time']
    job_id = job['job_id']
    family_type = job['family_type'] - 1  # Adjusting index for 0-based indexing

    current_time = arrival_time

    # For each cell in the process for this family type
    for cell in process_data["Manufacturing Process"][str(job['family_type'])]:
        min_time = float('inf')
        selected_resource = None

        # Find the optimal resource in the cell
        for resource in factory_data["FactoryPi"]["Cells"][cell - 1]["Resources"]:
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

        # Update current time for the next cell
        current_time = finish_time

for rid, jobs in resource_jobs.items():
    print(f"Resource {rid}:")
    for job in jobs:
        print(f"  Job {job['job_id']} (Family {job['family_type']}) from {job['start_time']} to {job['finish_time']}")

# Prepare data for Gantt chart
fig, ax = plt.subplots(figsize=(12, 6))

colors = ["#FF9999", "#66B2FF", "#99FF99", "#FFCC99", "#FF6666"]
resource_labels = {}
y_pos = 0

for rid, jobs in sorted(resource_jobs.items()):
    resource_labels[rid] = y_pos
    for job in jobs:
        ax.barh(y_pos, job['finish_time'] - job['start_time'], left=job['start_time'],
                color=colors[job['family_type'] - 1], edgecolor='black')
        ax.text(job['start_time'] + (job['finish_time'] - job['start_time']) / 2, y_pos,
                f"Job {job['job_id']}", va='center', ha='center', color='black')
    y_pos += 1

# Set labels and grid
ax.set_yticks(list(resource_labels.values()))
ax.set_yticklabels([f"Resource {rid}" for rid in resource_labels.keys()])
ax.set_xlabel("Time")
ax.set_title("Gantt Chart for Job Scheduling in Factory")
ax.grid(True)

# Add legend outside the plot
patches = [mpatches.Patch(color=colors[i], label=f'Family {i + 1}') for i in range(len(colors))]
ax.legend(handles=patches, loc='upper center', bbox_to_anchor=(1.15, 1), borderaxespad=0.)

plt.tight_layout()
plt.show()
