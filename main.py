import uos
import sys
import time
from m5stack import lcd, buttonA, buttonB, buttonC
import network
import time
import _thread

# Files in sysPy will not be shown in app list
fsys = set(['main.py', 'boot.py', 'cache.py'])

PATH_CACHE = './cache.py'
FLAG_FOREGROUND = True

def eventCls():
	pass

def flushCache():
	with open(PATH_CACHE, 'w') as o:
		o.write('')

def styleInit():
	lcd.setColor(lcd.WHITE)
	lcd.font(lcd.FONT_Ubuntu, transparent=True, fixedwidth=False)

def sysInit():
	import uos
	try:
		uos.mountsd()
	except:
		lcd.print('Cannot mount SD card!')


class UIPainter:
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

	def alert(self, text):
		lcd.rect(0, 0, 320, 240, lcd.DARKGREY, lcd.DARKGREY)
		lcd.println(text, lcd.CENTER, color=lcd.RED)
		lcd.println('Long press \"A\" to exit', lcd.CENTER, color=lcd.BLACK)
		while not buttonA.isPressed():
			time.sleep(1)

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
		if 'sd' in uos.listdir('/'):
			return 1
		else:
			return 0

	# def ftpStatus(self):
	# 	status = network.ftp.status()
	# 	if status[0] == -1:
	# 		return 0
	# 	else:
	# 		return 1

	def __th_statusMonitor(self):
		ip = UIPainter()
		while (FLAG_FOREGROUND):
			if self.wifiStatus() == 1:
				ip.wifi(0, 2, 20, lcd.DARKGREY)
			elif self.wifiStatus() == 2:
				ip.wifi(0, 2, 20)
			if self.sdStatus():
				ip.text(30, 5, 'SD')
			# if self.ftpStatus():
			# 	ip.text(60, 5, 'FTP')
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
		self.index = 0					# Initial choice
		self.MIOP = 11					# Max Index in One Page
		self.currentPage = 1
		self.upleft = (0, 24)
		self.downright = (320, 204)
		# self.__drawBackground()
		self.refresh(selections)
		buttonA.wasPressed(self.pressUp)
		buttonB.wasPressed(self.pressDown)
		buttonC.wasPressed(self.fileSelected)
		
	def pressUp(self):
		if self.index > 0:
			self.index -= 1
		else:
			self.index = len(self.selections) - 1
		self.__guiUpdate()

	def pressDown(self):
		if self.index < len(self.selections):
			self.index += 1
		else:
			self.index = 0
		self.__guiUpdate()

	def __drawBackground(self):
		lcd.rect(self.upleft[0],
			self.upleft[1],
			self.downright[0]-self.upleft[0],
			self.downright[1]-self.upleft[1],
			lcd.BLACK,
			lcd.BLACK)

	def __drawNaviBar(self, currentPage):
		h_bar = self.downright[1]-self.upleft[1]
		h_lever = int(h_bar / int(len(self.selections) / self.MIOP + 1))
		lcd.rect(308,
			self.upleft[1],
			self.downright[0]-self.upleft[0],
			h_bar,
			lcd.WHITE,
			lcd.WHITE)
		lcd.rect(308,
			self.upleft[1] + h_lever * (currentPage-1),
			self.downright[0]-self.upleft[0],
			h_lever,
			lcd.WHITE,
			lcd.DARKGREY)

	def __guiUpdate(self):
		lcd.setCursor(self.upleft[0]+1, self.upleft[1]+1)

		cp = int(self.index / self.MIOP) + 1	# Current page
		if self.currentPage != cp:				# Which means that it is time to flip over
			self.currentPage = cp
			self.__drawBackground()
			self.__drawNaviBar(cp)

		sru = (cp - 1) * self.MIOP
		if len(self.selections) - sru >= self.MIOP:
			srd = sru + self.MIOP
		else:
			srd = len(self.selections)
		for i in range(sru, srd):
			if i == self.index:
				lcd.println(self.selections[i], color=lcd.GREEN)
			else:
				lcd.println(self.selections[i], color=lcd.WHITE)

	def refresh(self, newSelections):
		self.selections = newSelections
		self.index = 0
		self.__drawBackground()
		if len(self.selections) > self.MIOP:
			self.__drawNaviBar(1)
		self.__guiUpdate()

class FileList(Menu):
	def __init__(self, root):
		files = list(set(uos.listdir(root)) - fsys)
		if uos.getcwd() != '/':
			files.insert(0, '/')
		uos.chdir(root)
		super().__init__(files)

	def pyRun(self, fname):
		global FLAG_FOREGROUND
		FLAG_FOREGROUND = False
		buttonA.wasPressed(eventCls)
		buttonB.wasPressed(eventCls)
		buttonC.wasPressed(eventCls)
		print('Launch %s...' %  uos.getcwd()+'/'+fname)
		lcd.setCursor(self.upleft[0]+1, self.upleft[1]+1)
		lcd.println('Now loading...')
		with open(fname, 'r') as o:
			code = o.read()
		with open(PATH_CACHE, 'w') as o:
			o.write(code)
		if 'cache' in sys.modules.keys():
			del sys.modules['cache']
		lcd.clear()
		import cache
		cache.main()
		uos.remove(PATH_CACHE)

	def fileSelected(self):
		try:
			uos.chdir(self.selections[self.index])
			newFileList = list(set(uos.listdir()) - fsys)
			if uos.getcwd() != '/':
				newFileList.insert(0, '/')
			# self.index = 0
			# self.__drawBackground()
			# self.guiUpdate()
			self.refresh(newFileList)
		except:
			if self.selections[self.index][-3:] == '.py':
				self.pyRun(self.selections[self.index])
				welcome(uos.getcwd())

def welcome(root):
	global FLAG_FOREGROUND
	FLAG_FOREGROUND = True
	lcd.clear()
	styleInit()
	fw = Framework('M5UI')
	fw.drawFrame()
	frontpage = FileList(root)
	# frontpage.guiUpdate()

def main():
	flushCache()
	sysInit()
	welcome('/')

if __name__ == '__main__':
	main()