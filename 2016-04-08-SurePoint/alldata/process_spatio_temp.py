#!/usr/bin/env python3

import time
import sys
import pprint
import numpy as np
import math
import datetime
import csv
import os

from dateutil.parser import parse

MO = {}
ranges = {}
fix_GT = False
try:
	if ':' in sys.argv[1]:
		fix_GT = True
		POS = np.array(list(map(float, sys.argv[1].split(':'))))
	else:
		for l in open(sys.argv[1]):
			if l[0] == '#':
				continue
			MO[float(l.split()[0])] = np.array(list(map(float, l.split()[4:7])))

	for l in open(sys.argv[2]):
		if l[0] == '#':
			continue
		ranges[float(l.split()[0])] = np.array(list(map(float, l.split()[1:])))

	ANC = np.array(list(map(float, sys.argv[3].split(':'))))

	ofile = open(sys.argv[4], 'w')
except:
	print("ERR: arguments should be:")
	print("./script processed.data all_ranges.data x:y:z outfile")
	print("")
	raise


if fix_GT:
	GT = np.sqrt(sum( (ANC-POS)**2 ))
	for t in sorted(ranges):
		ofile.write(str(t) + '\t')
		for r in ranges[t]:
			ofile.write('{:.3f}\t'.format(r - GT))
		ofile.write('\n')
else:
	for t in sorted(MO):
		GT = np.sqrt(sum( (ANC-MO[t])**2 ))
		if t in ranges:
			ofile.write(str(t) + '\t')
			for r in ranges[t]:
				ofile.write('{:.3f}\t'.format(r - GT))
			ofile.write('\n')
		else:
			print(t)


