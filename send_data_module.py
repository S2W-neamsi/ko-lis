from cmath import nan
import time
import requests
from time import sleep
import os
import Adafruit_SSD1306
import Adafruit_DHT
import RPi.GPIO as GPIO
from ubidots import ApiClient

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

led1 = 5
led2 = 6
led3 = 13

PIN_DHT = 4
PIN_RELAY = 27

# Raspberry Pi pin configuration:
RST = 24
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# First define some constants to allow easy resizing of shapes.
padding = 2
shape_width = 20
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = padding

# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(led3, GPIO.OUT)

GPIO.setmode(GPIO.BCM)

TOKEN = "BBFF-QGpKKAZQYQQRVveUVCjr87iCxzNMJP"  # Put your TOKEN here
DEVICE_LABEL = "riil"  # Put your device label here
VARIABLE_LABEL_1 = "temperature"  # Put your first variable label here
VARIABLE_LABEL_2 = "humidity"  # Put your second variable label here
VARIABLE_LABEL_3 = "relay"
VARIABLE_LABEL_4 = "mie"
VARIABLE_LABEL_5 = "sayurbening"


def led(id, on):
    if (id == 1):
        if (on):
            GPIO.output(led1, GPIO.HIGH)
        else:
            GPIO.output(led1, GPIO.LOW)

    elif (id == 2):
        if (on):
            GPIO.output(led2, GPIO.HIGH)
        else:
            GPIO.output(led2, GPIO.LOW)

    elif (id == 3):
        if (on):
            GPIO.output(led3, GPIO.HIGH)
        else:
            GPIO.output(led3, GPIO.LOW)


def lcdBegin():
    # Initialize library.
    disp.begin()


def clearlcd():
    disp.clear()


def lcdOn():
    disp.image(image)
    disp.display()


def lcdWrite(line1, line2, line3):
    # Draw some shapes.
    # Load default font.
    font = ImageFont.load_default()
    font18 = ImageFont.truetype('Minecraftia.ttf', 18)
    font20 = ImageFont.truetype('Minecraftia.ttf', 20)
    font24 = ImageFont.truetype('Minecraftia.ttf', 24)

    # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php
    # font = ImageFont.truetype('Minecraftia.ttf', 8)

    # Write two lines of text.
    draw.text((x, top), line1, font=font, fill=255)
    draw.text((x, top + 18), line2, font=font20, fill=255)
    draw.text((x, top + 22 + 22), line3, font=font, fill=255)

    # Display image.
    # disp.image(image)
    # disp.display()


def lcd():
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Load default font.
    font = ImageFont.load_default()
    font18 = ImageFont.truetype('Minecraftia.ttf', 18)
    font20 = ImageFont.truetype('Minecraftia.ttf', 20)
    font24 = ImageFont.truetype('Minecraftia.ttf', 24)

    # Sensor should be set to Adafruit_DHT.DHT11,
    # Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
    sensor = Adafruit_DHT.DHT11

    # Example using a Beaglebone Black with DHT sensor
    # connected to pin P8_11.
    pin = 4

    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).

    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        str_temp = ' {0:0.2f} *C '.format(temperature)
        str_hum = ' {0:0.2f} %'.format(humidity)
        print('Temp={0:0.1f}*C'.format(temperature))
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        disp.clear()
        disp.display()
        draw.text((3, top), 'Temperature', font=font, fill=255)
        draw.text((x, top + 16), str_temp, font=font18, fill=255)

        # disp.image(image)
        # disp.display()

        if temperature >= 30:
            led(2, True)
        else:
            led(2, False)
    else:
        print('Failed to get reading. Try again!')


def temperature():
    DHT_SENSOR = Adafruit_DHT.DHT11

    humidity = None
    temperature = None

    while temperature is None and humidity is None:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, PIN_DHT)

    return temperature


def humidity():
    DHT_SENSOR = Adafruit_DHT.DHT11

    temperature = None
    humidity = None

    while temperature is None and humidity is None:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, PIN_DHT)

    return humidity


def relay():
    # api setup
    api = ApiClient(token='BBFF-G7bHXCDx1yl8uspx6CqH9ng1jla1Ea')
    VARIABLE_LABEL_3 = api.get_variable("63006b41a0d47d000d429582")
    status = VARIABLE_LABEL_3.get_values(1)

    # status off/on
    return status[0]['value']


def mie():
    # api setup
    api = ApiClient(token='BBFF-G7bHXCDx1yl8uspx6CqH9ng1jla1Ea')
    VARIABLE_LABEL_4 = api.get_variable("6301dc504a33092efc606d96")
    mie = VARIABLE_LABEL_4.get_values(1)

    # status off/on
    return mie[0]['value']


def sayurbening():
    # api setup
    api = ApiClient(token='BBFF-G7bHXCDx1yl8uspx6CqH9ng1jla1Ea')
    VARIABLE_LABEL_5 = api.get_variable("631303bb223fb0342e80faba")
    valsayur = VARIABLE_LABEL_5.get_values(1)

    # status off/on
    return valsayur[0]['value']


masakan = None


def controlRelay():
    global masakan
    _relay = relay()
    _mie = mie()
    _sayurbening = sayurbening()

    if _relay or _mie or _sayurbening:
        GPIO.setup(PIN_RELAY, GPIO.OUT)
        GPIO.output(PIN_RELAY, GPIO.HIGH)
        lcd()
        led(3, True)
        if _relay:
            masakan = "relay"
            clearlcd()
            lcdWrite("", "", line3="Kompor menyala")
            print(f"{masakan} menyala")

        if _mie:
            masakan = "mie"
            clearlcd()
            lcdWrite("", "", line3="Memasak mie")
            print(f"{masakan} sedang dimasak")

        if _sayurbening:
            masakan = "sayurbening"
            clearlcd()
            lcdWrite("", "", line3="Memasak sayurbening")
            print(f"{masakan} sedang dimasak")


    else:
        if masakan is not None:
            print(f"{masakan} selesai")
            clearlcd()
            lcdWrite("", f"{masakan} selesai", "")
            masakan = None
            time.sleep(5)
        else:
            clearlcd()
            lcdWrite("", "KO-LIS", "S2W-neamsi")

        GPIO.setup(PIN_RELAY, GPIO.IN)
        led(3, False)
        led(2, False)


def build_payload(variable_1, variable_2):
    # Creates two random values for sending data
    value_1 = temperature()
    value_2 = humidity()

    payload = {variable_1: value_1,
               variable_2: value_2,
               }

    return payload


def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True


def main():
    controlRelay()
    lcdOn()

    payload = build_payload(
        VARIABLE_LABEL_1, VARIABLE_LABEL_2)

    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished")


if __name__ == '__main__':
    led(1, True)  # Nyala led merah
    lcdBegin()
    lcdWrite("", "KO-LIS", "S2W-neamsi")

    try:
        while (True):
            main()
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nProgram Mati")

        led(1, False)
        led(2, False)
        led(3, False)
        clearlcd()
        GPIO.cleanup()