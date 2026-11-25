#!/bin/bash

set -e

mkdir -p results/autoscaling

echo "=========================================="
echo "STARTING 10-MINUTE AUTOSCALING EXPERIMENT"
echo "=========================================="

# Ensure HPA controls the Deployment
kubectl get hpa emi-web -n emi

# Start host and pod profiling for the full experiment
python3 scripts/profile_system.py \
    --duration 610 \
    --label autoscaling &

PROFILE_PID=$!

# Start HPA monitoring
python3 scripts/monitor_hpa.py \
    --duration 610 \
    --interval 15 \
    --output results/autoscaling/hpa_metrics.csv &

HPA_PID=$!

sleep 3

echo
echo "PHASE 1: 10 req/s for 120 seconds"

python3 scripts/load_test.py \
    --rate 10 \
    --duration 120 \
    --replicas 1 \
    --output results/autoscaling/phase1_10rps.csv

echo
echo "PHASE 2: 100 req/s for 300 seconds"

python3 scripts/load_test.py \
    --rate 100 \
    --duration 300 \
    --replicas 1 \
    --output results/autoscaling/phase2_100rps.csv

echo
echo "PHASE 3: 10 req/s for 180 seconds"

python3 scripts/load_test.py \
    --rate 10 \
    --duration 180 \
    --replicas 1 \
    --output results/autoscaling/phase3_10rps.csv

wait "$PROFILE_PID"
wait "$HPA_PID"

echo
echo "=========================================="
echo "AUTOSCALING EXPERIMENT COMPLETED"
echo "=========================================="
