import clean as cl
import image
import os
import time
import generateGraph as gg
from datetime import datetime, timedelta

def update(dateTime):
    gg.storeToNAS()
    cl.clean(3)
    image.showImage(gg.generateLineGraph())


while 1:
    try:
        update(datetime.now().date())
        dt = datetime.now() + timedelta(hours=24)
        while datetime.now() < dt:
            time.sleep(60)
    except:
        continue

