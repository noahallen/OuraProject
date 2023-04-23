import sys
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto
from font_intuitive import Intuitive

def showImage(fileName):
    inky = auto(ask_user=True, verbose=True)
    saturation = .8

    

    image = Image.open(fileName)
    image=image.rotate(180)
    resizedimage = image.resize(inky.resolution)

    if len(sys.argv) > 2:
        saturation = float(sys.argv[2])

    inky.set_image(resizedimage, saturation=saturation)
    inky.show()


def showText(string):
    intuitive_font = ImageFont.truetype(Intuitive, int(22 * 2))
    inky = auto(ask_user=True, verbose=True)
    saturation = .8

    img = Image.new("P", inky.resolution)
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), string, inky.WHITE, font=intuitive_font)
    img=img.rotate(180)
    resizedimage = img.resize(inky.resolution)

    if len(sys.argv) > 2:
        saturation = float(sys.argv[2])
    inky.set_image(resizedimage, saturation=saturation)
    inky.show()