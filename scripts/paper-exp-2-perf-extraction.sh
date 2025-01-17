#!/usr/bin/env bash

# Extracts the perf data from gramine-perf-logs/paper-2-perf.data (created by paper-exp-2-profiling.py) and saves it as
# table in results/perf-before-opt.txt

for i in $(seq 0 9)
do
  perf report --no-children --no-call-graph -n -i gramine-perf-logs/paper-2-perf-$i.data --stdio >> results/perf-before-opt-$i.txt
done
