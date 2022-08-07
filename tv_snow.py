#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Example image-blitting.
"""
import time
import struct
import random
from PIL import Image, ImageDraw
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c

serial = i2c(port=1, address=0x3C)


device = ssd1306(serial, width=128, height=32)


def snow():
    data = [random.randint(0, 0xFFFFFF)
            for _ in range(device.width * device.height)]
    packed = struct.pack('i' * len(data), *data)
    background = Image.frombytes("RGBA", device.size, packed)

    return background.convert(device.mode)


def main():
    images = [snow() for _ in range(20)]
    timeout_start = time.time()
    while time.time() < timeout_start + 7:
        random.shuffle(images)
        for background in images:
            device.display(background)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
