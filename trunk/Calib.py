from globvars import X, Y, Z, R
import sys

class Calib:
	def __init__(self,witilt):
		self.init()
		self.witilt = witilt
	def init(self):
		self.hash = [0] * 6
		self.data = []
		self.num_frames = 400
		self.frames = [[]] * 6
		self.index = 0
		self.frm_counter = 0
		self.axes = (0,0)
		for i in range(len(self.frames)):
			self.frames[i] = [(0,0,0,0)] * self.num_frames
		self.onRecord = False
		self.onCalibration = False
		self.msg = ''
	def getColor(self):
		if self.onRecord :
			return (255,0,0)
		else :
			return None
	def doRecord(self, frame):		
		if self.index < self.witilt.fs * 2 :
			self.msg = ['Do not move or rotate the module','']
			self.frm_counter = 0
		else:
			if self.frm_counter < self.num_frames:
				self.msg = ['Recording...','']
				self.frames[self.axes[0]][self.frm_counter] = frame
				self.frm_counter += 1
			else:
				self.hash[self.axes[0]] = 1
				self.onRecord = False
		self.index += 1
	def getAxes(self, frame):
		mid_value = 511
		raw = [abs(x-mid_value) for x in [frame[X],frame[Y],frame[Z]]]
		temp = ([i for i in range(len(raw)) if raw[i] == max(raw)][0])
		self.axes = (self.axes[1],temp * 2 + (frame[temp] > mid_value))
		self.msg = []
		self.msg.append('Selected axes is \'%s\'' % ['X[L]','X[H]','Y[L]','Y[H]','Z[L]','Z[H]'][self.axes[1]])
		self.msg.append(['','(calibrated)'][self.hash[self.axes[1]]])
		if (self.axes[0] == self.axes[1]) and (self.hash[self.axes[0]] == 0):
			self.index += 1
			if self.index > (self.num_frames / 4):
				self.onRecord = True
				self.index = 0
		else:
			self.index = 0
	def ProcessRecord(self):
		# Check if calibration data have been collected in full
		if self.hash[:] != [1] * 6:
			return False
		# calculate calibration data based on gathered cal_frames
		average = [0] * 7
		self.data = []
		for i in range(len(self.frames)):
			average[i] = sum([x[int(i/2)] for x in self.frames[i]]) / len(self.frames[i])
			average[6] += sum([x[R] for x in self.frames[i]]) / len(self.frames[i])
		for i in [X,Y,Z]:
			width = int((average[i*2+1]-average[i*2])/2)
			mid = average[i*2] + width
			self.data.append((mid,width))
		self.data.append(int(average[6]/6))
		print 'New calibration data: %s' % self.data
		self.saveData()
		return True
	def ProcessString(self, string = None):
		if string == None : raise Exception('Calib.getFromString(): No string was passed')
		temp = string
		self.data = []
		#-- X channel
		signal_str = 'X Midpoint: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): Midpoint for X channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		mid = int(temp[:temp.find(' ')])
		signal_str = 'X G-Width: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): G-Width for X channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		width = int(temp[:temp.find('\n')])
		self.data.append((mid,width))
		#-- Y channel
		signal_str = 'Y Midpoint: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): Midpoint for Y channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		mid = int(temp[:temp.find(' ')])
		signal_str = 'Y G-Width: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): G-Width for Y channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		width = int(temp[:temp.find('\n')])
		self.data.append((mid,width))
		#-- Z channel
		signal_str = 'Z Midpoint: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): Midpoint for Z channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		mid = int(temp[:temp.find(' ')])
		signal_str = 'Z G-Width: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): G-Width for Z channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		width = int(temp[:temp.find('\n')])
		self.data.append((mid,width))
		#-- R channel
		temp = string
		signal_str = 'Zero Value: '
		pos = temp.find(signal_str)
		if pos == -1 : raise Exception('Calib.getFromString(): Midpoint for R channel can\'t be identified')
		temp = temp[pos + len(signal_str):]
		self.data.append(int(temp[:temp.find('\n')]))
		return True
	def saveData(self, fn = 'calib.dat'):
		fout = open(fn,'w')
		fout.writelines(repr(self.data))
		fout.close()
	def loadData(self, fn = 'calib.dat'):
		fin = None
		while True:
			try :
				if not fn : return False
				fin = open(fn, 'r')
				break
			except Exception as comment:
				print >> sys.stderr, 'Calib.loadData(): %s' % comment
				fn = raw_input('File name with calibration data (empty to cancel operation)')
		data = None
		while True:
			try:
				line = fin.readline()
				if line == '\n' : continue
				data = eval(line)
				if (type(data) == list) or (not line):
					break
			except Exception as comment:
				print >> sys.stderr, 'Calib.loadData(): %s' % comment
		try:
			if type(data) == list and map(type,data) == [tuple,tuple,tuple,int] and	map(len,data[0:3]) == [2,2,2]:
				self.data = data
				fin.close()
				return True
		except Exception as comment:
				print >> sys.stderr, 'Calib.loadData(): %s' % comment
		return False