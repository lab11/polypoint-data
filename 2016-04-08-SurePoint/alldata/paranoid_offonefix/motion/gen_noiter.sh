#!/usr/bin/env bash

set -e

~/code/lab11/polypoint/software/firmware/data_dump_glossy.py -f out.raw.4 -t -n -o out.4.no_iter
pushd ../
./process.py out.4.no_iter
popd
