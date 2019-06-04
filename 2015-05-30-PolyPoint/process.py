#!/usr/bin/env python3

#Conversion from mocap coordinate frame to PH coordinate frame:
# ph_coords = [-optitrack_coords(:,1)+7.308,-optitrack_coords(:,3)+3.048,optitrack_coords(:,2)+0.065];

import time
import sys
import pprint
import numpy as np
import math
import datetime
import csv

from dateutil.parser import parse

try:
	EXP = sys.argv[1]
except IndexError:
	print("ERR: Script requires one argument, experiment to process")
	print("     Try ./process first_flight")
	sys.exit(1)

#if EXP == 'quad':
#	print("quad: Correcting MO time by +15 hours\n\n")
#	TIME_FIX = 15
#	SEC_FIX = 0.55
#elif EXP == 'train':
#	print("train: Correcting MO time by -3 hours\n\n")
#	TIME_FIX = 3
#	SEC_FIX = 0.55
#elif EXP == 'time_offset':
#	TIME_FIX = 3
#	SEC_FIX = 0

TIME_FIX = 3
if EXP == 'first_flight':
	SEC_FIX = -54.0
if EXP == 'second_flight':
	SEC_FIX = -53.9

#with open('timestamps_anchor2_{}.txt'.format(EXP)) as f:
#	lines = f.readlines()
#
#	start_seq, start_ts = lines[0].split(' ', maxsplit=1)
#	end_seq, end_ts = lines[-1].split(' ', maxsplit=1)
#
#	start_seq = int(start_seq)
#	end_seq = int(end_seq)
#
#	start_dt = parse(start_ts)
#	end_dt = parse(end_ts)
#
#	pprint.pprint(start_dt)
#	print(start_dt)
#	print(repr(start_dt))
#	#help(start_dt)
#
#	start_ts = start_dt.timestamp()
#	end_ts = end_dt.timestamp()
#
#	print("PH Start Time: {}".format(datetime.datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S.%f')))
#	print("PH   End Time: {}".format(datetime.datetime.fromtimestamp(  end_ts).strftime('%Y-%m-%d %H:%M:%S.%f')))
#
#	PH_seq_time = np.linspace(start_ts, end_ts, end_seq-start_seq+1)

# [timestamp, (x,y,z)]
PH_data = []

with open('{}/log.txt'.format(EXP)) as ifile:
	for line in ifile:
		line = line.split()
		PH_data.append([
			float(line[0]),
			np.array(
				list(map(float, line[1:4]))
			)]
		)

print("PH Start Time: {}".format(datetime.datetime.fromtimestamp(PH_data [0][0]).strftime('%Y-%m-%d %H:%M:%S.%f')))
print("PH   End Time: {}".format(datetime.datetime.fromtimestamp(PH_data[-1][0]).strftime('%Y-%m-%d %H:%M:%S.%f')))

with open('optitrack/{}.csv'.format(EXP)) as f:
	l = f.readline()
	assert l.split(',')[8] == 'Capture Start Time'
	field = l.split(',')[9]
	field = field.replace('.', ':', 2)
	start, msec_ampm = field.split('.')
	msec, ampm = msec_ampm.split(' ')
	ts = start + ' ' + ampm
	#print(ts)
	dt = parse(ts)
	dt = dt + datetime.timedelta(hours=TIME_FIX, seconds=SEC_FIX)
	#print(dt)
	MO_start_ts = dt.timestamp()
	MO_start_ts += int(msec) / 1000

	l = f.readlines()[-1]
	off = float(l.split(',')[1])

	print("MO Start Time: {}".format(datetime.datetime.fromtimestamp(MO_start_ts).strftime('%Y-%m-%d %H:%M:%S.%f')))
	print("MO   End Time: {}".format(datetime.datetime.fromtimestamp(MO_start_ts+off).strftime('%Y-%m-%d %H:%M:%S.%f')))

print('')

# [time, (x, y, z)]
MO_data = []

# Frame,Time,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z,X,Y,Z


with open('optitrack/{}.csv'.format(EXP)) as csvfile:
	reader = csv.reader(csvfile)
	start = False
	OBJ_IDX = 0
	for row in reader:
		if row == []:
			continue
		if row[0] == '0':
			start = True
		if start:
			if EXP == 'first_flight' and int(row[0]) == 2180:
				# MoCap loses tracker and reacquires
				OBJ_IDX = 51
			try:
				MO_data.append([
					MO_start_ts + float(row[1]),
					np.array([
						-float(row[4+OBJ_IDX]) + 7.308,
						-float(row[2+OBJ_IDX]) + 3.045,
						 float(row[3+OBJ_IDX]) + 0.065
						 ])
					])
			except ValueError:
				if row[2+OBJ_IDX] == '':
					continue
				else:
					print(row)
					raise


print("PH Start: ", end="")
pprint.pprint(PH_data[:1])
print("MO Start: ", end="")
pprint.pprint(MO_data[:1])
print('')
print("PH   End: ", end="")
pprint.pprint(PH_data[-1:])
print("MO   End: ", end="")
pprint.pprint(MO_data[-1:])
print("MO   End Time: {}".format(datetime.datetime.fromtimestamp(MO_data[-1][0]).strftime('%Y-%m-%d %H:%M:%S.%f')))
print('')


# PH_data:
#   was: [timestamp, (x,y,z)]
# PH_data_err:
#   now: [timestamp, (x,y,z), MO_point, err]
#
# Not PH_data runs a little longer than PH_data_err b/c the mocap cut off sooner
# so we compute PH_data_err only through the end of the mocap data

# If PH data starts before MO data, advance PH until MO has started
PH_start_idx = 0
while PH_data[PH_start_idx][0] < MO_data[0][0]:
	PH_start_idx += 1

print("PH_start_idx", PH_start_idx)

PH_data_err = []
MO_idx = 0
for point in PH_data[PH_start_idx:]:
	try:
		while point[0] > MO_data[MO_idx][0]:
			MO_idx += 1
	except IndexError:
		print("MO ran out. Stopping processing at last common timestamp:", point[0])
		break
	MO_point = (MO_data[MO_idx-1][1] + MO_data[MO_idx][1]) / 2
	diff = MO_point - point[1]
	err = math.sqrt(np.sum(diff*diff))
	PH_data_err.append([
		point[0],
		point[1],
		MO_point,
		err
		])

with open("{}.processed.data".format(EXP), "w") as o:
	#o.write("# TIME\t\t\tPH X\tPH Y\tPH Z\tMO X\tMO Y\tMO Z\tERR\n")
	for point in PH_data_err:
		o.write("{}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\n".format(
			point[0],
			point[1][0],
			point[1][1],
			point[1][2],
			point[2][0],
			point[2][1],
			point[2][2],
			point[3],
			))

print("Done. Results written to {}.processed.data".format(EXP))
