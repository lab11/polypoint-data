#!/usr/bin/env bash

set -e

for i in "0" "r1" "r3" "r9"; do
	~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.4 -t -v $i -o out.4.nodiv.$i
	pushd ../
	./process.py out.4.nodiv.$i
	popd
done
