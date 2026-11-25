import argparse
import csv
import json
import random
import threading
import time
import urllib.request
import urllib.error

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone


parser = argparse.ArgumentParser()

parser.add_argument("--rate", type=int, required=True)
parser.add_argument("--duration", type=int, default=60)
parser.add_argument("--replicas", type=int, required=True)
parser.add_argument("--output", required=True)

args = parser.parse_args()

URL = "http://emi.local/api/emi"

TOTAL_REQUESTS = args.rate * args.duration

results = []
lock = threading.Lock()


def send_request(request_number, scheduled_time):

    principal = random.randint(100000, 2000000)
    rate = round(random.uniform(5.0, 20.0), 2)
    months = random.choice([12, 18, 24, 36, 48, 60, 72, 84, 120])

    payload = {
        "P": principal,
        "rate": rate,
        "n": months
    }

    data = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Connection": "close"
    }

    request = urllib.request.Request(
        URL,
        data=data,
        headers=headers,
        method="POST"
    )

    start = time.perf_counter()

    status = 0
    served_by = ""
    error = ""

    try:
        with urllib.request.urlopen(request, timeout=15) as response:

            status = response.status
            body = json.loads(response.read().decode("utf-8"))

            served_by = body.get("servedBy", "")

    except urllib.error.HTTPError as exc:
        status = exc.code
        error = str(exc)

    except Exception as exc:
        error = str(exc)

    latency = (time.perf_counter() - start) * 1000

    completed_time = datetime.now(timezone.utc).isoformat()

    row = {
        "request_number": request_number,
        "scheduled_time": scheduled_time,
        "completed_time": completed_time,
        "principal": principal,
        "rate": rate,
        "months": months,
        "http_status": status,
        "response_time_ms": round(latency, 3),
        "served_by": served_by,
        "success": status == 200,
        "error": error
    }

    with lock:
        results.append(row)


print("========================================")
print("LOAN EMI LOAD TEST")
print("========================================")
print("Ingress URL:", URL)
print("Replicas:", args.replicas)
print("Request rate:", args.rate, "requests/second")
print("Duration:", args.duration, "seconds")
print("Total scheduled requests:", TOTAL_REQUESTS)
print("========================================")


start_time = time.perf_counter()

with ThreadPoolExecutor(max_workers=300) as executor:

    futures = []

    for i in range(TOTAL_REQUESTS):

        target_time = start_time + (i / args.rate)

        wait_time = target_time - time.perf_counter()

        if wait_time > 0:
            time.sleep(wait_time)

        scheduled = datetime.now(timezone.utc).isoformat()

        futures.append(
            executor.submit(send_request, i + 1, scheduled)
        )

    for future in as_completed(futures):
        future.result()


elapsed = time.perf_counter() - start_time

results.sort(key=lambda x: x["request_number"])

successes = sum(1 for r in results if r["success"])
failures = len(results) - successes

latencies = [
    r["response_time_ms"]
    for r in results
    if r["success"]
]

average_latency = (
    sum(latencies) / len(latencies)
    if latencies else 0
)

output_file = args.output

with open(output_file, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "request_number",
            "scheduled_time",
            "completed_time",
            "principal",
            "rate",
            "months",
            "http_status",
            "response_time_ms",
            "served_by",
            "success",
            "error"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


summary_file = output_file.replace(".csv", "_summary.csv")

with open(summary_file, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "replicas",
        "request_rate",
        "duration_seconds",
        "scheduled_requests",
        "completed_requests",
        "successful_requests",
        "failed_requests",
        "average_response_time_ms",
        "actual_test_duration_seconds"
    ])

    writer.writerow([
        args.replicas,
        args.rate,
        args.duration,
        TOTAL_REQUESTS,
        len(results),
        successes,
        failures,
        round(average_latency, 3),
        round(elapsed, 3)
    ])


print("\n========== TEST SUMMARY ==========")
print("Scheduled requests:", TOTAL_REQUESTS)
print("Completed requests:", len(results))
print("Successful requests:", successes)
print("Failed requests:", failures)
print("Average response time:", round(average_latency, 3), "ms")
print("Actual duration:", round(elapsed, 2), "seconds")
print("Raw results:", output_file)
print("Summary:", summary_file)
print("==================================")
