from flask import Flask, request, Response
from flask_cors import CORS
import RPi.GPIO as GPIO
import time, math, struct, random, sys
from pathlib import Path
from luma.core.virtual import viewport
from luma.core.render import canvas
from PIL import ImageFont, Image, ImageDraw
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from random import randint, gauss, randrange
from luma.core.sprite_system import framerate_regulator, spritesheet


app = Flask(__name__)
CORS(app)

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, width=128, height=32)

color_r = 0
color_g = 0
color_b = 0

rgb_busy = False
oled_busy = False

blurb = """


   Episode IV:
   A NEW HOPE

It is a period of
civil war. Rebel
spaceships, striking
from a hidden base,
have won their first
victory against the
evil Galactic Empire.

During the battle,
Rebel spies managed
to steal secret plans
to the Empire's ulti-
mate weapon, the
DEATH STAR, an armor-
ed space station with
enough power to des-
troy an entire planet.

Pursued by the
Empire's sinister
agents, Princess Leia
races home aboard her
starship, custodian
of the stolen plans
that can save her
people and restore
freedom to the
galaxy....
"""

def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)

font = make_font("ProggyTiny.ttf", 30)

@app.route('/starwars', methods=['GET'])
def process_sw_scroll():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    return star_wars_scroll() 

@app.route('/matrix', methods=['GET'])
def process_activate_matrix():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    return activate_matrix() 

@app.route('/snow', methods=['GET'])
def process_snow():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    return make_it_snow()

@app.route('/invaders', methods=['GET'])
def process_invaders():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    return play_invaders()

@app.route('/stars', methods=['GET'])
def process_stars():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    return into_the_stars()

@app.route('/runner', methods=['GET'])
def process_runner():
    if oled_busy:
        return Response("Device is busy", status=503, mimetype='application/json')
    return activate_runner()

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

def activate_matrix():
    global oled_busy
    oled_busy = True
    wrd_rgb = [
        (154, 173, 154),
        (0, 255, 0),
        (0, 235, 0),
        (0, 220, 0),
        (0, 185, 0),
        (0, 165, 0),
        (0, 128, 0),
        (0, 0, 0),
        (154, 173, 154),
        (0, 145, 0),
        (0, 125, 0),
        (0, 100, 0),
        (0, 80, 0),
        (0, 60, 0),
        (0, 40, 0),
        (0, 0, 0)
    ]

    clock = 0
    blue_pilled_population = []
    max_population = device.width * 8
    regulator = framerate_regulator(fps=10)

    def increase_population():
        blue_pilled_population.append([randint(0, device.width), 0, gauss(1.2, 0.6)])

    timeout_start = time.time()
    while time.time() < timeout_start + 7:
        clock += 1
        with regulator:
            with canvas(device, dither=True) as draw:
                for person in blue_pilled_population:
                    x, y, speed = person
                    for rgb in wrd_rgb:
                        if 0 <= y < device.height:
                            draw.point((x, y), fill=rgb)
                        y -= 1
                    person[1] += speed

        if clock % 5 == 0 or clock % 3 == 0:
            increase_population()

        while len(blue_pilled_population) > max_population:
            blue_pilled_population.pop(0)
    device.clear()
    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')

def star_wars_scroll():
    global oled_busy
    oled_busy = True
    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'starwars.png'))
    logo = Image.open(img_path)

    virtual = viewport(device, width=device.width, height=768)

    for _ in range(2):
        with canvas(virtual) as draw:
            draw.text((0, 0), "A long time ago", fill="white")
            draw.text((0, 12), "in a galaxy far", fill="white")
            draw.text((0, 24), "far away....", fill="white")

    time.sleep(5)

    for _ in range(2):
        with canvas(virtual) as draw:
            draw.bitmap((20, 0), logo, fill="white")
            for i, line in enumerate(blurb.split("\n")):
                draw.text((0, 40 + (i * 12)), text=line, fill="white")

    time.sleep(2)

    for y in range(450):
        virtual.set_position((0, y))
        time.sleep(0.008)

    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')

def into_the_stars():
    global oled_busy
    oled_busy = True
    def init_stars(num_stars, max_depth):
        stars = []
        for i in range(num_stars):
            star = [randrange(-25, 25), randrange(-25, 25), randrange(1, max_depth)]
            stars.append(star)
        return stars
    def move_and_draw_stars(stars, max_depth):
        origin_x = device.width // 2
        origin_y = device.height // 2

        with canvas(device) as draw:
            for star in stars:
                star[2] -= 0.19
                if star[2] <= 0:
                    star[0] = randrange(-25, 25)
                    star[1] = randrange(-25, 25)
                    star[2] = max_depth

                k = 128.0 / star[2]
                x = int(star[0] * k + origin_x)
                y = int(star[1] * k + origin_y)
                if 0 <= x < device.width and 0 <= y < device.height:
                    size = (1 - float(star[2]) / max_depth) * 4
                    if (device.mode == "RGB"):
                        shade = (int(100 + (1 - float(star[2]) / max_depth) * 155),) * 3
                    else:
                        shade = "white"
                    draw.rectangle((x, y, x + size, y + size), fill=shade)
    max_depth = 32
    stars = init_stars(512, max_depth)
    timeout_start = time.time()
    while time.time() < timeout_start + 7:
        move_and_draw_stars(stars, max_depth)
    device.clear()
    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')

def play_invaders():
    global oled_busy
    oled_busy = True

    arrow = [0x04, 0x02, 0x01, 0x02, 0x04]
    alien1 = [0x4C, 0x1A, 0xB6, 0x5F, 0x5F, 0xB6, 0x1A, 0x4C]
    alien2 = [0x18, 0xFD, 0xA6, 0x3C, 0x3C, 0xA6, 0xFD, 0x18]
    alien3 = [0xFC, 0x98, 0x35, 0x7E, 0x7E, 0x35, 0x98, 0xFC]
    ARMY_SIZE_ROWS = 2
    ARMY_SIZE_COLS = 6

    class bullet(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.alive = False

        def render(self, draw):
            if self.alive:
                draw.line((self.x, self.y, self.x, self.y + 2), fill="white")

        def reset(self, x, y):
            self.x = x
            self.y = y
            self.alive = True
            return

        def update(self, direction):
            if self.alive:
                self.y = self.y + (direction * 4)
                if self.y < 10:
                    self.alive = False
    
    class player(object):
        def __init__(self):
            self.x = 48
            self.y = 54
            self.bullets = [bullet(0, 0) for _ in range(4)]

        def render(self, draw):
            for i in range(len(arrow)):
                line = arrow[i]
                for j in range(3):
                    if line & 0x1:
                        draw.point((self.x - 2 + i, self.y + j), fill="white")
                    line >>= 1

            for bullet in self.bullets:
                bullet.render(draw)

        def update(self, direction):
            t = self.x + (direction * 2)
            if t > 4 and t < 92:
                self.x = t
            for bullet in self.bullets:
                bullet.update(-1)

        def shoot(self):
            for bullet in self.bullets:
                if not bullet.alive:
                    bullet.reset(self.x, self.y)
                    break
    
    class invader(object):
        def __init__(self, minx, maxx, x, y):
            self.x = x
            self.y = y
            self._direction = 1
            self.alive = True
            self.score = 10
            self._minx = minx
            self._maxx = maxx
            return

        def render(self, draw):
            if self.alive:
                for i in range(len(alien2)):
                    line = alien2[i]
                    for j in range(8):
                        if line & 0x1:
                            draw.point((self.x - 4 + i, self.y - 4 + j), "green")
                        line >>= 1

        def update(self):
            invaded = False
            if self.alive:
                t = self.x + self._direction
                if t > self._minx and t < self._maxx:
                    self.x = self.x + self._direction
                else:
                    self._direction = self._direction * -1
                    self.y = self.y + 2
                    if self.y > 44:
                        invaded = True
            return invaded
    
    class army(object):
        def __init__(self):
            self.invaded = False
            self.invaders = []
            for i in range(ARMY_SIZE_ROWS):
                for j in range(ARMY_SIZE_COLS):
                    minx = 4 + (j * 12)
                    maxx = 30 + (j * 12)
                    x = 4 + (j * 12)
                    y = 14 + (i * 12)
                    self.invaders.append(invader(minx, maxx, x, y))

        def render(self, draw):
            for invader in self.invaders:
                invader.render(draw)

        def update(self, bullets):
            for invader in self.invaders:
                if invader.update():
                    self.invaded = True

            for invader in self.invaders:
                if invader.alive:
                    for bullet in bullets:
                        if bullet.alive:
                            t = (invader.x - bullet.x) * (invader.x - bullet.x) + (invader.y - bullet.y) * (invader.y - bullet.y)
                            # if point is in circle
                            if t < 25:  # 5 * 5 = r * r
                                invader.alive = False
                                bullet.alive = False

        def size(self):
            size = 0
            for invader in self.invaders:
                if invader.alive:
                    size += 1
            return size

        def score(self):
            score = 0
            for invader in self.invaders:
                if not invader.alive:
                    score += invader.score
            return score
    
    def ai_logic_shoot(army, plyr):
        for invader in army.invaders:
            if invader.alive:
                if plyr.x > (invader.x - 2) and plyr.x < (invader.x + 2):
                    if random.random() < 0.75:
                        plyr.shoot()
                        return

    def ai_logic_move(army, plyr, rows):
        for i in rows:
            invader = army.invaders[i]
            if invader.alive:
                if plyr.x < invader.x:
                    plyr.update(1)
                    return
                elif plyr.x > invader.x:
                    plyr.update(-1)
                    return
            i += 1

    if device.width < 96 or device.height < 64:
        raise ValueError("Unsupported mode: {0}x{1}".format(device.width, device.height))

    regulator = framerate_regulator()
    plyr = player()
    army = army()
    rows = random.sample(range(12), 12)

    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'splash.bmp'))
    splash = Image.open(img_path) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)


    # Double buffering in pygame?
    device.display(splash)
    device.display(splash)

    time.sleep(3)
    device.clear()

    while not army.invaded and army.size() > 0:
        with regulator:
            with canvas(device) as draw:
                draw.line((0, 61, 95, 61), fill="white")
                draw.line((0, 63, 95, 63), fill="white")

                ai_logic_shoot(army, plyr)
                ai_logic_move(army, plyr, rows)

                army.update(plyr.bullets)

                army.render(draw)
                plyr.render(draw)

                draw.text((8, 0), text="Score: {0}".format(army.score()), fill="blue")

    # Double buffering in pygame?
    for i in range(2):
        with canvas(device) as draw:
            if army.size() == 0:
                draw.text((27, 28), text="Victory", fill="blue")
            else:
                draw.text((30, 28), text="Defeat", fill="red")

    time.sleep(5)


    device.clear()
    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')


def activate_runner():
    global oled_busy
    oled_busy = True

    data = {
        'image': str(Path(__file__).resolve().parent.joinpath('images', 'runner.png')),
        'frames': {
            'width': 64,
            'height': 67,
            'regX': 0,
            'regY': 2
        },
        'animations': {
            'run-right': {
                'frames': range(19, 9, -1),
                'next': "run-right",
            },
            'run-left': {
                'frames': range(0, 10),
                'next': "run-left"
            }
        }
    }

    regulator = framerate_regulator()
    sheet = spritesheet(**data)
    runner = sheet.animate('run-right')
    x = -sheet.frames.width
    dx = 3
    num_iterations = 125

    while num_iterations > 0:
        with regulator:
            num_iterations -= 1

            background = Image.new(device.mode, device.size, "white")
            background.paste(next(runner), (x, 0))
            device.display(background)
            x += dx

            if x >= device.width:
                runner = sheet.animate('run-left')
                dx = -dx

            if x <= -sheet.frames.width:
                runner = sheet.animate('run-right')
                dx = -dx
    device.clear()
    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')


def make_it_snow():
    global oled_busy
    oled_busy = True
    def snow():
        data = [random.randint(0, 0xFFFFFF)
                for _ in range(device.width * device.height)]
        packed = struct.pack('i' * len(data), *data)
        background = Image.frombytes("RGBA", device.size, packed)

        return background.convert(device.mode)
    images = [snow() for _ in range(20)]
    timeout_start = time.time()
    while time.time() < timeout_start + 7:
        random.shuffle(images)
        for background in images:
            device.display(background)
    device.clear()
    oled_busy = False
    return Response("Successful", status=201, mimetype='application/json')

def display_message(message):
    global oled_busy
    oled_busy = True
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