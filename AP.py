def main():
	from m5stack import lcd, buttonA
	import network
	import json
	import time

	try:
		lcd.setCursor(0,0)
		ap_if = network.WLAN(network.AP_IF)
		ap_if.config(essid='M5UI-181122', channel=6)
		ap_if.active(True)

		lcd.println('AP launched.')
		lcd.println('Gate: 192.168.4.1')

		while not buttonA.isPressed():
			time.sleep(.2)
	except:
		pass

if __name__ == '__main__':
	main()