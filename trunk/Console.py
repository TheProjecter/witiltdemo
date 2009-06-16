import sys, pygame, threading, time, warnings, getopt
import Screen, Calib, WiTiltV3, DSP
from globvars import *

class Console(threading.Thread):
	"""
	Console class, creates and manages user interface
	"""
	def __init__(self):
		# Superclass constructor invocation
		threading.Thread.__init__(self)
		# Command line arguments processing
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hp:", ["help","port="])
		except Exception as comment:
			print >> sys.stderr, 'Console.__init__(): %s' % comment
			sys.exit(2)
		# Options processing
		port = None
		for o, a in opts:
			if o in ("-h", "--help"):
				self.usage(sys.argv[0])
				sys.exit(0)
			elif o in ("-p", "--port"):
				port = a
			else:
				assert False, "unhandled option"
		# Ignoring silly warnings
		warnings.filterwarnings('ignore', category=DeprecationWarning, message=r'os\.popen3')
		# Creating instances
		self.witilt = WiTiltV3.WiTiltV3(port)
		self.screen = Screen.Screen((1000,700),'freemono,sharjah',20)
		self.cal = Calib.Calib(self.witilt)
		self.dsp = DSP.DSP()
		self.screen.setCaption(self.witilt.name)
	def toList(self,string):
		return [item for item in string.splitlines() if item]
	def usage(self,fn):
		print "Usage: python %s [-h] [-p port]" % fn
		print "   -h        -- this help message;"
		print "   -p port   -- use specific serial port (/dev/rfcomm0 by default)"
	def getMenuText(self,menuid = 0):
		text = []
		if menuid == 0:
			text.append("Main menu:")
			text.append("=======================")
			text.append("1. Start position/rotation monitor")
			text.append("2. Configure WiTilt module")
			text.append("3. Technical information")
			text.append("4. Quit")
		elif menuid == 1:
			text.append("Technical information:")
			text.append("=======================")
		return text
	def run(self):
		# Initialization
		State = 'm_menu'
		nState = 'm_menu'
		pState = ''
		myEvent = pygame.event.Event(pygame.USEREVENT)
		pygame.event.clear()
		pygame.event.set_allowed(None)
		pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.USEREVENT])
		pygame.event.post(myEvent)
		# Frame loop
		while True:
			# Event handling
			event = pygame.event.wait()
			cmd = ''
			if event.type == pygame.QUIT:
				break
			elif event.type == pygame.KEYDOWN:
				if event.unicode in ['x', 'i', 'd', 'y', 'n', ' ', 'c', 'A', 'S', 'R', '1', '2', '3', '4', '5', '6', '7'] :
					cmd = event.unicode.encode()
				elif event.key == pygame.K_ESCAPE:
					if State != 'm_menu':
						State = nState = 'm_menu'
						if self.witilt.ser.inWaiting():
							self.witilt.write('A')
							self.witilt.ser.flushInput()
							self.screen.dRects = []
							pygame.display.update()
					else:
						break
			# Drawing something into the frame
			if State == 'm_menu':
				# Main menu
				if cmd == '1':
					nState = 'monitor'
					pygame.event.post(myEvent)
				elif cmd == '2':
					nState = 'w_menu'
					pygame.event.post(myEvent)
				elif cmd == '3':
					nState = 'info'
					pygame.event.post(myEvent)
				elif cmd == '4':
					break
				else:
					pOut = self.getMenuText(0)
					self.screen.dRects.extend(self.screen.putText(pOut))					
			elif State == 'w_menu':
				# WiTilt menu
				if pState != State:
					# Very first invocation
					self.witilt.ser.flushInput()
					self.witilt.write(' ')
					pOut = self.toList(self.witilt.getMainMenu())
				elif cmd != '':
					# Only if command has been issued
					self.witilt.write(cmd)
					pOut = self.toList(self.witilt.getMainMenu())
				self.screen.dRects.extend(self.screen.putText(pOut))
			elif State == 'monitor':
				# Monitor and show position and orientation
				if pState != State:
					try:
						# Check monitoring parameters: sampling frequency, channels, etc
						self.witilt.write(' ')
						self.witilt.checkIt(self.witilt.getBytes())
						fs = self.witilt.fs
						self.dsp.setFrameSpeed(fs)
						# Get calibration data
						if not self.cal.loadData():
							self.witilt.write('3')
							self.cal.ProcessString(self.witilt.getBytes())
							self.witilt.write('x')
							self.witilt.ser.flushInput()
						print 'Calibration data to be used: %s' % self.cal.data
						# Finally...
						self.witilt.write('1')
						self.witilt.write('S')
						buf=[]
						pygame.time.delay(40)						# wait until 4 frames will be collected in witilt buffer
						temp = self.witilt.ser.read(40)			# read 20 bytes expecting the beginning of transfer
						pos = temp.find('#@\x00')
						if pos == -1 : raise Exception('Can\'t start the process...')
						buf.extend(temp[pos:])
						Index = ord(buf[2])*256+ord(buf[3])
						if Index != 1 : raise Exception('Wrong data arrived at the initialization stage (Index = %d)' % Index)
						val_cnt = 0										# current frame counter
						max_cnt = 256									# how many frames are constantly kept
						frames = [(0,0,0,0)] * max_cnt
						pIndex = 0
						timeOffset = pygame.time.get_ticks()
						onCalibration = False
					except Exception as comment:
						print >> sys.stderr, 'Console.run(): %s' % comment
						nState = 'm_menu'
				else:
					# Get data from WiTilt
					realTime = (pygame.time.get_ticks() - timeOffset) / 1000
					if self.witilt.ser.inWaiting() > (frmSize*fs/fps):
						buf.extend(self.witilt.getBytes())
					i = 0;
					while (len(buf) > frmSize) and (i < max_cnt):
						# Offset to the beginning of the frame
						if buf[0] != '#' or buf[frmSize-1] != '$' :
							for j in range(len(buf)) :
								if buf[j] == '$' : break
							buf[:(j+1)] = []
						# Extract frame from the buffer (first frmSize bytes)
						(buf[:frmSize],raw_frame) = ([],map(ord,buf[2:(frmSize-1)]))
						Index = raw_frame[0]*256 + raw_frame[1]
						frames[val_cnt] = (
							raw_frame[2]*256 + raw_frame[3],
							raw_frame[4]*256 + raw_frame[5],
							raw_frame[6]*256 + raw_frame[7],
							raw_frame[8]*256 + raw_frame[9]
						)
						if onCalibration:
							# Gathering calibration data
							if self.cal.onRecord:
								self.cal.doRecord(frames[val_cnt])
							else:
								self.cal.getAxes(frames[val_cnt])
						else:
							# Process the frame
							dsp_frame = self.dsp.mean(frames,val_cnt,64)
							# Integrate speed, position and angle
							self.dsp.doInt(dsp_frame,self.cal,Index - pIndex)
						# Index assignment
						pIndex = Index
						# Frame counter update
						val_cnt = (val_cnt + 1) % max_cnt
						i += 1
					# Keyboard processing
					if cmd == ' ' :
						# Reset integrators
						self.dsp.resetInt()
					elif cmd == 'c' :
						# Toggle calibration mode
						if onCalibration :
							if self.cal.hash[:] == [1] * 6:
								self.dsp.resetInt()
								onCalibration = False
								self.cal.ProcessRecord()
						else:
							self.cal.init()
							onCalibration = True							
					# Drawing
					if onCalibration:
						self.screen.calUpdate(self.cal)
					else:
						data = self.dsp.getData()
						#print data
						self.screen.monUpdate(data,realTime)
				pygame.event.post(myEvent)
			elif State == 'info':
				# Displaying technical info
				if pState != State:
					# Very first invocation
					pOut = self.getMenuText(1)
					dRects.extend(self.screen.putText(pOut))
			else:
				# Wrong state
				print >> sys.stderr, 'Console.run(): Wrong state'
			# Update states
			pState = State
			State = nState
			# Redraw the screen
			self.screen.reDraw()
		self.witilt.ser.close()
		pygame.quit ()
		print "Done!"
	
	
	
