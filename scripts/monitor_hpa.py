import argparse
import csv
import json
import subprocess
import time

from datetime import datetime, timezone


parser = argparse.ArgumentParser()

parser.add_argument("--duration", type=int, default=610)
parser.add_argument("--interval", type=int, default=15)
parser.add_argument("--output", required=True)

args = parser.parse_args()

start = time.monotonic()

with open(args.output, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "timestamp",
        "elapsed_seconds",
        "request_rate",
        "current_replicas",
        "desired_replicas",
        "average_cpu_utilization_percent"
    ])

    while time.monotonic() - start < args.duration:

        elapsed = time.monotonic() - start

        # Required 10-minute workload phases
        if elapsed < 120:
            request_rate = 10
        elif elapsed < 420:
            request_rate = 100
        else:
            request_rate = 10

        try:

            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "hpa",
                    "emi-web",
                    "-n",
                    "emi",
                    "-o",
                    "json"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            data = json.loads(result.stdout)

            current = data.get("status", {}).get(
                "currentReplicas", ""
            )

            desired = data.get("status", {}).get(
                "desiredReplicas", ""
            )

            cpu = ""

            metrics = data.get("status", {}).get(
                "currentMetrics", []
            )

            for metric in metrics:

                if metric.get("type") == "Resource":

                    resource = metric.get("resource", {})

                    if resource.get("name") == "cpu":

                        cpu = resource.get(
                            "current",
                            {}
                        ).get(
                            "averageUtilization",
                            ""
                        )

            timestamp = datetime.now(timezone.utc).isoformat()

            writer.writerow([
                timestamp,
                round(elapsed, 2),
                request_rate,
                current,
                desired,
                cpu
            ])

            f.flush()

            print(
                f"{elapsed:.0f}s | "
                f"Rate: {request_rate} | "
                f"Current: {current} | "
                f"Desired: {desired} | "
                f"CPU: {cpu}"
            )

        except Exception as exc:

            print("HPA monitoring error:", exc)

        time.sleep(args.interval)


print("HPA monitoring completed.")
print("Saved:", args.output)
