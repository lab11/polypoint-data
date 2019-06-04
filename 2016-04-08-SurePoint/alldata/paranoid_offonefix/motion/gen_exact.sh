#!/usr/bin/env bash

set -e

for i in $(seq 3 9); do
	~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.4 -t -e $i -o out.4.exact$i
	pushd ../
	./process.py out.4.exact$i
	popd
done
