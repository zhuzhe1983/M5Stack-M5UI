# -*- advanced -*-
import uos
import json
import time

import network
from m5stack import lcd, buttonA
from microWebSrv import MicroWebSrv
from micropython import const

class Main:
	def __init__(self):
		self.ws = MicroWebSrv(port=8000)
		self.post_buffer = []
	
	def wifiCheck(self):
		sta_if = network.WLAN(network.STA_IF)
		ap_if = network.WLAN(network.AP_IF)
		if (sta_if.active() == False and ap_if.active() == False) or sta_if.ifconfig()[0] == '0.0.0.0':
			ap_if = network.WLAN(network.AP_IF)
			ap_if.config(essid='M5UI-181122', channel=6)
			ap_if.active(True)

			lcd.println('Sync is working in AP mode.')
		else:
			if sta_if.ifconfig()[0] == '192.168.4.1':
				lcd.println('Sync is working in AP mode.')
			else:
				lcd.println('Sync is working in WIFI mode.')

	def startServer(self):

		def __acceptWebSocketCallback(webSocket, httpClient) :
			lcd.println('New connection comes.')
			webSocket.SendText(json.dumps(['login', 'SyncSyncSync']))
			webSocket.RecvTextCallback = __recvTextCallback
			# webSocket.RecvBinaryCallback = self.__recvBinaryCallback
			# webSocket.ClosedCallback = self.__closedCallback

		def __recvTextCallback(webSocket, msg):
			msg = eval(msg)
			# ['command', 'parameter']
			cmd = msg[0]
			para = msg[1]
			lcd.println('Receive command: %s' % cmd)
			if True:
				if cmd == 'ls':
					webSocket.SendText(json.dumps(['ls', uos.listdir()]))
				elif cmd == 'cd':
					uos.chdir(para)
					webSocket.SendText(json.dumps(['cd', uos.listdir()]))
				elif cmd == 'get':
					with open(para, 'r') as o:
						webSocket.SendText(json.dumps(['get', o.read()]))
				elif cmd == 'post':
					# post fname.py slice_no string
					self.post_buffer.append(msg[3])
					if msg[2] == -1:
						with open(para, 'w') as o:
							o.write('')
						with open(para, 'a') as o:
							for s in self.post_buffer:
								o.write(s)
						self.post_buffer = []
						webSocket.SendText(json.dumps(['post', 1]))
				elif cmd == 'rm':
					uos.remove(para)
				elif cmd == 'exit':
					webSocket.Close()
					self.ws.Stop()
			else:
				lcd.println('ERR occur.')

		self.wifiCheck()
		# ws.MaxWebSocketRecvLen = 128
		self.ws.WebSocketThreaded = False
		self.ws.AcceptWebSocketCallback = __acceptWebSocketCallback
		self.ws.Start(threaded=False)

	def run(self):
		self.startServer()

if __name__ == '__main__':
	Main().run()