def main():
	import time
	import uos

	from m5stack import lcd, buttonA, buttonB, buttonC
	import network
	import binascii

	DNAME_ROOT = 'wifi_analyzer'


	def drawNaviButton(strA='START', strB='STOP', strC='EXIT'):
		lcd.text(40, 215, strA, lcd.WHITE)
		lcd.text(135, 215, strB, lcd.WHITE)
		lcd.text(240, 215, strC, lcd.WHITE)

	def fnameGen():
		currentFileList = list(filter(lambda x: 'WA_' in x, uos.listdir('/sd/'+DNAME_ROOT)))
		currentFileList = list(map(lambda x: x.lower(), currentFileList))
		if 'wa_0001.csv' not in currentFileList:
			return 'WA_0001.csv'
		else:
			currentFileList.sort()
			newestFileName = currentFileList[-1]
			no = int(newestFileName[3:7])
			return 'WA_%s.csv' % (('%4d' % (no + 1)).replace(' ', '0'))

	def resdisplay(apresults, n, time):
		lcd.rect(0, 0, 320, 24, lcd.BLUE, lcd.BLUE)
		lcd.font(lcd.FONT_Ubuntu, transparent=True)
		lcd.text(0, 2, 'N_AP:%d N_SCAN:%d TIME:%d' % (len(apresults), n, time), lcd.WHITE)
		lcd.rect(0,24,320,186, lcd.BLACK, lcd.BLACK)
		lcd.setCursor(0,24)
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

	try:
		uos.stat('/sd')
	except:
		try:
			uos.mountsd()
		except:
			lcd.println('No SD card is found.')
			return -1

	try:
		sdFiles = uos.listdir('/sd')
		if DNAME_ROOT not in sdFiles:
			uos.mkdir('/sd/' + DNAME_ROOT)
	except:
		lcd.println('The SD card is not writable.')
		return -2

	try:
		drawNaviButton()
		lcd.setCursor(0,0)

		lcd.println('Press START to start')
		while not buttonA.isPressed():
			time.sleep(.5)
			if buttonC.isPressed():
				return 0
			
		wlan = network.WLAN(network.STA_IF)
		wlan.active(True)

		fname = fnameGen()
		lcd.println('Recording into %s...' % fname)
		
		ts = time.time()
		n = 0
		while not buttonB.isPressed():
			buf = ''
			aps = wlan.scan()
			n += 1
			te = time.time()-ts
			for ap in aps:
				# (ssid, bssid, primary_chan, rssi, auth_mode, auth_mode_string, hidden)
				mac = (binascii.hexlify(ap[1])).decode()
				mac = ':'.join([mac[:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:12]])
				buf += '%.3f,%s,%s,%d,%s\n' % (te, mac, ap[0].decode(), ap[3], ap[2])
			print(buf+'---------------------')
			resdisplay(aps, n, int(te))

			with open('/sd/'+DNAME_ROOT+'/'+fname, 'a') as o:
				o.write(buf)
		lcd.println('Exit.')

	except:
		print('Exit since error.')
		pass

if __name__ == '__main__':
	main()