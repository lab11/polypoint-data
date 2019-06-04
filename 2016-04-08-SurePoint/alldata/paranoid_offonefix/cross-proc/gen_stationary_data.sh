#!/usr/bin/env bash

set -e

for i in $(seq 25); do
	~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.$i -t -o stationary_data-$i.txt
done

for i in $(seq 25); do
	~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.cross.$i -t -o stationary_data-2-$i.txt
done
