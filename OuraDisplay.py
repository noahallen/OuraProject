import clean as cl
import image
import os
import time
import generateGraph as gg
from datetime import datetime, timedelta

def update():
    cl.clean(3)
    try:
        gg.storeToNAS("daily_sleep")
        gg.storeToNAS("daily_activity")
        gg.storeToNAS("daily_readiness")
        gg.storeToNAS("heartrate")
        gg.storeToNAS("sleep")
        gg.storeToNAS("workout")
        gg.storeToNAS("tag")
        gg.storeToNAS("session")
        
        image.showImage(gg.generateSleepLineGraph())
    except Exception as e: 
        image.showText(e)

while 1:
    try:
        time.sleep(60)
        update()
        dt = datetime.now() + timedelta(hours=5)
        while datetime.now() < dt:
            time.sleep(60)
    except:
        pass

