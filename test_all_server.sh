#!/bin/bash

protocols=("tcp" "web")
packagings=("json" "msgpack" "pickle")

CONFIG="./config/config.yml"

for protocol in "${protocols[@]}"
do
  for packaging in "${packagings[@]}"
  do
    pid=$(lsof -t -i:9000)

    if [ -n "$pid" ]; then
        kill -9 $pid
    fi

    echo "======================================="
    echo "TEST: $protocol + $packaging"
    echo "======================================="

    sed -i "s/^protocol:.*/protocol: $protocol/" $CONFIG
    sed -i "s/^packaging_type:.*/packaging_type: $packaging/" $CONFIG

    python test_server.py

  done
done