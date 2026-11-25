import argparse
import csv
import os
import re
import subprocess
import time

from datetime import datetime, timezone

import psutil


parser = argparse.ArgumentParser()

parser.add_argument("--duration", type=int, default=60)
parser.add_argument("--label", required=True)

args = parser.parse_args()

duration = args.duration
label = args.label

os.makedirs("results", exist_ok=True)

host_file = f"results/{label}_host_cpu.csv"
pod_file = f"results/{label}_pod_metrics.csv"

print("Starting system profiling:", label)
print("Duration:", duration, "seconds")


# Host CPU CSV

with open(host_file, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "timestamp",
        "host_cpu_percent",
        "host_memory_percent"
    ])

    start = time.time()
    next_sample = start

    while time.time() - start < duration:

        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent

        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            cpu,
            memory
        ])

        f.flush()


# Pod CPU and memory CSV

with open(pod_file, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "timestamp",
        "pod_name",
        "cpu_millicores",
        "cpu_utilization_percent",
        "memory",
        "run_label"
    ])

    start = time.time()

    while time.time() - start < duration:

        timestamp = datetime.now(timezone.utc).isoformat()

        try:

            result = subprocess.run(
                ["kubectl", "top", "pods", "-n", "emi", "--no-headers"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:

                for line in result.stdout.strip().splitlines():

                    fields = line.split()

                    if len(fields) < 3:
                        continue

                    pod = fields[0]

                    # Only application pods
                    if not pod.startswith("emi-web-"):
                        continue

                    cpu_value = fields[1]
                    memory_value = fields[2]

                    if cpu_value.endswith("m"):
                        cpu_m = float(cpu_value[:-1])
                    else:
                        cpu_m = float(cpu_value) * 1000

                    # CPU request is 100m
                    cpu_percent = cpu_m / 100 * 100

                    writer.writerow([
                        timestamp,
                        pod,
                        round(cpu_m, 2),
                        round(cpu_percent, 2),
                        memory_value,
                        label
                    ])

                f.flush()

            else:
                print("kubectl top error:", result.stderr.strip())

        except Exception as exc:
            print("Profiling error:", exc)

        time.sleep(15)


print("Profiling completed.")
print("Host CPU file:", host_file)
print("Pod metrics file:", pod_file)
