#!/bin/bash

set -e

RATES=(10 25 50 100 200)
REPLICAS=(1 2 3)

mkdir -p results/fixed-replicas

for REPLICA in "${REPLICAS[@]}"
do

    echo "======================================"
    echo "SETTING WEB REPLICAS TO $REPLICA"
    echo "======================================"

    kubectl scale deployment emi-web \
        --replicas="$REPLICA" -n emi

    kubectl rollout status deployment/emi-web -n emi

    kubectl get pods -n emi -o wide

    for RATE in "${RATES[@]}"
    do

        LABEL="replicas_${REPLICA}_rate_${RATE}"

        echo
        echo "======================================"
        echo "RUN: $LABEL"
        echo "======================================"

        # Start profiling in background
        python3 scripts/profile_system.py \
            --duration 60 \
            --label "$LABEL" &

        PROFILE_PID=$!

        sleep 2

        # Start load test
        python3 scripts/load_test.py \
            --rate "$RATE" \
            --duration 60 \
            --replicas "$REPLICA" \
            --output "results/fixed-replicas/${LABEL}.csv"

        # Wait for profiling to finish
        wait "$PROFILE_PID"

        echo "Completed: $LABEL"

        sleep 10

    done

done

echo
echo "ALL 15 FIXED-REPLICA EXPERIMENTS COMPLETED."
