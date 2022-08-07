from flask import Flask, request, Response
from flask_cors import CORS
import RPi.GPIO as GPIO
import time, math
from pathlib import Path
from luma.core.virtual import viewport
from luma.core.render import canvas
from PIL import ImageFont
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c


app = Flask(__name__)
CORS(app)

serial = i2c(port=1, address=0x3C)

color_r = 0
color_g = 0
color_b = 0

rgb_busy = False
oled_busy = False

def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)

font = make_font("ProggyTiny.ttf", 30)

@app.route('/rgb', methods=['POST'])
def process_json_rgb():
    if rgb_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        r = int(request.json["r"])
        g =int(request.json["g"])
        b = int(request.json["b"])
        return set_rgb(r, g, b)
    else:
        return 'Content-Type not supported!'

@app.route('/message', methods=['POST'])
def process_json_message():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        message = request.json["message"]
        return display_message(message)
    else:
        return 'Content-Type not supported!'

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def display_message(message):
    global oled_busy
    oled_busy = True
    device = ssd1306(serial, width=128, height=32)
    virtual = viewport(device, width=1360, height=768)

    with canvas(virtual) as draw:
        draw.text((0, 12), "New Message!", font=font, fill="white")

    time.sleep(3)

    with canvas(virtual) as draw:
        draw.text((0,12), message, font=font, fill="white")

    time.sleep(2)

    for x in range(int(len(message)*11)):
        virtual.set_position((x, 0))
        time.sleep(0.001)
    
    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')

def set_rgb(r, g, b):
    global rgb_busy
    rgb_busy = True
    pins = (11,13,15) 
    GPIO.setmode(GPIO.BOARD)
    
    def setup():
        global pwmR, pwmG, pwmB
        for i in pins:  
            GPIO.setup(i, GPIO.OUT)
            GPIO.output(i, False)
        pwmR = GPIO.PWM(pins[0], 2000) 
        pwmG = GPIO.PWM(pins[1], 2000)
        pwmB = GPIO.PWM(pins[2], 2000)
        pwmR.start(0) 
        pwmG.start(0)
        pwmB.start(0)
        
    def setColor(r, g, b):  
        pwmR.ChangeDutyCycle(r)
        pwmG.ChangeDutyCycle(g)
        pwmB.ChangeDutyCycle(b)
        
    def displayColors(r, g, b):
        setColor((r/255)*100, (g/255)*100, (b/255)*100) 
        time.sleep(5)  
        
    def destroy():
        pwmR.stop()
        pwmG.stop()
        pwmB.stop()
        GPIO.cleanup()

    setup()
    displayColors(r, g, b)
    destroy()
    rgb_busy = False
    return Response("Successful", status=201, mimetype='application/json')