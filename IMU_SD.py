# -*- advanced -*-

import time
import uos
import _thread

from m5stack import lcd, buttonA, buttonB, buttonC
import network
from machine import I2C
from alib.mpu6050 import MPU6050


class Main:

	def __init__(self):
		self.DNAME_ROOT = 'imu'
		self.FNAME_FRONT = 'IMU_'
		self.PATH_LOG = './log_IMU.txt'
		self.FLAG_SD = 0
		self.FLAG_END = 0
		self.SIZE_BUF = 100

		self.i2c = I2C(sda=21, scl=22, speed=400000)
		self.fname_save = None
		self.dataBuf = []
		self.n = 0
		self.counter = 0
		self.period = 20

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
			no = int(newestFileName[4:8])
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

	# def __th_sdcard(self):
	# 	while self.FLAG_END == 0:
	# 		bufLen = len(self.dataBuf)
	# 		if bufLen > 10:
	# 			ts = time.time()
	# 			dataBuf_inner = self.dataBuf[:bufLen]
	# 			del(self.dataBuf[:bufLen])
	# 			strBuf = ''
	# 			for dl in dataBuf_inner:
	# 				strBuf += '%f,%f,%f,%f,%f,%f,%f\n' % tuple(dl)
	# 			with open('/sd/'+self.DNAME_ROOT+'/'+self.fname_save, 'a') as o:
	# 				o.write(strBuf)
	# 			print('Write to SD card. (%d items, %f s)' % (bufLen, time.time()-ts))
	# 		else:
	# 			# print('Waiting...')
	# 			time.sleep_ms(self.period)


	# def __th_display(self):
	# 	if self.FLAG_END == 0:
	# 		# lcd.rect(0,0,320,210, lcd.BLACK, lcd.BLACK)
	# 		# lcd.setCursor(0,0)
	# 		# lcd.font(lcd.FONT_DefaultSmall)
	# 		println(self.strBuf)
	# 	return 0

	def imu_record(self):
		
		try:
			imu = MPU6050(self.i2c)
		except:
			print('I2C Error.')
			self.i2c.deinit()
			return -1

		# th_dh = _thread.start_new_thread('toSD', self.__th_sdcard, ())

		while not buttonB.isPressed():
			if self.FLAG_END == 1:
				break
			acc = imu.acceleration
			gyro = imu.gyro
			
			self.dataBuf.append((time.time(), )+acc+gyro)
			# '%f,%f,%f,%f,%f,%f,%f\n' % ((time.time(), )+acc+gyro)
			
			self.n += 1
			
			time.sleep_ms(self.period)

		self.FLAG_END = 1
		self.i2c.deinit()
		lcd.println('Writing...')

		with open('/sd/'+self.DNAME_ROOT+'/'+self.fname_save, 'a') as o:
			for ds in self.dataBuf:
				o.write('%f,%f,%f,%f,%f,%f,%f\n' % ds)
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

		self.imu_record()


if __name__ == '__main__':
	Main.run()