import paho.mqtt.client as mqtt
import time
import threading

HOST = "iot.eclipse.org"
PORT = 1883

class Controller:
    def __init__(self):
        self.client = None

    def client_loop(self):
        # client_id = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        self.client = mqtt.Client(client_id="PC233", clean_session=True)
        self.client.connect(HOST, PORT, 60)
        self.client.publish('sync', '\x00\x07test.txtimport main\nprint(\'haha\')', qos=0)
        # self.client.loop_forever()


if __name__ == '__main__':
    c = Controller()
    c.client_loop()