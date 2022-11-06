
import sys

from PIL import Image, ImageOps

from inky.auto import auto

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
