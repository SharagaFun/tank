from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
import RPi.GPIO as GPIO          
from time import sleep
import os
from threading import Thread
import statistics
from smbus import SMBus
from huawei_lte_api.Client import Client
import netifaces
from huawei_lte_api.Connection import Connection
import gpsd
import wifi as wsd

blockpercentage = False
oldpercentage = 0
hconnection = None
hclient = None
lgpsd = gpsd.connect()


def is_interface_up(interface):
	try:
		addr = netifaces.ifaddresses(interface)
	except:
		return False
	return netifaces.AF_INET in addr
	
	
def gps():
	global lgpsd
	while True:
		try:
			packet = gpsd.get_current()
			if packet.mode >= 2:
				socketio.emit('gps', {'sattelites': str(packet.sats), 'latitude': str(packet.lat), 'longitude': str(packet.lon), 'speed': str(packet.hspeed)})
			else:
				socketio.emit('gps', {'sattelites': str(packet.sats), 'latitude': 'N/A', 'longitude': 'N/A', 'speed': 'N/A'})
		except:
			socketio.emit('gps', {'sattelites': '0'})
		sleep(1)

def thread_function():
	global blockpercentage, oldpercentage
	while True:
		values = list()
		for i in range(80):
			bus.write_byte(DEV_ADDR, adc_channel)
			bus.read_byte(DEV_ADDR)
			bus.read_byte(DEV_ADDR)
			values.append (bus.read_byte(DEV_ADDR))
			sleep(0.1)
		voltage = round(min(values)*0.0956132, 3)
		percent = round((voltage-12.2)/(15-12.2)*100)
		percent = percent if percent <=100 else 100
		percent = percent if oldpercentage-percent <=4 else oldpercentage-3
		percent = percent if percent >=0 else 0
		percent = oldpercentage if blockpercentage else percent
		oldpercentage = percent
		socketio.emit('battery', {'voltage': "{:.1f}".format(voltage), 'percentage': str(percent)})

def huawei():
	global hconnection, hclient
	while True:
		if is_interface_up('eth1'):
			try:
				if hconnection is not None and hclient is not None:
						hsignal = hclient.monitoring.status()['SignalIcon']
						hnettype = hclient.device.information()['workmode']
						socketio.emit('modem', {'signal': hsignal, 'nettype': hnettype})
				else:
					hconnection = Connection('http://192.168.8.1/')
					hclient = Client(hconnection)
			except:
				socketio.emit('modem', {'signal': '0', 'nettype': 'N/A'})
		else:
			socketio.emit('modem', {'signal': '0', 'nettype': 'N/A'})
		sleep(1)
		
def wifi():
	while True:
		wifisignal = os.popen("awk 'NR==3 {printf($3*10/7)}' /proc/net/wireless").read()
		if (wifisignal):
			socketio.emit('wifi', {'signal': wifisignal+"%"})
		else:
			socketio.emit('wifi', {'signal': "0%"})
		sleep(1)

DEV_ADDR = 0x48
adc_channel = 0b1000010
dac_channel = 0b1000000
bus = SMBus(1)

in1 = 22
in2 = 27
in3 = 23
in4 = 24
en1 = 17
en = 25
temp1=1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setup(en1,GPIO.OUT)
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)
p1=GPIO.PWM(en1,1000)
p.start(25)
p1.start(25)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@socketio.on('message')
def handle_message(message):
    global blockpercentage
    print('received message: ' + message)
    p.ChangeDutyCycle(50)
    p1.ChangeDutyCycle(50)
    blockpercentage = True
    if message == 'w':
    	GPIO.output(in1,GPIO.HIGH)
    	GPIO.output(in2,GPIO.LOW)
    	GPIO.output(in3,GPIO.HIGH)
    	GPIO.output(in4,GPIO.LOW)
    elif message == '/':
    	GPIO.output(in1,GPIO.LOW)
    	GPIO.output(in2,GPIO.LOW)
    	GPIO.output(in3,GPIO.LOW)
    	GPIO.output(in4,GPIO.LOW)
    	sleep(5)
    	blockpercentage = False
    elif message == 'a':
    	GPIO.output(in1,GPIO.HIGH)
    	GPIO.output(in2,GPIO.LOW)
    	GPIO.output(in3,GPIO.LOW)
    	GPIO.output(in4,GPIO.HIGH)
    elif message == 'd':
    	GPIO.output(in1,GPIO.LOW)
    	GPIO.output(in2,GPIO.HIGH)
    	GPIO.output(in3,GPIO.HIGH)
    	GPIO.output(in4,GPIO.LOW)
    if message == 's':
    	GPIO.output(in1,GPIO.LOW)
    	GPIO.output(in2,GPIO.HIGH)
    	GPIO.output(in3,GPIO.LOW)
    	GPIO.output(in4,GPIO.HIGH)
    if message == 'scan':
    	networks = list()
    	[networks.append({'ssid':i.ssid.encode("latin1").decode("unicode-escape").encode("latin1").decode('utf-8'), 'signal':i.signal, 'encrypted':i.encrypted}) for i in list(wsd.Cell.all('wlan0'))]
    	socketio.emit('scan', networks)
    	
@socketio.on('right')
def handle_message(message):
    global blockpercentage
    blockpercentage = True
    coord = int(message)
    if coord>50:
    	coord=50
    if coord<-50:
    	coord=-50
    p1.ChangeDutyCycle(abs(coord))
    if coord>0:
    	GPIO.output(in1,GPIO.HIGH)
    	GPIO.output(in2,GPIO.LOW)
    elif coord<0:
    	GPIO.output(in1,GPIO.LOW)
    	GPIO.output(in2,GPIO.HIGH)
    else:
    	GPIO.output(in1,GPIO.LOW)
    	GPIO.output(in2,GPIO.LOW)
    	sleep(5)
    	blockpercentage = False

@socketio.on('left')
def handle_message(message):
    global blockpercentage
    blockpercentage = True
    coord = int(message)
    if coord>50:
    	coord=50
    if coord<-50:
    	coord=-50
    p.ChangeDutyCycle(abs(coord))
    if coord>0:
    	GPIO.output(in3,GPIO.HIGH)
    	GPIO.output(in4,GPIO.LOW)
    elif coord<0:
    	GPIO.output(in3,GPIO.LOW)
    	GPIO.output(in4,GPIO.HIGH)
    else:
    	GPIO.output(in3,GPIO.LOW)
    	GPIO.output(in4,GPIO.LOW)
    	sleep(5)
    	blockpercentage = False
    
if __name__ == '__main__':
    vthread = Thread(target=thread_function)
    vthread.daemon = True
    vthread.start()
    hthread = Thread(target=huawei)
    hthread.daemon = True
    hthread.start()
    wthread = Thread(target=wifi)
    wthread.daemon = True
    wthread.start()
    gthread = Thread(target=gps)
    gthread.daemon = True
    gthread.start()
    socketio.run(app,  host='0.0.0.0', port=5001)

