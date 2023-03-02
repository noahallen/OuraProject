import clean as cl
import image
import os
import time
import generateGraph as gg
from datetime import datetime, timedelta

def update():
    cl.clean(1)
    path = gg.generateLineGraph()
    image.showImage(path)


while 1:
    print("Running update: ")
    update()

    dt = datetime.now() + timedelta(hours=1)

    while datetime.now() < dt:
        time.sleep(60)

