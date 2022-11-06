#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time

from inky.auto import auto
from PIL import Image

def clean(cycles):
    print("""Inky pHAT: Clean

    Displays solid blocks of red, black, and white to clean the Inky pHAT
    display of any ghosting.

    """)

    inky_display = auto(ask_user=True, verbose=True)

    colours = (inky_display.RED, inky_display.BLACK, inky_display.WHITE)
    colour_names = (inky_display.colour, "black", "white")

    # Create a new canvas to draw on

    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))

    # Loop through the specified number of cycles and completely
    # fill the display with each colour in turn.

    for i in range(cycles):
        print("Cleaning cycle %i\n" % (i + 1))
        for j, c in enumerate(colours):
            print("- updating with %s" % colour_names[j])
            inky_display.set_border(c)
            for x in range(inky_display.WIDTH):
                for y in range(inky_display.HEIGHT):
                    img.putpixel((x, y), c)
            inky_display.set_image(img)
            inky_display.show()
            time.sleep(1)
        print("\n")

    print("Cleaning complete!")
