#!/usr/bin/env python3

import argparse
import binascii
import os
import struct
import sys

import serial

import numpy as np
import scipy.io as sio

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--serial',   default='/dev/tty.usbserial-AL00EZAS')
parser.add_argument('-b', '--baudrate', default=3000000, type=int)
parser.add_argument('-o', '--outfile',  default='out')
parser.add_argument('-t', '--textfiles',action='store_true',
		help="Generate ASCII text files with the data")
parser.add_argument('-m', '--matfile',  action='store_true',
		help="Generate Matlab-compatible .mat file of the data")
parser.add_argument('-n', '--binfile',  action='store_true',
		help="Generate binary file of the data")

args = parser.parse_args()

dev = serial.Serial(args.serial, args.baudrate)
if dev.isOpen():
	print("Connected to device at " + dev.portstr)
else:
	raise NotImplementedError("Failed to connect to serial device " + args.serial)


def useful_read(length):
	b = dev.read(length)
	while len(b) < length:
		b += dev.read(length - len(b))
	assert len(b) == length
	return b


of = open('out.raw.{}'.format(args.outfile), 'wb')

while True:
	of.write(dev.read())


