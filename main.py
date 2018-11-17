import uos
import sys
import time
from m5stack import lcd, buttonA, buttonB, buttonC
import network
import time
import _thread

# Files in sysPy will not be shown in app list
fsys = set(['main.py', 'boot.py', 'cache.py', 'alib'])

PATH_CACHE = './cache.py'
PATH_TIME = '/flash/etc/timenow.txt'
FLAG_FOREGROUND = True

def eventCls():
	pass

def flushCache():
	with open(PATH_CACHE, 'wb') as o:
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

def sysTime():
	def __timer():
		timenow = 0
		with open(PATH_TIME, 'r') as o:
			timenow = int(o.read())
		while True:
			time.sleep(1)
			timenow += 1
			with open(PATH_TIME, 'w') as o:
				o.write(str(timenow))
	# (16384, 0, 0, 0, 0, 0, 0, 0, 0, 0)
	if uos.stat(PATH_TIME)[6] == 0:
		with open(PATH_TIME, 'w') as o:
			o.write('0')
	th_m = _thread.start_new_thread('timer', __timer, ())


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

	def pyLauncher(self, fname):
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
		try:
			import cache
			if code[:18] == b'# -*- advanced -*-':
				print('-*- This is an advanced program -*-')
				cache.Main().run()
			else:
				cache.main()
		except:
			print('ERR')
			raise
		uos.remove(PATH_CACHE)

	def txtReader(self, fname):
		lcd.clear()
		f = Framework('txtReader')
		f.drawNaviButton(strC='EXIT')
		lcd.font(lcd.FONT_Ubuntu, transparent=False, fixedwidth=True)
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

				for row in range(11):
					for col in range(19):
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
			if self.selections[self.index][-3:] == '.py':
				self.pyLauncher(self.selections[self.index])
			elif self.selections[self.index][-4:].lower() in ['.txt', '.csv'] or self.selections[self.index][-5:].lower() == '.json':
				self.txtReader(self.selections[self.index])
			welcome(uos.getcwd())
		else:
			try:
				uos.chdir(self.selections[self.index])
				newFileList = list(set(uos.listdir()) - fsys)
				if uos.getcwd() != '/':
					newFileList.insert(0, '/')
				self.refresh(newFileList)
			except:
				pass

def welcome(root):
	global FLAG_FOREGROUND
	FLAG_FOREGROUND = True
	lcd.clear()
	styleInit()
	fw = Framework('M5UI')
	fw.drawBanner()
	fw.drawNaviButton()
	frontpage = FileList(root)
	# frontpage.guiUpdate()

def main():
	flushCache()
	# sysTime()
	sysInit()
	welcome('/')

if __name__ == '__main__':
	main()