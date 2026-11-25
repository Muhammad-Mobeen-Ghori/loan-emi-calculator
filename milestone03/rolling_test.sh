#!/bin/bash

URL="http://emi.local/api/emi"

TOTAL=0
SUCCESS=0
FAILED=0

echo "Starting continuous requests during rolling update..."
echo "Press Ctrl+C after the rolling update completes."
echo "-----------------------------------------------------"

while true
do
    TOTAL=$((TOTAL + 1))

    RESPONSE=$(curl -sS --http1.1 \
        -H "Connection: close" \
        -H "Content-Type: application/json" \
        -X POST "$URL" \
        -d '{"P":500000,"rate":12,"n":24}' \
        -w '\n%{http_code}' \
        --max-time 15)

    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "200" ]; then
        SUCCESS=$((SUCCESS + 1))
        POD=$(echo "$BODY" | jq -r '.servedBy')
        echo "Request $TOTAL: SUCCESS - Pod: $POD"
    else
        FAILED=$((FAILED + 1))
        echo "Request $TOTAL: FAILED - HTTP $HTTP_CODE"
    fi

    echo "Total: $TOTAL | Success: $SUCCESS | Failed: $FAILED"
    sleep 0.2
done
