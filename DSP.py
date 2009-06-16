from globvars import X,Y,Z,R

class DSP:
	def __init__(self):
		self.resetInt()
		self.fs = None
	def setFrameSpeed(self, fs):
		self.fs = fs
	def resetInt(self):
		self.a = [0] * 3
		self.v = [0] * 3
		self.p = [0] * 3
		self.omega = 0
		self.alpha = 0
		self.frame = (0,0,0,0)
	@staticmethod
	def mean(data, index, win_size = None):
		# 'data' is the list of tuples of fixed size
		if win_size > len(data) or win_size == None:
			win_size = len(data)
		if index > len(data):
			index %= len(data)
		temp = (data*2)[len(data)+index-(win_size-1):len(data)+index+1]
		return tuple([float(sum(x))/len(x) for x in zip(*temp)])
	def doInt(self, frame, cal, gap = 1):
		ffs = self.fs * gap
		for i in [X,Y,Z]:
			self.a[i] = (float(frame[i] - cal.data[i][0]) / cal.data[i][1] - 0) * 1.0
			self.v[i] += self.a[i] / float(ffs)
			self.p[i] += self.v[i] / float(ffs)
		self.omega = float(frame[R] - cal.data[R]) / 3.41
		self.alpha += self.omega / float(ffs)
		self.frame = frame
	def getData(self):
		return [
			self.frame,
			(self.alpha,),
			tuple(self.a),
			tuple(self.v),
			tuple(self.a)
		]