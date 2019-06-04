#!/usr/bin/env bash

set -e

for f in $(seq 25) ; do
	~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.$f -a -d -o full-$f
done
for f in $(seq 25) ; do
	~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.cross.$f -a -d -o full-$(( 25 + $f ))
done

# These anchors had HW issues, drop them from the dataset
rm full-*.24 full-*.2e full-*.28

./proc2.py

