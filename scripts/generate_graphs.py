import csv
import glob
import os
from datetime import datetime

import matplotlib.pyplot as plt


os.makedirs("results/graphs", exist_ok=True)


# ------------------------------------------------
# GRAPH 1:
# Average response time vs request rate
# ------------------------------------------------

replica_data = {1: [], 2: [], 3: []}

for filename in glob.glob("results/fixed-replicas/*_summary.csv"):

    with open(filename, newline="") as f:

        rows = list(csv.DictReader(f))

        if not rows:
            continue

        row = rows[0]

        replicas = int(row["replicas"])
        rate = int(row["request_rate"])
        average = float(row["average_response_time_ms"])

        replica_data[replicas].append((rate, average))


plt.figure()

for replicas, values in replica_data.items():

    values.sort()

    if values:
        rates = [v[0] for v in values]
        response_times = [v[1] for v in values]

        plt.plot(
            rates,
            response_times,
            marker="o",
            label=f"{replicas} replicas"
        )

plt.xlabel("Request rate (requests/second)")
plt.ylabel("Average response time (ms)")
plt.title("Average Response Time vs Request Rate")
plt.legend()
plt.grid(True)

plt.savefig(
    "results/graphs/graph1_response_time.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ------------------------------------------------
# GRAPH 2:
# CPU utilization for 3 replicas at 100 req/s
# ------------------------------------------------

filename = "results/replicas_3_rate_100_pod_metrics.csv"

if os.path.exists(filename):
    pod_data = {}

    with open(filename, newline="") as f:
        for row in csv.DictReader(f):
            pod = row["pod_name"]
            timestamp = row["timestamp"]
            cpu = float(row["cpu_utilization_percent"])
            # Make sure you append (timestamp, cpu) to pod_data[pod] here!

    # Process each pod's values AFTER reading the file
    for pod, values in pod_data.items():
        start_time = datetime.fromisoformat(
            values[0][0].replace("Z", "+00:00")
        )

        times = [
            (
                datetime.fromisoformat(t.replace("Z", "+00:00"))
                - start_time
            ).total_seconds()
            for t, _ in values
        ]

        cpu_values = [v[1] for v in values]


    with open(filename, newline="") as f:

        for row in csv.DictReader(f):

            pod = row["pod_name"]

            timestamp = row["timestamp"]
            cpu = float(row["cpu_utilization_percent"])

            pod_data.setdefault(pod, []).append((timestamp, cpu))

    plt.figure()

    for pod, values in pod_data.items():

        values.sort()

        times = list(range(len(values)))
        cpu_values = [v[1] for v in values]

        plt.plot(
            times,
            cpu_values,
            marker="o",
            label=pod
        )

    plt.xlabel("Time since start (seconds)")
    plt.ylabel("CPU utilization (% of CPU request)")
    plt.title("Pod CPU Utilization - 3 Replicas, 100 req/s")
    plt.legend()
    plt.grid(True)

    plt.savefig(
        "results/graphs/graph2_pod_cpu.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

else:
    print("Missing file:", filename)


# ------------------------------------------------
# GRAPH 3:
# Autoscaling test: request rate, CPU and replicas
# ------------------------------------------------

filename = "results/autoscaling/hpa_metrics.csv"

if os.path.exists(filename):

    elapsed = []
    request_rate = []
    cpu = []
    replicas = []

    with open(filename, newline="") as f:

        for row in csv.DictReader(f):

            elapsed.append(float(row["elapsed_seconds"]))
            request_rate.append(float(row["request_rate"]))

            cpu_value = row["average_cpu_utilization_percent"]
            replica_value = row["current_replicas"]

            cpu.append(
                float(cpu_value) if cpu_value else None
            )

            replicas.append(
                float(replica_value) if replica_value else None
            )

    fig, axes = plt.subplots(
        3,
        1,
        sharex=True,
        figsize=(11, 9)
    )

    axes[0].plot(elapsed, request_rate, marker="o")
    axes[0].set_ylabel("Request rate")
    axes[0].set_title("Autoscaling Experiment - 10 Minutes")
    axes[0].grid(True)

    axes[1].plot(elapsed, cpu, marker="o")
    axes[1].set_ylabel("Average CPU (%)")
    axes[1].grid(True)

    axes[2].plot(elapsed, replicas, marker="o")
    axes[2].set_ylabel("Web replicas")
    axes[2].set_xlabel("Elapsed time (seconds)")
    axes[2].grid(True)

    plt.tight_layout()

    plt.savefig(
        "results/graphs/graph3_autoscaling.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

else:
    print("Missing file:", filename)


print("Graph generation completed.")
print("Check results/graphs/")
