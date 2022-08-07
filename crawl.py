#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# PYTHON_ARGCOMPLETE_OK

import time, math
from pathlib import Path
from luma.core.virtual import viewport
from luma.core.render import canvas
from PIL import ImageFont
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c

serial = i2c(port=1, address=0x3C)

def make_font(name, size):
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', name))
    return ImageFont.truetype(font_path, size)

font = make_font("ProggyTiny.ttf", 30)

# message = "Hi there!"
# message = "I am the queen of France, I love to dance in my pants.  The quick brown fox jumps over the lazy godd"
message = "I love tacos.  They are so tasty!  YUMMMMM!!!"

def main():

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


if __name__ == "__main__":
    try:
        device = ssd1306(serial, width=128, height=32)
        main()
    except KeyboardInterrupt:
        pass
