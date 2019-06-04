#!/usr/bin/env python3

import sys
import struct

HEADER      = (0x80018001).to_bytes(4, 'big')
DWT_TIME_UNITS = 1/499.2e6/128

dev = open('out.exp{}.raw'.format(sys.argv[1]), 'rb')
o   = open('out.exp{}.txt'.format(sys.argv[1]), 'w')

def useful_read(length):
	b = dev.read(length)
	while len(b) < length:
		r = dev.read(length - len(b))
		if len(r) == 0:
			raise EOFError
		b += r
	assert len(b) == length
	return b

def find_header():
	b = useful_read(len(HEADER))
	while b != HEADER:
		b = b[1:len(HEADER)] + useful_read(1)


last_ts = None

any_t = False
count = 0
total = 0

last_idx = None

while True:
	find_header()
	ts, = struct.unpack("<Q", useful_read(8))
	if last_ts is None or last_ts > ts:
		t = 0
	else:
		t = (ts-last_ts)*DWT_TIME_UNITS
	last_ts = ts
	useful_read(15)
	id = useful_read(1)
	bitmask, = struct.unpack("<Q", useful_read(8))
	idx = useful_read(1)

	if any_t:
		count += 1
		if last_idx != idx:
			total += 1
		last_idx = idx
		print("** {} {}".format(count, total))
		o.write("{} {}\n".format(count, total))
	else:
		if idx != b'\x00':
			o.write("{} {}\n".format(count, total))
			count += 1
			o.write("{} {}\n".format(count, total))
			count += 1
			last_idx = idx
			any_t = True
			total = 1
			print("** {} {}".format(count, total))
			o.write("{} {}\n".format(count, total))

	print(t, bitmask, idx)

