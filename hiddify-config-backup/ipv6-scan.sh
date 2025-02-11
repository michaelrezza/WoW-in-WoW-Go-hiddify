#!/bin/bash

set -e  # Stop on error

echo "Starting IPv6 scan..." > ipv6-scan/ipv6_result.txt

# Retrieve the list of IPv6 addresses from WARP
warp-cli account | grep "2606:4700" > ipv6-scan/ipv6_list.txt

# Find the fastest IPv6 by measuring ping response time
best_ipv6=""
best_ping=9999

while IFS= read -r ip; do
    avg_ping=$(ping6 -c 3 -q "$ip" | awk -F'/' 'END{print ($4+0)}')
    if [[ ! -z "$avg_ping" ]] && (( $(echo "$avg_ping < $best_ping" | bc -l) )); then
        best_ping=$avg_ping
        best_ipv6=$ip
    fi
done < ipv6-scan/ipv6_list.txt

echo "Fastest IPv6: $best_ipv6 with Ping: $best_ping ms"
echo "$best_ipv6" > ipv6-scan/best_ipv6.txt