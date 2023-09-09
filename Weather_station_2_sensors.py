from ISStreamer.Streamer import Streamer
import time
import board

# DHT22 sensor library
import adafruit_dht

#pH Sensor libraries
import busio
import sys
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# --------- User Settings ---------
SENSOR_LOCATION_NAME = "Trial Room"
BUCKET_NAME = ":partly_sunny: Weather Station"
BUCKET_KEY = "test"
ACCESS_KEY = "ist_tW5YA1Fl3QQJeBrEnFSPMHoj5lkPL-A1"

#MINUTES_BETWEEN_READS = 1
METRIC_UNITS = True
# ---------------------------------
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

dhtSensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)
streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)

def read_voltage(channel):
    while True:
        buf = list()
        
        for i in range(10): # Take 10 samples
            buf.append(channel.voltage)
        buf.sort() # Sort samples and discard highest and lowest
        buf = buf[2:-2]
        avg = (sum(map(float,buf))/6) # Get average value from remaining 6
        pH = (round((round(avg,2)*-5.6)+21.555,2))

        #print(round((round(avg,2)*-5.6)+21.555,2))
        #print(round(avg,2), 'V')
        return pH
        time.sleep(2)
        
channel = AnalogIn(ads, ADS.P0)

while True:
        try:
                humidity = dhtSensor.humidity
                temp_c = dhtSensor.temperature
                pH = read_voltage(channel)
                
        except RuntimeError:
                print("RuntimeError, trying again...")
                continue
              
        if METRIC_UNITS:
                streamer.log(SENSOR_LOCATION_NAME + " Temperature(C)", temp_c)
                print("Temperature: {}*C   Humidity: {}%   pH:  {}".format(temp_c, humidity, pH))
                time.sleep(3)
        else:
                temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
                print("Temperature: {}*C".format(temp_c))
                streamer.log(SENSOR_LOCATION_NAME + " Temperature(F)", temp_f)
        humidity = format(humidity,".2f")
        pH = format(pH, ".3f")
        streamer.log(SENSOR_LOCATION_NAME + " Humidity(%)", humidity)
        streamer.log(SENSOR_LOCATION_NAME + " pH", pH)
        streamer.flush()
        time.sleep(5)
        #time.sleep(60*MINUTES_BETWEEN_READS)
