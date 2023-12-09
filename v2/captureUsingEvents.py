# This file includes setting up an event handler for processing 
# device events. This code example involves using the button press
# of my external headphone device to trigger an image capture.

from picamera2 import Picamera2
import time
import base64
import io
import numpy as np
from evdev import InputDevice
from select import select

dev = InputDevice('/dev/input/event0')

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={
	"format": "XRGB8888",
	"size": (640, 480)
}))
picam2.start()

def capture():
	image = picam2.capture_image()
	image = image.rotate(180)
	image_io = io.BytesIO()
	image.save(image_io, "PNG")
	image.save("a.png")
	base64_image = base64.b64encode(image_io.getvalue()).decode('utf-8')
	return f"data:image/jpeg;base64,{base64_image}"

while True:
   	select([dev], [], [])
	capture()