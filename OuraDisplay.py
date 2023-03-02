import clean as cl
import image
import os
import time
import generateGraph as gg
from datetime import datetime, timedelta

def update():
    cl.clean(2)
    image.showImage(gg.generateLineGraph())


while 1:
    try:
        update()
        dt = datetime.now() + timedelta(hours=4)
        while datetime.now() < dt:
            time.sleep(60)
    except:
        continue

