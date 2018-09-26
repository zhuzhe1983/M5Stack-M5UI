def main():
	import network
	from m5stack import lcd, buttonA
	import time

	try:
		while not buttonA.isPressed():
			lcd.setCursor(0, 0)
			network.ftp.start(user="micro", password="python", buffsize=1024, timeout=300)
			fs = network.ftp.status()
			lcd.println('Server IP: %s' % fs[4])
			lcd.println('Server status: %s' % fs[2])
			lcd.println('Data status: %s' % fs[3])
			time.sleep(1)
		network.ftp.stop()
	except:
		pass
