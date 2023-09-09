#module imports
import machine, onewire, ds18x20, time
import os
import network
#import secrets
import ubinascii
import ussl as ssl
import ntptime
from umqtt.simple import MQTTClient

#configuring your Wifi SSID and password
ssid = "@_R3mo"
password = "password"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140) # this will disable powersave mode
wlan.connect(ssid, password)

# checking connection status
max_wait = 10
while max_wait >0:
    if wlan.status()<0 or wlan.status()>=3:
        break
    max_wait -=1
    print('waiting for connection...')
    time.sleep(1)
    
# handling connection error
if wlan.status() !=3:
    raise RuntimeError('wifi connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' +status[0])

# MQTT client and broker constants
MQTT_CLIENT_KEY = "insert your key"
MQTT_CLIENT_CERT = "insert certification"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

MQTT_BROKER = "insert broker"
MQTT_BROKER_CA ="insert .pem file"

# MQTT topic constant
MQTT_TEMP_TOPIC = "insert IOT device topic"



# initializing data input pin
ds_pin = machine.Pin(16)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))



# Reading PEM files
def read_pem(file):
    with open(file,'r') as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])
        
        return ubinascii.a2b_base64(base64_text)
    
# call back function to handle received MQTT messages
def on_mqtt_msg(topic,msg):
    #convert topic and message from bytes to string
    topic_str = topic.decode()
    msg_str = msg.decode()
    print(f"RX: {topic_str}\n\t{msg__str}")
    
# callback function to periodically send MQTT ping messages to broker
#def
# Read data in private key, certificate and root CA files
key = read_pem(MQTT_CLIENT_KEY)
cert = read_pem(MQTT_CLIENT_CERT)
ca = read_pem(MQTT_BROKER_CA)

# callback function 

client = MQTTClient( MQTT_CLIENT_ID,
                     MQTT_BROKER,
                      keepalive = 60,
                        ssl = True,
                        ssl_params = {
                            "key":key,
                            "cert":cert,
                            "server_hostname":MQTT_BROKER,
                            "cert_reqs":ssl.CERT_REQUIRED,
                            "cadata":ca,
                            },
                         )
client.connect()
#client.subscribe(MQTT_TEMP_TOPIC)
print('Connected to MQTT Broker: ' + MQTT_BROKER)



#Reading sensor data
roms = ds_sensor.scan()
print('Temperature from ds18x20 device')

while True:
    
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        tnum = round(ds_sensor.read_temp(rom))
        print(tnum, "Celsius")
        tnum_str = str(tnum)
        #publish as mqtt payload
        client.publish(MQTT_TEMP_TOPIC,tnum_str)
        
    time.sleep(3)
