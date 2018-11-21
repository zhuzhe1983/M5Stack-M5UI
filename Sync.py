def main():
	import uos
	import json
	import time
	import _thread

	import network
	from m5stack import lcd, buttonA
	from microWebSrv import MicroWebSrv
	from micropython import const

	def wifiCheck():
		sta_if = network.WLAN(network.STA_IF)
		if sta_if.active() == False:
			sta_if.active(True)
			wifi = json.load(open('/flash/etc/wlan.json', 'r'))
			ssid = wifi['wifi']['ssid']
			pwd = wifi['wifi']['password']
			sta_if.connect(ssid, pwd)
			while sta_if.ifconfig()[0] == '0.0.0.0':
				time.sleep(.5)

			lcd.println('Connect to WLAN.')


	def __acceptWebSocketCallback(webSocket, httpClient) :
		print("WS ACCEPT")
		webSocket.SendText(json.dumps(['login', 'SyncSyncSync']))
		webSocket.RecvTextCallback = __recvTextCallback
		# webSocket.RecvBinaryCallback = self.__recvBinaryCallback
		# webSocket.ClosedCallback = self.__closedCallback

	def __recvTextCallback(webSocket, msg):
		msg = eval(msg)
		# ['command', 'parameter']
		cmd = msg[0]
		para = msg[1]
		print('Receive command: %s' % cmd)
		if cmd == 'ls':
			webSocket.SendText(json.dumps(['ls', uos.listdir()]))
		elif cmd == 'cd':
			uos.chdir(para)
			webSocket.SendText(json.dumps(['cd', uos.listdir()]))
		elif cmd == 'get':
			with open(para, 'r') as o:
				webSocket.SendText(json.dumps(['get', o.read()]))
		elif cmd == 'post':
			with open(para, 'w') as o:
				o.write(msg[2])
			webSocket.SendText(json.dumps(['post', 1]))

	
	wifiCheck()
	ws = MicroWebSrv(port=8000)
	ws.MaxWebSocketRecvLen = 256
	# ws.WebSocketThreaded = False
	ws.AcceptWebSocketCallback = __acceptWebSocketCallback
	ws.Start(threaded=False)

if __name__ == '__main__':
	main()