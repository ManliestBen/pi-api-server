from flask import Flask, request, Response
from flask_cors import CORS
import RPi.GPIO as GPIO
import time


app = Flask(__name__)
CORS(app)

color_r = 0
color_g = 0
color_b = 0

@app.route('/post_json', methods=['POST'])
def process_json():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        r = int(request.json["r"])
        g =int(request.json["g"])
        b = int(request.json["b"])
        return run_test(r, g, b)
    else:
        return 'Content-Type not supported!'

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test")
def test():
    return run_test()

def run_test(r, g, b):
    pins = (11,13,15) # R = 11, G = 12, B = 13
    GPIO.setmode(GPIO.BOARD)
    
    def setup():
        global pwmR, pwmG, pwmB
        for i in pins:  # iterate on the RGB pins, initialize each and set to HIGH to turn it off (COMMON ANODE)
            GPIO.setup(i, GPIO.OUT)
            GPIO.output(i, False)
        pwmR = GPIO.PWM(pins[0], 2000)  # set each PWM pin to 2 KHz
        pwmG = GPIO.PWM(pins[1], 2000)
        pwmB = GPIO.PWM(pins[2], 2000)
        pwmR.start(0)   # initially set to 0 duty cycle
        pwmG.start(0)
        pwmB.start(0)
        
    def setColor(r, g, b):  # 0 ~ 100 values since 0 ~ 100 only for duty cycle
        pwmR.ChangeDutyCycle(r)
        pwmG.ChangeDutyCycle(g)
        pwmB.ChangeDutyCycle(b)
        
    def displayColors(r, g, b):
        setColor((r/255)*100, (g/255)*100, (b/255)*100) #   cornflower blue color
        time.sleep(5)   # 1s
        
    def destroy():
        pwmR.stop()
        pwmG.stop()
        pwmB.stop()
        GPIO.cleanup()

    setup()
    displayColors(r, g, b)
    destroy()
    return Response("Successful", status=201, mimetype='application/json')