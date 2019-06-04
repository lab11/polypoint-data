#!/usr/bin/env python3

import numpy as np

ANCHORS = {
		'22': (  .212,  8.661, 4.047),
		'3f': ( 7.050,  0.064, 3.295),
		#'28': (12.704,  9.745, 3.695),
		'2c': ( 2.312,  0.052, 1.369),
		#'24': (11.649,  0.058, 0.333),
		'23': (12.704,  3.873, 2.398),
		#'2e': ( 8.822, 15.640, 3.910),
		'2b': ( 0.717,  3.870, 2.522),
		'26': (12.704, 15.277, 1.494),
		'30': (12.610,  9.768, 0.064),
		'27': ( 0.719,  3.864, 0.068),
		}


center = [7.102, 7.616, 1.877]

# We walked y first, then x
one_foot = 0.3048

for a in ANCHORS:
	print(a)
	for i in range(1,51):
		origin = list(center)
		if i > 25:
			origin[0] -= (-13 + int(i-25)) * one_foot
		else:
			origin[1] += (-13 + int(i)) * one_foot

		GT_RANGE = np.sqrt(sum( (np.array(origin) - np.array(ANCHORS[a]))**2 ))

		ofile = open('onept_{}.{}'.format(i, a), 'w')
		for l in open('full-{}.df.{}'.format(i, a)):
			if l.split()[0] == '#':
				continue
			for r in map(float, l.split()[1:]):
				ofile.write(str(r-GT_RANGE) + '\t')
			ofile.write('\n')

