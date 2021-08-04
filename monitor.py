import argparse
from datetime import datetime
from prometheus_client import start_http_server, Summary, Gauge, Counter
import time
import Adafruit_DHT


DHT_SENSOR = Adafruit_DHT.AM2302
# DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

SENSOR_TIME = Summary('sensor_reading_seconds', 'Time spent waiting for values from sensor')
TEMPERATURE_GAUGE = Gauge('temperature', 'Temperature')
HUMIDITY_GAUGE = Gauge('humidity', 'Humidity')
SENSOR_ERRORS = Counter('sensor_errors', 'Errors reading the sensor')

@SENSOR_TIME.time()
def read_sensor():
    return Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN, 30, 1)

def main_loop(loop_delay):
  while True:
    timestamp = datetime.now().isoformat()
    humidity, temperature = read_sensor()

    if humidity is not None and temperature is not None:
      HUMIDITY_GAUGE.set(humidity)
      TEMPERATURE_GAUGE.set(temperature)
      print(f"{timestamp} Temp: {temperature:.1f}*C  Humidity: {humidity:.1f}%")
    else:
      SENSOR_ERRORS.inc()
      print("Failed to retrieve data from humidity sensor")

    time.sleep(loop_delay)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--metrics-port', default=8000, type=int)
  parser.add_argument('--loop-delay', default=5, type=int)
  args = parser.parse_args()
  start_http_server(args.metrics_port)
  print(f'Started metrics server on :{args.metrics_port}')
  print(f'Reading sensor every {args.loop_delay} seconds')
  main_loop(args.loop_delay)
