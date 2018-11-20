# -*- advanced -*-

import time
import uos
import _thread

from m5stack import lcd, buttonA, buttonB, buttonC
import network
import binascii

class Main:

	def __init__(self):
		self.DNAME_ROOT = 'wifi_analyzer'
		self.FNAME_FRONT = 'WA_'
		self.PATH_LOG = '/flash/log/log_WiFiAnalyzeMT.txt'
		self.FLAG_WRITTING = 0
		self.FLAG_END = 0

		self.fname_save = None
		self.strBuf = ''
		self.wlan = network.WLAN(network.STA_IF)
		self.wlan.active(True)

	def drawNaviButton(self, strA='START', strB='STOP', strC='EXIT'):
		lcd.text(40, 215, strA, lcd.WHITE)
		lcd.text(135, 215, strB, lcd.WHITE)
		lcd.text(240, 215, strC, lcd.WHITE)

	def fnameGen(self):
		currentFileList = list(filter(lambda x: self.FNAME_FRONT in x, uos.listdir('/sd/'+self.DNAME_ROOT)))
		currentFileList = list(map(lambda x: x.upper(), currentFileList))
		if self.FNAME_FRONT + '0001.CSV' not in currentFileList:
			return self.FNAME_FRONT+'0001.CSV'
		else:
			currentFileList.sort()
			newestFileName = currentFileList[-1]
			no = int(newestFileName[3:7])
			return self.FNAME_FRONT + '%s.CSV' % (('%4d' % (no + 1)).replace(' ', '0'))

	def fileCheck(self):
		try:
			uos.stat('/sd')
			lcd.println('SD card has already been mounted.')
		except:
			try:
				uos.mountsd()
				lcd.println('SD card is mounted.')
			except:
				lcd.println('No SD card is found.')
				return -1
		try:
			sdFiles = uos.listdir('/sd')
			if self.DNAME_ROOT not in sdFiles:
				uos.mkdir('/sd/' + self.DNAME_ROOT)
				lcd.println('mkdir /sd/%s/' % self.DNAME_ROOT)
		except:
			lcd.println('The SD card is not writable.')
			return -2
		return 0

	def __th_writter(self):
		if self.FLAG_END == 0:
			self.FLAG_WRITTING = 1
			with open('/sd/'+self.DNAME_ROOT+'/'+self.fname_save, 'a') as o:
				o.write(self.strBuf)
			self.FLAG_WRITTING = 0
		return 0

	def __th_display(self, apresults):
		if self.FLAG_END == 0:
			print(self.strBuf+'---------------------')
			lcd.rect(0,0,320,210, lcd.BLACK, lcd.BLACK)
			lcd.setCursor(0,0)
			lcd.font(lcd.FONT_DefaultSmall)
			
			if len(apresults) < 15:
				i = 0
				for apresult in apresults:
					resstr = '%02d, ch: %02d, rs: %d, %s\n' % (i+1, apresult[2], apresult[3], apresult[0].decode())
					lcd.print(resstr,color = lcd.WHITE)
					i = i + 1
			else:
				for i in range(0,15):
					apresult = apresults[i]
					resstr = '%02d, ch: %02d, rs: %d, %s\n' % (i+1, apresult[2], apresult[3], apresult[0].decode())
					lcd.print(resstr,color = lcd.WHITE)
		return 0

	def scanner(self):
		ts = time.time()
		while not buttonB.isPressed():
			if self.FLAG_END == 1:
				break
			aps = self.wlan.scan()
			if self.FLAG_WRITTING == 0:
				self.strBuf = ''
				for ap in aps:
					# (ssid, bssid, primary_chan, rssi, auth_mode, auth_mode_string, hidden)
					self.strBuf += '%f,%s,%s,%d,%s\n' % (time.time()-ts, (binascii.hexlify(ap[1])).decode(), ap[0].decode(), ap[3], ap[2])
				
				th1 = _thread.start_new_thread('sd', self.__th_writter, ())
				th2 = _thread.start_new_thread('display', self.__th_display, (aps, ))
			else:
				with open(self.PATH_LOG, 'w') as o:
					o.write('[%f] Write failed.' % time.time()-ts)
		self.FLAG_END = 1
		return 0

# ------------------ MAIN ------------------
	def run(self):
		if self.fileCheck() < 0:
			return -1
		self.drawNaviButton()
		
		lcd.setCursor(0,0)
		lcd.println('Press START to start')
		while not buttonA.isPressed():
			if buttonC.isPressed():
				return 0
			time.sleep(.5)

		self.fname_save = self.fnameGen()
		lcd.println('Record into %s' % self.fname_save)

		self.scanner()


if __name__ == '__main__':
	Main.run()