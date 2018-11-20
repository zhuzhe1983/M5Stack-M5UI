# -*- advanced -*-

import json
import os
import struct
import time

from m5stack import lcd, buttonA
import network

class Main:

	def __init__(self):
		sta_if = network.WLAN(network.STA_IF)
		if sta_if.active() == False:
			sta_if.active(True)
			wifi = json.load(open('/flash/etc/wlan.json', 'r'))
			ssid = wifi['wifi']['ssid']
			pwd = wifi['wifi']['password']
			sta_if.connect(ssid, pwd)

		self.m = None
		self.msg = None

	def mqtt(self):
		def __recv(msg):
			self.msg = msg[2]
			print('[%s] Data arrived from topic: %s. (%d)' % (msg[0], msg[1], len(msg[2])))
			self.exec(msg[2])

		self.m = network.mqtt("sync", "mqtt://192.168.31.245", port=1883, data_cb=__recv)
		self.m.start()
		self.m.subscribe(b'sync')

	def exec(self, cmd):
		# +----+-----+--------------+
		# |type|len_1|payload1,2,...|
		# +----+-----+--------------+
		head = struct.unpack('b', cmd[0])[0]
		len_1 = struct.unpack('b', cmd[1])[0]
		payload1 = cmd[2:2+len_1]
		payload2 = cmd[2+len_1:]

		if head == 0x00:
			print('Update %s' % payload1.decode())
			with open(payload1.decode(), 'wb') as o:
				o.write(payload2)

	def run(self):
		self.mqtt()
		while not buttonA.isPressed():
			time.sleep(.2)

if __name__ == '__main__':
	Main.run()
