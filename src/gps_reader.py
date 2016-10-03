#!/usr/bin/env python
import serial
import re


def dlog(strg):
	#pass
	print(strg)


class GpsException(BaseException):
	pass


class BadChecksum(GpsException):
	pass


class MalformedString(GpsException):
	pass


class CommonGpsObject():
	def __init__(self):
		self.raw_string = ""
		self.payload_string = ""
		self.checksum_string = ""
		self.checksum = 0
		self.valid_checksum = False
	
	def parse_common(self, input_string):
		dlog("parse_common: {}".format(input_string.strip()))
		self.raw_string = input_string
		payload = re.split(r'\*',input_string)
		assert len(payload)==2
		self.payload_string = payload[0].strip()
		self.checksum_string = payload[1].rstrip()
		# Validate checksum
		dlog("Validating checksum...")
		calc_checksum = 0x00
		for character in self.payload_string:
			if r'$' == character:
				continue
			elif r'*' == character:
				break
			else:
				calc_checksum ^= ord(character)
		calc_checksum_str = str( hex(calc_checksum) ).lstrip("0x")
		if (calc_checksum_str != self.checksum_string):
			raise BadChecksum(input_string)


class GgaObject(CommonGpsObject):
	def __init__(self):
		CommonGpsObject.__init__(self)
	
	def parse(self, input_str):
		# First ensure its a valid NMEA string
		CommonGpsObject.parse_common(self, input_str)
		# Populate all data from the parsed string
		for idx,data in enumerate(re.split(',',self.payload_string)):
			# TODO
			pass


class GllObject(CommonGpsObject):
	def __init__(self):
		CommonGpsObject.__init__(self)
	
	def parse(self, input_str):
		# First ensure its a valid NMEA string
		CommonGpsObject.parse_common(self, input_str)
		# Populate all data from the parsed string
		for idx,data in enumerate(re.split(',',self.payload_string)):
			# TODO
			pass


class GsaObject(CommonGpsObject):
	def __init__(self):
		CommonGpsObject.__init__(self)
	
	def parse(self, input_str):
		# First ensure its a valid NMEA string
		CommonGpsObject.parse_common(self, input_str)
		# Populate all data from the parsed string
		for idx,data in enumerate(re.split(',',self.payload_string)):
			# TODO
			pass


class RmcObject(CommonGpsObject):
	def __init__(self):
		CommonGpsObject.__init__(self)
		self.time_str = ""
		self.time = 0.0
		self.valid = False # decoded valid_flag
		self.valid_flag = 'V'
		self.longitude = 0.0
		self.long_dir = "N"
		self.latitude = 0.0
		self.lat_dir = "N"
		self.unknown1 = 0.0
		self.unknown2 = 0.0
		self.date_str = 0
		self.date = 0 # TODO: standard python date library thing
	
	def __repl___(self):
		if not self.valid:
			return "Invalid GPS Packet!!!"
		else:
			return "Valid RMC packat at time %s" % (self.time_str)
	
	def is_valid(self):
		return self.valid
	
	def parse(self, input_str):
		# First ensure its a valid NMEA string
		CommonGpsObject.parse_common(self, input_str)
		# Populate all data from the parsed string
		for idx,data in enumerate(re.split(',',self.payload_string)):
			# TODO
			print ("{}:\t{}".format(idx,data))
	

class GpsParser(serial.Serial):
	""" TODO"""
	def __init__(self, port, baudrate):
		# Create objects to hold all (supported) types of NMEA message
		self.RMC = RmcObject()
		self.GGA = GgaObject()
		self.GLL = GllObject()
		self.GSA = GsaObject()
		# Blank a string to store any GPS start-up text
		self.text = ""
		# All other GPS metadata
		self.rate = 0       # Hz
		self.valid = False  # Is the LATEST GPS message valid?
		# Base class initialization
		# TODO: launch this in a separate thread that's always watching
		#       and populating the latest data
		try:
			super(GpsParser,self).__init__(port=port, baudrate=baudrate)
		except:
			print("Didn't work.")
	
	def parse_manual(self):
		linein = super(GpsParser,self).readline()
		linein.strip()
		if re.match(r"\$GPTXT,", linein):
			print("Text information: {}".format(linein))
			self.text.append(linein)
		elif re.match(r"\$GPRMC,", linein):
			self.RMC.parse(linein)
			dlog("Parsed: {}".format(self.RMC))
			# Extract relevant data from RMC message
			self.valid = self.RMC.is_valid()
			# TODO: the rest
		elif re.match(r"\$GPGGA,", linein):
			self.GGA.parse(linein)
			dlog("Parsed: {}".format(self.GGA))
		elif re.match(r"\$GPGLL,", linein):
			self.GLL.parse(linein)
			dlog("Parsed: {}".format(self.GLL))
		elif re.match(r"\$GPGSA,", linein):
			self.GSA.parse(linein)
			dlog("Parsed: {}".format(self.GSA))
	
	### Getters ###
	# Access GPS hardware infromation
	def get_rate(self) : return self.rate
	def get_text(self) : return self.text
	# Access GPS data
	def valid(self)    : return self.valid
	def get_time(self) : return self.time
	def get_location(self) : return (self.logitude, self.latitude)
	# Get raw NMEA object types
	def get_rmc(self) : return self.RMC
	def get_gga(self) : return self.GGA
	def get_gll(self) : return self.GLA
	def get_gsa(self) : return self.GSA


def main():
	JeffGps = GpsParser(port='/dev/ttyS0', baudrate=115200)
	
	print ("Going to print out all RMC messages...")
	while 1:
		JeffGps.parse_manual()

if __name__ == '__main__':
    main()
