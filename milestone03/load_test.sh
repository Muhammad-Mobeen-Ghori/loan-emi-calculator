#!/bin/bash

URL="http://emi.local/api/emi"

echo "Starting 30 EMI requests..."
echo "--------------------------------"

for i in $(seq 1 30)
do
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
        POD=$(echo "$BODY" | jq -r '.servedBy')

        if [ "$POD" = "null" ] || [ -z "$POD" ]; then
            echo "Request $i: FAILED - servedBy missing"
        else
            echo "Request $i: SUCCESS - Served by $POD"
        fi
    else
        echo "Request $i: FAILED - HTTP $HTTP_CODE"
        echo "$BODY"
    fi
done
