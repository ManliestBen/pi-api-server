from flask import Flask, request, Response
from flask_cors import CORS
import RPi.GPIO as GPIO
import time


app = Flask(__name__)
CORS(app)

color_r = 0
color_g = 0
color_b = 0

@app.route('/rgb', methods=['POST'])
def process_json():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        r = int(request.json["r"])
        g =int(request.json["g"])
        b = int(request.json["b"])
        return set_rgb(r, g, b)
    else:
        return 'Content-Type not supported!'

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def set_rgb(r, g, b):
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
    return Response("Successful", status=201, mimetype='application/json')