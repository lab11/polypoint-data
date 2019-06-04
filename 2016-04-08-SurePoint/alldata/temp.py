#!/usr/bin/env python3

import sys
import numpy as np

import os

if not os.path.exists('out.{}.processed.data'.format(sys.argv[1])):
	sys.exit()

a = []
last_ts = None
last_pos = None
speeds = []
for l in open('out.{}.processed.data'.format(sys.argv[1])):
	ts = float(l.split()[0])
	pos = np.array(list(map(float, l.split()[4:7])))
	if last_ts is not None:
		diff = np.sqrt(sum( (pos-last_pos)**2 ))
		speed = diff / (ts - last_ts)
		speeds.append(speed)
	last_ts = ts
	last_pos = pos
	a.append(float(l.split()[-1]))

a = np.array(a)
s = np.array(speeds)

print('')
print(sys.argv[1])
print(np.median(a))
print(np.percentile(a, 90))
print(np.percentile(a, 95))
print('---')
print(np.median(s))
print(np.percentile(s, 90))
print(np.percentile(s, 99))
print(max(s))

