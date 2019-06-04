#!/usr/bin/env python3

import logging
log = logging.getLogger(__name__)

import os
if 'DEBUG' in os.environ:
	logging.basicConfig(level=logging.DEBUG)

try:
	import coloredlogs
	#coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s'
	coloredlogs.DEFAULT_LOG_FORMAT = '%(message)s'
	coloredlogs.DEFAULT_LEVEL_STYLES['debug'] = {'color': 'cyan'}
	if 'DEBUG' in os.environ:
		coloredlogs.install(level=logging.DEBUG)
	else:
		coloredlogs.install()

except ImportError:
	pass


import argparse
import binascii
import struct
import sys
import time

import serial

import numpy as np
import scipy.io as sio
from scipy.optimize import fmin_bfgs, least_squares

import dataprint


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', default='./motion/out.raw.4')
parser.add_argument('-o', '--outfile',  default='out.4.anchor_windows')

args = parser.parse_args()

ofile = open(args.outfile, 'w')

##########################################################################

def useful_read(length):
	b = dev.read(length)
	while len(b) < length:
		r = dev.read(length - len(b))
		if len(r) == 0:
			raise EOFError
		b += r
	assert len(b) == length
	return b


HEADER      = (0x80018001).to_bytes(4, 'big')
DATA_HEADER = (0x8080).to_bytes(2, 'big')
FOOTER      = (0x80FE).to_bytes(2, 'big')
DWT_TIME_UNITS = 1/499.2e6/128;
SPEED_OF_LIGHT = 2.99792458e8;
AIR_N = 1.0003;
good = 0
bad = 0
NUM_RANGING_CHANNELS = 3
NUM_RANGING_BROADCASTS = 30
EUI_LEN = 8
data_section_length = 8*NUM_RANGING_CHANNELS + 8+1+1+8+8+30*8

def antenna_and_channel_to_subsequence_number(tag_antenna_index, anchor_antenna_index, channel_index):
	anc_offset = anchor_antenna_index * NUM_RANGING_CHANNELS
	tag_offset = tag_antenna_index * NUM_RANGING_CHANNELS * NUM_RANGING_CHANNELS
	base_offset = anc_offset + tag_offset + channel_index
	
	ret = base_offset
	return ret

def oneway_get_ss_index_from_settings(anchor_antenna_index, window_num):
	tag_antenna_index = 0
	channel_index = window_num % NUM_RANGING_CHANNELS
	ret = antenna_and_channel_to_subsequence_number(tag_antenna_index, anchor_antenna_index, channel_index)
	return ret

def find_header():
	b = useful_read(len(HEADER))
	while b != HEADER:
		b = b[1:len(HEADER)] + useful_read(1)

def dwtime_to_millimeters(dwtime):
	ret = dwtime*DWT_TIME_UNITS*SPEED_OF_LIGHT/AIR_N
	ret = ret * 1000;
	return ret


###############################################################

data_array = []

anc_seen_hist = [5]

windows = [0,0,0]

start = 1459998187.496
first_time = None

last_position = np.array((0,0,0))

dev = open(args.file, 'rb')
print("Reading data back from file:", args.file)

try:
	while True:
		log.info("{:>20s}: Good {}    Bad {}    Avg {:.1f}    Last {}\t\t".format(
				args.file, good, bad, np.mean(anc_seen_hist), anc_seen_hist[-1]))

		try:
			log.debug("")
			log.debug("")
			log.debug("")
			find_header()

			num_anchors, = struct.unpack("<B", useful_read(1))

			ranging_broadcast_ss_send_times = np.array(struct.unpack("<30Q", useful_read(8*NUM_RANGING_BROADCASTS)))

			if first_time is None:
				first_time = ranging_broadcast_ss_send_times[15]
			DWT_TIME_UNITS = (1.0/499.2e6/128.0)
			ts = start +  (ranging_broadcast_ss_send_times[15] - first_time) * DWT_TIME_UNITS

			ranges = {}
			round_windows = [0,0,0]

			for x in range(num_anchors):
				b = useful_read(len(DATA_HEADER))
				if b != DATA_HEADER:
					log.warn("missed DATA_HEADER")
					raise AssertionError
				anchor_eui = useful_read(EUI_LEN)
				anchor_eui = anchor_eui[::-1] # reverse bytes
				anchor_eui = binascii.hexlify(anchor_eui).decode('utf-8')
				anchor_final_antenna_index, = struct.unpack("<B", useful_read(1))
				window_packet_recv, = struct.unpack("<B", useful_read(1))
				anc_final_tx_timestamp, = struct.unpack("<Q", useful_read(8))
				anc_final_rx_timestamp, = struct.unpack("<Q", useful_read(8))
				tag_poll_first_idx, = struct.unpack("<B", useful_read(1))
				tag_poll_first_TOA, = struct.unpack("<Q", useful_read(8))
				tag_poll_last_idx, = struct.unpack("<B", useful_read(1))
				tag_poll_last_TOA, = struct.unpack("<Q", useful_read(8))
				tag_poll_TOAs = np.array(struct.unpack("<"+str(NUM_RANGING_BROADCASTS)+"H", useful_read(2*NUM_RANGING_BROADCASTS)))

				if tag_poll_first_idx >= NUM_RANGING_BROADCASTS or tag_poll_last_idx >= NUM_RANGING_BROADCASTS:
					log.warn("tag_poll outside of range; skpping")
					continue
			
				# Perform ranging operations with the received timestamp data
				tag_poll_TOAs[tag_poll_first_idx] = tag_poll_first_TOA
				tag_poll_TOAs[tag_poll_last_idx] = tag_poll_last_TOA

				approx_clock_offset = (tag_poll_last_TOA - tag_poll_first_TOA)/(ranging_broadcast_ss_send_times[tag_poll_last_idx] - ranging_broadcast_ss_send_times[tag_poll_first_idx])

				# Interpolate betseen the first and last to find the high 48 bits which fit best
				for jj in range(tag_poll_first_idx+1,tag_poll_last_idx):
					estimated_toa = tag_poll_first_TOA + (approx_clock_offset*(ranging_broadcast_ss_send_times[jj] - ranging_broadcast_ss_send_times[tag_poll_first_idx]))
					actual_toa = (int(estimated_toa) & 0xFFFFFFFFFFF0000) + tag_poll_TOAs[jj]

					if(actual_toa < estimated_toa - 0x7FFF):
						actual_toa = actual_toa + 0x10000
					elif(actual_toa > estimated_toa + 0x7FFF):
						actual_toa = actual_toa - 0x10000

					tag_poll_TOAs[jj] = actual_toa

				# Get the actual clock offset calculation
				num_valid_offsets = 0
				offset_cumsum = 0
				for jj in range(NUM_RANGING_CHANNELS):
					if(tag_poll_TOAs[jj] & 0xFFFF > 0 and tag_poll_TOAs[26+jj] & 0xFFFF > 0):
						offset_cumsum = offset_cumsum + (tag_poll_TOAs[26+jj] - tag_poll_TOAs[jj])/(ranging_broadcast_ss_send_times[26+jj] - ranging_broadcast_ss_send_times[jj])
						num_valid_offsets = num_valid_offsets + 1

				if num_valid_offsets == 0:
					continue
				offset_anchor_over_tag = offset_cumsum/num_valid_offsets;

				# Figure out what broadcast the received response belongs to
				ss_index_matching = oneway_get_ss_index_from_settings(anchor_final_antenna_index, window_packet_recv)
				if int(tag_poll_TOAs[ss_index_matching]) & 0xFFFF == 0:
					log.warn("no bcast ss match, ss_index_matching {}, TOAs[{}] = {}".format(
						ss_index_matching, ss_index_matching, tag_poll_TOAs[ss_index_matching]))
					continue
		
				matching_broadcast_send_time = ranging_broadcast_ss_send_times[ss_index_matching]
				matching_broadcast_recv_time = tag_poll_TOAs[ss_index_matching]
				response_send_time = anc_final_tx_timestamp
				response_recv_time = anc_final_rx_timestamp
		
				two_way_TOF = ((response_recv_time - matching_broadcast_send_time)*offset_anchor_over_tag) - (response_send_time - matching_broadcast_recv_time)
				one_way_TOF = two_way_TOF/2
		
				# Declare an array for sorting ranges
				distance_millimeters = []
				for jj in range(NUM_RANGING_BROADCASTS):
					broadcast_send_time = ranging_broadcast_ss_send_times[jj]
					broadcast_recv_time = tag_poll_TOAs[jj]
					if int(broadcast_recv_time) & 0xFFFF == 0:
						continue
		
					broadcast_anchor_offset = broadcast_recv_time - matching_broadcast_recv_time
					broadcast_tag_offset = broadcast_send_time - matching_broadcast_send_time
					TOF = broadcast_anchor_offset - broadcast_tag_offset*offset_anchor_over_tag + one_way_TOF
		
					distance_millimeters.append(dwtime_to_millimeters(TOF))

				range_mm = np.percentile(distance_millimeters,12)
				range_mm -= 140

				range_m = range_mm / 1000

				if range_mm < 0 or range_mm > (1000*30):
					log.warn('Dropping impossible range %d', range_mm)
					continue

				ranges[anchor_eui[-2:]] = range_mm / 1000
				windows[window_packet_recv] += 1
				round_windows[window_packet_recv] += 1

			footer = useful_read(len(FOOTER))
			if footer != FOOTER:
				raise AssertionError

			if len(anc_seen_hist) > 20:
				anc_seen_hist.pop(0)
			anc_seen_hist.append(len(ranges))

			ofile.write('{:.2f}\t{}\t{}\t{}\n'.format(ts, *round_windows))

			good += 1


		except (AssertionError, NotImplementedError):
			bad += 1

except EOFError:
	pass

print("\nGood {}\nBad  {}".format(good, bad))
if sum(windows):
	print("Windows {} ({:.1f}) {} ({:.1f}) {} ({:.1f})".format(
		windows[0], 100* windows[0] / sum(windows),
		windows[1], 100* windows[1] / sum(windows),
		windows[2], 100* windows[2] / sum(windows),
		))



