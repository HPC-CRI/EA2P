#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ["PowerRam"]

import os
import psutil


class PowerRam():
	"""

	PowerRam
	---------------
	
	Python classes monitoring RAM's power usage. 
	We used an analytical approach to calibrate RAM power by combining information of DIMM nomminal Power for each DDR memory module version, number of DIMM slots in use and the memory footprint during application execution
	"""
	
	def __init__(self):
		"""

		PowerRam
		---------------
		
		Python classes monitoring RAM's power usage.
		"""
		self.ram_power = self.get_memory_power()
		self.number_slots = self.get_number_slots()

	def append_energy_usage(self):
		"""
		We used an analytical approach to calibrate RAM power by combining information of DIMM nomminal Power for each DDR memory module version, number of DIMM slots in use and the memory footprint during application execution
		"""
		ram_usage = psutil.virtual_memory()
		ram_percent = ram_usage[2]
		THRESHOLD0 = 5
		THRESHOLD1 = 10
		THRESHOLD2 = 25
		THRESHOLD3 = 50
		THRESHOLD4 = 70
		if ram_usage[2] <= THRESHOLD0 :
			ram_percent = 35
		elif ram_usage[2] <= THRESHOLD1 :
			ram_percent = 65
		elif ram_usage[2] <= THRESHOLD2 :
			ram_percent = 70
		elif ram_usage[2] <= THRESHOLD3 :
			ram_percent = 75
		elif ram_usage[2] <= THRESHOLD4 :
			ram_percent = 80
		else :
			ram_percent = 85

		energy_usage = {"dram":(self.ram_power * self.number_slots * ram_percent / 100)}
		#print(energy_usage)
		return energy_usage

	def get_number_slots(self):
		os.system("sudo dmidecode -t 17 | grep 'Memory Device' > tmp_ram_slots.txt")
		#os.system("sudo-g5k dmidecode -t 17 | grep 'Memory Device' > tmp_ram_slots.txt")
		with open(r"tmp_ram_slots.txt", 'r') as fp:
			lines = len(fp.readlines())
		return lines

	def get_memory_power(self):
		#os.system("sudo-g5k dmidecode -t 17 | grep 'Type: ' > tmp_ram_type.txt")
		os.system("sudo dmidecode -t 17 | grep 'Type: ' > tmp_ram_type.txt")
		with open(r"tmp_ram_type.txt", 'r') as fp:
			ram_type = fp.readlines()[0]

		os.system("sudo dmidecode -t 17 | grep 'GB' > tmp_ram_size.txt")
		#os.system("sudo-g5k dmidecode -t 17 | grep 'GB' > tmp_ram_size.txt")
		with open(r"tmp_ram_size.txt", 'r') as fp2:
			ram_size = fp2.readlines()[0]

		if ("DDR5" in ram_type) or ("DDR4" in ram_type) :
			if "16" in ram_size :
				return 4.0
			elif "32" in ram_size:
				return 5.0
			elif "64" in ram_size:
				return 6.0
			elif "128" in ram_size:
				return 8.0
			else :
				return 10.0
		elif "DDR3" in ram_type:
			return 4.5
		else :
			return 0.0
