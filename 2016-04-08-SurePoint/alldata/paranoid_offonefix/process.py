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
import os

from dateutil.parser import parse

try:
	EXP = sys.argv[1]
except IndexError:
	print("ERR: Script requires one argument, experiment to process")
	print("     Try ./process first_flight")
	sys.exit(1)


TIME_FIX = 3
if EXP == 'out.1':
	SEC_FIX = 14*60-24.2
if EXP == 'out.2':
	SEC_FIX = -24*60*60 - 30*60 - 8
if EXP == 'out.3':
	SEC_FIX = -24*60*60 - 30*60 - 32
if EXP[:5] == 'out.4':
	SEC_FIX = -24*60*60 - 30*60 - 81.5
if EXP == 'out.5':
	SEC_FIX = -24*60*60 - 35*60 - -40
if EXP == 'out.6':
	SEC_FIX = -24*60*60 - 83*60 - -13
if EXP == 'out.7':
	SEC_FIX = -24*60*60 - 87*60 - -17


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

with open('motion/{}'.format(EXP)) as ifile:
	for line in ifile:
		if line[0] == '#':
			continue
		line = line.split()
		PH_data.append([
			float(line[0]),
			np.array(
				list(map(float, line[1:4]))
			)]
		)

print("PH Start Time: {}".format(datetime.datetime.fromtimestamp(PH_data [0][0]).strftime('%Y-%m-%d %H:%M:%S.%f')))
print("PH   End Time: {}".format(datetime.datetime.fromtimestamp(PH_data[-1][0]).strftime('%Y-%m-%d %H:%M:%S.%f')))


optfile = 'optitrack/{}.csv'.format(EXP)
if EXP[:5] == 'out.4':
	optfile = 'optitrack/out.4.csv'

with open(optfile) as f:
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


with open(optfile) as csvfile:
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
			if EXP == 'motion1' and int(row[0]) == 3882:
				OBJ_IDX = 3
			if EXP == 'out.5' and int(row[0]) == 166:
				OBJ_IDX = 3
			if EXP == 'out.5' and int(row[0]) == 365:
				OBJ_IDX = 6
			if EXP == 'out.5' and int(row[0]) == 1526:
				OBJ_IDX = 9
			if EXP == 'out.6' and int(row[0]) == 1610:
				OBJ_IDX = 3
			if EXP == 'out.6' and int(row[0]) == 9298:
				OBJ_IDX = 6
			try:
				MO_data.append([
					MO_start_ts + float(row[1]),
					np.array([
						-float(row[4+OBJ_IDX]) + 7.102,
						-float(row[2+OBJ_IDX]) + 7.616,
						 float(row[3+OBJ_IDX]) + 0.065
						 ])
					])
			except ValueError:
				if row[2+OBJ_IDX] == '':
					continue
				else:
					print(row)
					raise


print("PH   Len: ", len(PH_data))
print("MO   Len: ", len(MO_data))
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

last_MO = None
last_ts = None

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
	diff_xy = MO_point[:2] - point[1][:2]
	err_xy = math.sqrt(np.sum(diff_xy**2))

	if last_MO is None:
		speed = 0
	else:
		speed = np.sqrt(sum( (MO_point - last_MO)**2 )) / (point[0] - last_ts)
	last_MO = MO_point
	last_ts = point[0]

	PH_data_err.append([
		point[0],
		point[1],
		MO_point,
		err,
		err_xy,
		abs(MO_point[0] - point[1][0]),
		abs(MO_point[1] - point[1][1]),
		abs(MO_point[2] - point[1][2]),
		speed,
		])

aw = None
if os.path.exists(sys.argv[1] + '.anchor_windows'):
	aw = {}
	for line in open(sys.argv[1] + '.anchor_windows'):
		aw[float(line.split()[0])] = list(map(int, line.split()[1:4]))

with open("{}.processed.data".format(EXP), "w") as o:
	#o.write("# TIME\t\t\tPH X\tPH Y\tPH Z\tMO X\tMO Y\tMO Z\tERR\n")
	o.write( "#ts\t\tpp x  \tpp y  \tpp z  \tmo x  \tmo y  \t mo z \txyz er\txy err\tx err \ty err \tz err \taw1   \taw2   \taw3   \tspeed   \n")
	for point in PH_data_err:
		o.write("{}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:>2d}\t{:>2d}\t{:>2d}\t{:>2.3f}\n".format(
			point[0],
			point[1][0],
			point[1][1],
			point[1][2],
			point[2][0],
			point[2][1],
			point[2][2],
			point[3],
			point[4],
			point[5],
			point[6],
			point[7],
			0 if aw is None else aw[point[0]][0],
			0 if aw is None else aw[point[0]][1],
			0 if aw is None else aw[point[0]][2],
			point[8],
			))

print("Done. Results written to {}.processed.data".format(EXP))
