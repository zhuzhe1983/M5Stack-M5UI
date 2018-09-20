import os
import sys
import time
from m5stack import lcd, buttonA, buttonB, buttonC
import network
import time
import _thread

# Files in sysPy will not be shown in app list
sysPy = set(['main.py', 'boot.py', 'cache.py'])

flag_isHalt = False

def eventCls():
	pass

def flushCache():
	with open('cache.py', 'w') as o:
		o.write('')

def pyRun(fname):
	buttonA.wasPressed(eventCls)
	buttonB.wasPressed(eventCls)
	buttonC.wasPressed(eventCls)
	lcd.println('Now loading...')
	with open(fname, 'r') as o:
		code = o.read()
	with open('cache.py', 'w') as o:
		o.write(code)
	if 'cache' in sys.modules.keys():
		del sys.modules['cache']
	lcd.clear()
	import cache
	cache.main()
	welcome()


def styleInit():
	lcd.setColor(lcd.WHITE)
	lcd.font(lcd.FONT_Ubuntu, transparent=True, fixedwidth=False)

def sysInit():
	import uos
	try:
		uos.mountsd()
	except:
		lcd.print('Cannot mount SD card!')


class IconPainter:
	def __init__(self):
		pass

	def wifi(self, x, y, size, color=lcd.WHITE):
		lcd.setCursor(x, y)
		lcd.rect(x, int(y+.75*size), int(size*.2), size-int(y+.75*size), color, color)
		lcd.rect(int(x+.4*size), int(y+.5*size), int(size*.2), size-int(y+.5*size), color, color)
		lcd.rect(int(x+.8*size), int(y), int(size*.2), size, color, color)

	def text(self, x, y, txt, color=lcd.WHITE):
		lcd.setCursor(x, y)
		lcd.print(txt)

class Framework():
	def __init__(self, title):
		self.W = 320
		self.H = 240
		self.h_banner = 24
		self.h_bottom = 36
		self.title = title
		# self.foreground = True

	def wifiStatus(self):
		sta_if = network.WLAN(network.STA_IF)
		if sta_if.active() == False:
			return 0
		else:
			ni = sta_if.ifconfig()
			if ni[0] == '0.0.0.0':
				return 1
			else:
				return 2

	def sdStatus(self):
		import uos
		if 'sd' in uos.listdir('/'):
			return 1
		else:
			return 0

	def __th_statusMonitor(self):
		ip = IconPainter()
		while (flag_isHalt == False):
			if self.wifiStatus() == 1:
				ip.wifi(0, 2, 20, lcd.DARKGREY)
			elif self.wifiStatus() == 2:
				ip.wifi(0, 2, 20)
			if self.sdStatus():
				ip.text(30, 5, 'SD')
			time.sleep(1)

	def drawFrame(self):
		lcd.rect(0, 0, self.W, self.h_banner, lcd.BLUE, lcd.BLUE)
		lcd.setCursor(self.W - lcd.textWidth(self.title) - 5, 5)
		lcd.print(self.title)
		lcd.rect(0, self.H - self.h_bottom, self.W, self.h_bottom, lcd.DARKGREY, lcd.DARKGREY)
		lcd.line(int(self.W / 3), self.H - self.h_bottom, int(self.W / 3), self.H, lcd.WHITE)
		lcd.line(int(2 * self.W / 3), self.H - self.h_bottom, int(2 * self.W / 3), self.H, lcd.WHITE)
		lcd.text(40, 215, 'UP', lcd.WHITE)
		lcd.text(135, 215, 'DOWN', lcd.WHITE)
		lcd.text(240, 215, 'SELECT', lcd.WHITE)
		th_m = _thread.start_new_thread('monitor', self.__th_statusMonitor, ())


class Menu():
	def __init__(self, selections):
		self.selections = selections
		self.index = 0
		self.MIOP = 11					# Max Index in One Page
		self.currentPage = 1
		self.upleft = (0, 24)
		self.downright = (320, 204)
		
	def pressUp(self):
		if self.index > 0:
			self.index -= 1
		else:
			self.index = len(self.selections) - 1
		self.update()

	def pressDown(self):
		if self.index < len(self.selections):
			self.index += 1
		else:
			self.index = 0
		self.update()

	def update(self):
		lcd.rect(self.upleft[0],
			self.upleft[1],
			self.downright[0]-self.upleft[0],
			self.downright[1]-self.upleft[1],
			lcd.BLACK,
			lcd.BLACK)
		lcd.setCursor(self.upleft[0]+1, self.upleft[1]+1)

		cp = int(self.index / self.MIOP) + 1	# Current page
		sru = (cp - 1) * self.MIOP + (cp - 1)
		if len(self.selections) - sru >= self.MIOP:
			srd = sru + self.MIOP
		else:
			srd = len(self.selections)
		for i in range(sru, srd):
			if i == self.index:
				lcd.println(self.selections[i], color=lcd.GREEN)
			else:
				lcd.println(self.selections[i], color=lcd.WHITE)

class PyList(Menu):
	def execute(self):
		global flag_isHalt
		flag_isHalt = True
		pyRun(self.selections[self.index])

# class FileList:
# 	def __init__(self):
# 		self.files = list(filter(lambda x: x[-3:] == '.py', os.listdir()))

# 	def execute(self):
# 		pyRun(self.selections[self.index])


def welcome():
	global flag_isHalt
	flag_isHalt = False
	lcd.clear()
	styleInit()
	fw = Framework('M5UI')
	fw.drawFrame()
	execLst = list(filter(lambda x: x[-3:] == '.py', os.listdir()))
	execLst = list(set(execLst) - sysPy)
	frontpage = PyList(execLst)
	frontpage.update()
	buttonA.wasPressed(frontpage.pressUp)
	buttonB.wasPressed(frontpage.pressDown)
	buttonC.wasPressed(frontpage.execute)

def main():
	flushCache()
	sysInit()
	welcome()


if __name__ == '__main__':
	main()