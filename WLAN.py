def main():
	from m5stack import lcd, buttonA
	import network
	import json
	import time

	try:
		isConnected = False
		lcd.setCursor(0,0)
		sta_if = network.WLAN(network.STA_IF)
		if sta_if.active() == False:
			lcd.println('Connecting...')
			sta_if.active(True)
			wifi = json.load(open('/flash/etc/wlan.json', 'r'))
			ssid = wifi['wifi']['ssid']
			pwd = wifi['wifi']['password']
			sta_if.connect(ssid, pwd)
			# time.sleep(3)

		while not buttonA.isPressed():
			ni = sta_if.ifconfig()
			if ni[0] == '0.0.0.0':
				time.sleep(1)
			else:
				isConnected = True
				lcd.println('ip: %s' % ni[0])
				lcd.println('mask: %s' % ni[1])
				lcd.println('gate: %s' % ni[2])
				lcd.println('dns: %s' % ni[3])
				break

		if isConnected:
			while not buttonA.isPressed():
				time.sleep(.2)
	except:
		pass