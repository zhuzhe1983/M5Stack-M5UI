# -*- advanced -*-
# Since the program uses MPU6050, it can only run on M5Stack Fire

import time
import uos

from m5stack import lcd, buttonA, buttonB, buttonC
from machine import I2C, Timer
from alib.mpu6050 import MPU6050


class Main:

	def __init__(self):
		self.DNAME_ROOT = 'imu'
		self.FNAME_FRONT = 'IMU_'
		self.PATH_LOG = './log_IMU.txt'
		self.FLAG_SD = 0
		self.FLAG_END = 0
		self.SIZE_BUF = 100

		self.fname_save = None
		self.dataBuffer = []
		self.n = 0
		self.counter = 0
		self.period = 20

		self.i2c = None
		self.imu = None
		self.t1 = None
		self.t2 = None

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

	def sd(self):
		lcd.println('Write into SD...')
		with open('/sd/'+self.DNAME_ROOT+'/'+self.fname_save, 'a') as o:
			for ds in self.dataBuffer:
				o.write('%f,%f,%f,%f,%f,%f,%f\n' % ds)
		lcd.println('OK.')
		return 0

	def createTimer(self):
		def __getIMUData(timer):
			if not buttonB.isPressed():
				try:
					self.dataBuffer.append((time.time(), )+self.imu.acceleration+self.imu.gyro)
					self.n += 1
				except:
					print('Terminated.')
			else:
				self.FLAG_END = 1
				self.t1.deinit()
				self.i2c.deinit()
				self.sd()

		self.t1 = Timer(0)
		self.t1.init(period=20, mode=self.t1.PERIODIC, callback=__getIMUData)

	def IMU_Record(self):
		try:
			self.i2c = I2C(sda=21, scl=22, speed=400000)
			self.imu = MPU6050(self.i2c, accel_fs=0b00001000)
		except:
			print('I2C error.')
			self.i2c.deinit()
			return -1
		
		self.createTimer()
		
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
			time.sleep(.2)

		self.fname_save = self.fnameGen()
		lcd.println('Record into %s' % self.fname_save)

		self.IMU_Record()
		return 0
# ------------------------------------------


if __name__ == '__main__':
	Main.run()