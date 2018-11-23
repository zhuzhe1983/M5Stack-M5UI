import uos
import sys
import time
import network
import time

from m5stack import lcd, buttonA, buttonB, buttonC
from micropython import const
import _thread

# Files in fsys will not be shown in app list
fsys = set(['main.py', 'boot.py', 'cache.py', 'alib'])

PATH_CACHE = './cache.py'
FLAG_FOREGROUND = True

def eventCls():
	pass

def styleInit():
	lcd.setColor(lcd.WHITE)
	lcd.font(lcd.FONT_Ubuntu, transparent=True, fixedwidth=False)

def sysInit():
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

class Framework:
	def __init__(self, title):
		print('Framework %s ready' % title)
		self.W = const(320)
		self.H = const(240)
		self.h_banner = const(24)
		self.h_bottom = const(36)
		self.title = title

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

	def __th_statusMonitor(self):
		ip = UIPainter()
		if self.sdStatus():
			ip.text(30, 5, 'SD')
		while (FLAG_FOREGROUND):
			wifi = self.wifiStatus()
			# sd = self.sdStatus()
			if wifi == 1:
				ip.wifi(0, 2, 20, lcd.DARKGREY)
			elif wifi == 2:
				ip.wifi(0, 2, 20)
			# if self.ftpStatus():
			# 	ip.text(60, 5, 'FTP')
			time.sleep(3)

	def drawBanner(self):
		lcd.rect(0, 0, self.W, self.h_banner, lcd.BLUE, lcd.BLUE)
		lcd.setCursor(self.W - lcd.textWidth(self.title) - 5, 5)
		lcd.print(self.title)
		th_m = _thread.start_new_thread('monitor', self.__th_statusMonitor, ())

	def drawNaviButton(self, strA='UP', strB='DOWN', strC='SELECT'):
		lcd.rect(0, self.H - self.h_bottom, self.W, self.h_bottom, lcd.DARKGREY, lcd.DARKGREY)
		lcd.line(int(self.W / 3), self.H - self.h_bottom, int(self.W / 3), self.H, lcd.WHITE)
		lcd.line(int(2 * self.W / 3), self.H - self.h_bottom, int(2 * self.W / 3), self.H, lcd.WHITE)
		lcd.text(40, 215, strA, lcd.WHITE)
		lcd.text(135, 215, strB, lcd.WHITE)
		lcd.text(240, 215, strC, lcd.WHITE)

class Menu():
	def __init__(self, selections):
		self.selections = selections
		self.index = 0					# Initial choice
		self.MIOP = const(11)			# Max Index in One Page
		self.currentPage = 1
		self.upleft = (0, 24)
		self.downright = (320, 204)
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
			lcd.WHITE,
			lcd.WHITE)

	def __drawNaviBar(self, currentPage):
		h_bar = self.downright[1]-self.upleft[1] #204-24 = 180
		h_lever = int(h_bar / int(len(self.selections) / self.MIOP + 1))
		lcd.rect(308,
			self.upleft[1],
			self.downright[0]-self.upleft[0],
			h_bar,
			lcd.BLUE,
			lcd.BLUE)
		lcd.rect(308,
			self.upleft[1] + h_lever * (currentPage-1),
			self.downright[0]-self.upleft[0],
			h_lever,
			lcd.BLUE,
			lcd.DARKGREY)

	def __drawNaviBarcp1(self):
		h_bar = self.downright[1]-self.upleft[1] #204-24 = 180
		lcd.rect(308,
			self.upleft[1],
			self.downright[0]-self.upleft[0],
			h_bar,
			lcd.BLUE,
			lcd.BLUE)
		lcd.rect(308,
			24,
			self.downright[0]-self.upleft[0],
			170,
			lcd.BLUE,
			lcd.DARKGREY)

	def __guiUpdate(self):
		lcd.setCursor(self.upleft[0]+1, self.upleft[1]+1)

		cp = int(self.index / self.MIOP) + 1	# Current page

		if len(self.selections) <= 11:
			self.__drawNaviBarcp1()
			cp = 1
		
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
			yaxis = i-(cp-1)*10-(cp-1)
			if i == self.index:
				lcd.rect(0,24+yaxis*16,308,16,lcd.MAGENTA,lcd.MAGENTA)
				lcd.println(self.selections[i], color=lcd.BLACK)
			else:
				lcd.rect(0,24+yaxis*16,308,16,lcd.WHITE,lcd.WHITE)
				lcd.println(self.selections[i], color=lcd.BLACK)

	def refresh(self, newSelections):
		buttonA.wasPressed(self.pressUp)
		buttonB.wasPressed(self.pressDown)
		buttonC.wasPressed(self.fileSelected)
		self.selections = newSelections
		self.index = 0
		self.__drawBackground()
		if len(self.selections) > self.MIOP:
			self.__drawNaviBar(1)
		self.__guiUpdate()

class FileList(Menu):
	def __init__(self, root):
		self.framework = Framework('M5UI')
		self.root_current = root
		uos.chdir(root)
		super().__init__(self.__path2fileList(root))
		self.ui_refresh()

	def __path2fileList(self, path):
		fl = list(set(uos.listdir(path)) - fsys)
		fl.sort()
		if path != '/':
			fl.insert(0, '/')
		return fl

	def __ext(self, fname, exts):
		if '.' not in fname:
			return False
		elif fname.split('.')[-1].lower() in exts:
			return True
		else:
			return False

	def ui_refresh(self):
		global FLAG_FOREGROUND
		FLAG_FOREGROUND = True
		styleInit()
		self.framework.drawBanner()
		self.framework.drawNaviButton()

		self.refresh(self.__path2fileList(self.root_current))
		print('*** Welcome to M5UI ***')
		print('Start from: %s' % self.root_current)

	def app_pyLauncher(self, fname):
		print('Launch %s...' %  uos.getcwd()+'/'+fname)
		lcd.setCursor(self.upleft[0]+1, self.upleft[1]+1)
		lcd.println('Now loading...')
		with open(fname, 'rb') as o:
			code = o.read()
		with open(PATH_CACHE, 'wb') as o:
			o.write(code)
		if 'cache' in sys.modules.keys():
			del sys.modules['cache']
		lcd.clear()
		import cache
		if code[:18] == b'# -*- advanced -*-':
			print('-*- This is an advanced program -*-')
			cache.Main().run()
		else:
			cache.main()
		uos.remove(PATH_CACHE)

	def app_txtReader(self, fname):
		lcd.clear()
		f = Framework('txtReader')
		f.drawNaviButton(strC='EXIT')
		lcd.font(lcd.FONT_DefaultSmall, transparent=False, fixedwidth=True)
		idx = 0
		idx_s = [0]
		page = 0
		while True:
			letter_current_page = 0
			lcd.setCursor(0, 0)
			lcd.rect(0, 0, 320, 240 - f.h_bottom, lcd.BLACK, lcd.BLACK)
			with open(fname, 'r') as o:
				o.seek(idx)
				flag_end = False

				for row in range(20):
					for col in range(29):
						c = o.read(1)
						if not c:
							lcd.println('--- END ---')
							flag_end = True
							break
						if c != '\n':
							lcd.print(c)
							letter_current_page += 1
						else:
							letter_current_page += 1
							break
					lcd.print('\n')
					if flag_end:
						break
			while True:
				time.sleep(0.1)
				if buttonA.isPressed():
					if page != 0:
						page -= 1
						del(idx_s[-1])
						idx = idx_s[-1]
						break
				elif buttonB.isPressed():
					if c:
						idx += letter_current_page
						idx_s.append(idx)
						page += 1
						break
				elif buttonC.isPressed():
					return 0

	def fileSelected(self):
		if '.' in self.selections[self.index]:
			global FLAG_FOREGROUND
			FLAG_FOREGROUND = False
			buttonA.wasPressed(eventCls)
			buttonB.wasPressed(eventCls)
			buttonC.wasPressed(eventCls)
			if self.__ext(self.selections[self.index], ['py']):
				self.app_pyLauncher(self.selections[self.index])
			elif self.__ext(self.selections[self.index], ['csv', 'json', 'txt']):
				self.app_txtReader(self.selections[self.index])
			self.ui_refresh()
		else:
			try:
				uos.chdir(self.selections[self.index])
				self.root_current = uos.getcwd()
				self.refresh(self.__path2fileList(uos.getcwd()))
				print('Enter folder: %s' % self.root_current)
			except:
				print('*** Unknown file type ***')
				pass

def main():
	sysInit()
	styleInit()
	FileList('/')

if __name__ == '__main__':
	main()