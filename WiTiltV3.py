import sys, time, serial
from globvars import *

class WiTiltV3:
	"""
	WiTilt v3 class, supports data aquisition from WiTilt v3 board
	"""
	def __init__(self, port = None, timeout = None) :
		"""
		Initialization pocedure: opens serial port, inits the pygame interface
		"""
		if port == None:
			self.port = '/dev/rfcomm0'
		else:
			self.port = port
		if timeout == None:
			self.timeout = 0.2
		else:
			self.timeout = timeout
		self.name = 'WiTiltV3'
		self.fs = None
		self.rng = None
		try:
			self.ser = self.portOpen()
		except Exception as reason:
			print >> sys.stderr, 'WiTiltV3.__init__(): %s' % reason
			return None
		self.write('A')
		self.ser.flushInput()
		# check if it is WiTiltV3
		self.write(' ')
		if self.getBytes().find('WiTilt') == -1 :
			print >> sys.stderr, 'WiTiltV3.__init__(): WiTiltV3 module is not recognized on specified port'
			return None
	def portOpen(self):
		count = 0
		nAttempts = 3
		ser = None
		while count < nAttempts:
			print "Trying [%d/%d] to open serial port: %s\r" % (count+1,nAttempts,self.port),
			sys.stdout.flush()
			try:
				ser = serial.Serial(self.port, 115200, timeout = self.timeout)
				print 'Port opened successfully',' '*40
				break
			except:
				count += 1
		if ser == None : raise Exception(sys.exc_info()[1])
		return ser
	def write(self,ch=' ',timeout=None):
		"""
		writes a character into the port and waits self.timeout seconds
		"""
		self.ser.write(ch)
		self.ser.flush()
		if timeout == None: timeout = self.timeout
		time.sleep(timeout)
	def getBytes(self,nBytes = None):
		"""
		Returnes all data in waiting from the open serial port
		"""
		inWaiting = self.ser.inWaiting()
		if (nBytes == None) or (nBytes > inWaiting):
			return self.ser.read(inWaiting)
		else:
			return self.ser.read(nBytes)
	def getMainMenu(self):
		"""
		Returns any available text data from witilt module (or prints error message)
		"""
		if not self.ser.inWaiting :
			return 'WiTiltV3.getResponse(): no response from WiTilt module'
		else:
			return (self.getBytes()).lstrip('\n\r $STF,01').rstrip('\n\r: ')
	def checkIt(self, string):
		# Check if the module is in correct state
		temp = string
		signal_str = 'WiTilt v3.3'
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('WiTiltV3.CheckIt(): WiTilt module isn\'t ready (%s)' % temp[:20])
		# Determine sampling frequency
		temp = string
		signal_str = 'Frequency ('
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('WiTiltV3.CheckIt(): Sampling frequesncy can\'t be identified')
		temp = temp[pos + len(signal_str):]
		self.fs = int(temp[0:temp.find('Hz)')])
		# Make sure the binary mode is ON
		temp = string
		signal_str = 'Mode (Binary)'
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('WiTiltV3.CheckIt(): Binary mode isn\'t activated')
		# Make sure all required data channels are active
		temp = string
		signal_str = 'Channels (XYZ-R Active)'
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('WiTiltV3.CheckIt(): Required data channels are XYZ and R')
		# Make sure the sensor range is set
		temp = string
		signal_str = 'Sensor Range ('
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('WiTiltV3.CheckIt(): Sensor range can\'t be identified')
		temp = temp[pos + len(signal_str):]
		if temp[0] == ')' : raise Exception('WiTiltV3.CheckIt(): Sensor range isn\'t configured')
		self.rng = float(temp[0:temp.find('g)')])
		return True