def main():
	import network
	from m5stack import lcd, buttonA, buttonC
	import time
	import _thread

	# def __th_ftp():
	# 	network.ftp.start({user="micro", password="python", buffsize=1024, timeout=300})

	def ftp_status():
		fs = network.ftp.status()
		lcd.println('Server IP: %s' % fs[4])
		lcd.println('Server status: %s' % fs[2])
		lcd.println('Data status: %s' % fs[3])

	try:
		lcd.setCursor(0, 0)

		if network.ftp.status()[0] == -1:
			lcd.println('FTP is not opened.')
			while True:
				if buttonA.isPressed():
					_thread.start_new_thread('ftp', network.ftp.start, (), {'user': "micro", 'password': "python", 'buffsize': 1024, 'timeout': 300})
					ftp_status()
				elif buttonC.isPressed():
					break
				time.sleep(.2)

		else:
			ftp_status()
			while True:
				if buttonA.isPressed():
					network.ftp.stop()
					ftp_status()
				elif buttonC.isPressed():
					break
				time.sleep(.2)
	except:
		pass
