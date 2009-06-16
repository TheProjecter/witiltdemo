import pygame, sys, math
from globvars import *

class Screen:
	def __init__(self, size = (1000,700), fntName = None, fntSize = 20):
		pygame.init()
		# display
		self.clock = pygame.time.Clock()
		self.size = size
		self.surf = pygame.display.set_mode(size)
		self.dRects = []
		self.isSet = False
		self.clearAll()
		pygame.display.update()
		# fonts
		if fntName == None:
			self.mFont = pygame.font.Font(None,fntSize)
		else:
			self.mFont = pygame.font.SysFont(fntName,fntSize)
		# title font
		self.tFont = pygame.font.SysFont(fntName,int(fntSize * 2))
	def clearAll(self):		
		self.surf.fill(bgColor)
	def putText(self, s, isp = (4,4,1), icp = (3,3,1), font = None, center=(0,0), color = None):
		"""
		Draws the text in the screen at predefined position
		isp -- in screen position (NX,NY,i) with i from 1 to NX*NY
		icp -- in cell position (NX,NY,i) with i from 1 to NX*NY
		center = (X,Y) -- determines if centering is needed on particular coordinate
		font -- pygame.font.Font object to be used instead of default self.sFont
		"""
		# Initialization
		dRects = []
		if font == None : font = self.mFont
		if color == None : color = fgColor
		# Full cell size
		cell_f_size = (self.size[X] / isp[X], self.size[Y] / isp[Y])
		# Partial cell size
		cell_p_size = (cell_f_size[X] / icp[X], cell_f_size[Y] / icp[Y])
		# Text position
		x = int(((isp[N]-1) % isp[X]) * cell_f_size[X] + ((icp[N]-1) % icp[X] + 0.5) * cell_p_size[X])
		y0 = y = int(((isp[N]-1) / isp[X]) * cell_f_size[Y] + ((icp[N]-1) / icp[Y] + 0.5) * cell_p_size[Y])
		# Text rendering with respect to selected font
		if type(s) == str:
			text = font.render(s, True, color, bgColor)
			rect = self.surf.blit(text,(x-int(center[X]*text.get_width()/2),y-int(center[Y]*text.get_height()/2)))
			dRects.append(rect)
		elif type(s) == list:
			for i in range(len(s)):
				text = font.render(s[i], True, color, bgColor)
				rect = self.surf.blit(text,(x-int(center[X]*text.get_width()/2),y-int(center[Y]*text.get_height()/2)))
				dRects.append(rect)
				y += text.get_height() * 1.0
		else:
			print >> sys.stderr, "Screen.putText(): unsupported type of text provided"
		# Test cell division
		if False:
			dRects.append(pygame.draw.circle(self.surf, fgColor, (x,y0), 5))
			for i in range(isp[X]-1):
				x = cell_f_size[X] * (i+1)
				dRects.append(pygame.draw.line(self.surf,fgColor,(x,0),(x,self.size[Y])))
			for i in range(isp[Y]-1):
				y = cell_f_size[Y] * (i+1)
				dRects.append(pygame.draw.line(self.surf,fgColor,(0,y),(self.size[X],y)))
			for i in range(icp[X]-1):
				x = cell_p_size[X] * (i+1)
				dRects.append(pygame.draw.line(self.surf,fgColor,(x,0),(x,cell_f_size[Y]),1))
			for i in range(icp[Y]-1):
				y = cell_p_size[Y] * (i+1)
				dRects.append(pygame.draw.line(self.surf,fgColor,(0,y),(cell_f_size[X],y),1))
		# Return the list of "dirty" rectangles
		return dRects
	def setCaption(self, caption):
		pygame.display.set_caption(caption)
	def monUpdate(self, frmData, time):
		# Positions and sizes
		if self.isSet == False:
			self.isSet = True
			self.x0 = self.size[X]			# 1000
			self.x1 = int(self.x0/6)
			self.y0 = self.size[Y]			# 700
			self.y1 = int(self.y0/6)
			self.y2 = int(self.y1/2)
			self.y3 = self.y1 - self.y2
			self.y4 = self.y1 + int(self.y3/2)
			self.f2_pos = (self.x1,self.y4+int(self.mFont.get_height()/2))
			self.f2_size = (self.x0-self.f2_pos[X],self.y0-self.f2_pos[Y])
			self.f1_pos = (0,self.f2_pos[Y])
			self.f1_size = (self.x1,self.f2_size[Y])
			self.cr_size = 75
			self.or_size = 25
		# Grid
		self.dRects.append(pygame.draw.line(self.surf,titleColor,(0,self.y1),(self.x0,self.y1),2))
		self.dRects.append(pygame.draw.line(self.surf,titleColor,(self.x1,self.y1),(self.x1,self.y0),2))
		# Raw data text
		text = self.tFont.render('WiTilt Monitor v1.1', True, titleColor, bgColor)
		self.dRects.append(self.surf.blit(text,(int((self.x0-text.get_width())/2),int((self.y2-text.get_height())/2))))
		text = self.mFont.render('Raw data: ax = %4d, ay = %4d, az = %4d, omega = %4d, time = %-4d' %
			(frmData[RAW][X],frmData[RAW][Y],frmData[RAW][Z],frmData[RAW][R],time), True, fgColor, bgColor)
		self.dRects.append(self.surf.blit(text,(int((self.x0-text.get_width())/2),self.y2 + int((self.y3-text.get_height())/2))))
		# Left pane text
		text = self.mFont.render('Angle: %3d' % (frmData[AL][0]), True, fgColor, bgColor)
		self.dRects.append(self.surf.blit(text,(int((self.x1-text.get_width())/2),self.y4-int((text.get_height())/2))))
		# Right pane text
		text = self.mFont.render('Position: x = % 3.1f, y = % 3.1f, z = % 3.1f' % frmData[P], True, fgColor, bgColor)
		self.dRects.append(self.surf.blit(text,(self.x1+int((self.x0-self.x1-text.get_width())/2),self.y4-int((text.get_height())/2))))
		# Coordinates of origins
		o1_pos = (self.f1_pos[X]+int(self.f1_size[X]/2),self.f1_pos[Y]+int(self.f1_size[Y]/2))
		o2_pos = (self.f2_pos[X]+int(self.f2_size[X]/2),self.f2_pos[Y]+int(self.f2_size[Y]/2))
		# Mark on the left pane
		m1_pos = (o1_pos[X],o1_pos[Y]+int(frmData[P][Z]/2.0*self.f1_size[Y]))
		pygame.draw.circle(self.surf, markColor, m1_pos, int(self.cr_size/2), 2)
		pygame.draw.line(self.surf,markColor,(m1_pos[X]-int(self.cr_size/2),m1_pos[Y]),(m1_pos[X]+int(self.cr_size/2),m1_pos[Y]),2)
		pygame.draw.line(self.surf,markColor,(m1_pos[X],m1_pos[Y]-int(self.cr_size/2)),(m1_pos[X],m1_pos[Y]+int(self.cr_size/2)),2)
		m1_dis = (int(self.cr_size/2*math.cos(frmData[AL][0] * math.pi / 180.0)),int(self.cr_size/2*math.sin(frmData[AL][0] * math.pi / 180.0)))
		pygame.draw.circle(self.surf, markColor, (m1_pos[X]+m1_dis[X],m1_pos[Y]-m1_dis[Y]), 5,2)
		self.dRects.append(pygame.Rect(m1_pos[X]-self.cr_size,m1_pos[Y]-self.cr_size,m1_pos[X]+self.cr_size,m1_pos[Y]+self.cr_size))
		# Mark ion the right pane
		m2_pos = (o2_pos[X]+int(frmData[P][X]/2.0*self.f2_size[X]),o2_pos[Y]+int(frmData[P][Y]/2.0*self.f2_size[Y]))
		self.dRects.append(pygame.draw.circle(self.surf, markColor , m2_pos, 5))
		# Origin marks
		self.dRects.append(pygame.draw.line(self.surf,originColor,(o1_pos[X]-int(self.or_size/2),o1_pos[Y]),(o1_pos[X]+int(self.or_size/2),o1_pos[Y]),1))
		self.dRects.append(pygame.draw.line(self.surf,originColor,(o1_pos[X],o1_pos[Y]-int(self.or_size/2)),(o1_pos[X],o1_pos[Y]+int(self.or_size/2)),1))
		self.dRects.append(pygame.draw.line(self.surf,originColor,(o2_pos[X]-int(self.or_size/2),o2_pos[Y]),(o2_pos[X]+int(self.or_size/2),o2_pos[Y]),1))
		self.dRects.append(pygame.draw.line(self.surf,originColor,(o2_pos[X],o2_pos[Y]-int(self.or_size/2)),(o2_pos[X],o2_pos[Y]+int(self.or_size/2)),1))
		# FPS label
		text = self.mFont.render('fps: %2d' % self.clock.get_fps(), True, originColor, bgColor)
		self.dRects.append(self.surf.blit(text,(self.x0-100,15)))
	def calUpdate(self, cal):
		self.dRects.extend(self.putText('Calibration',isp=(1,3,1),icp=(1,1,1),center=(1,1),font=self.tFont))
		pOut = [
			'X[L] = %1d, X[H] = %1d' % (cal.hash[0],cal.hash[1]),
			'Y[L] = %1d, Y[H] = %1d' % (cal.hash[2],cal.hash[3]),
			'Z[L] = %1d, Z[H] = %1d' % (cal.hash[4],cal.hash[5])
		]
		self.dRects.extend(self.putText(pOut,isp=(1,5,2),icp=(1,1,1),center=(1,1),font=self.tFont))
		self.dRects.extend(self.putText(cal.msg,isp=(1,3,3),icp=(1,1,1),center=(1,1),font=self.tFont,color=cal.getColor()))
	def reDraw(self):
		# Update the frame if necessary
		if len(self.dRects):
			# Update display
			pygame.display.update(self.dRects)
			# Join dirty rectangles
			temp = self.dRects[0].unionall(self.dRects[1:])
			self.dRects = []
			self.dRects.append(temp)
		# Clear the surface
		self.clearAll()
		# ... and wait the next frame
		self.clock.tick(fps)


