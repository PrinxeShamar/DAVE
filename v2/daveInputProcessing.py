# This runs the primary flow logic of DAVE.
# It captures the prompt via terminal input to avoid 
# processing with an external mic.

from picamera2 import Picamera2
import time
import base64
import io
import numpy as np
from evdev import InputDevice
from select import select
import replicate
import pyaudio
from gtts import gTTS
import wave
import pygame

# Place your Replicate API Key.
client = replicate.Client(api_token="")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={
    "format": "XRGB8888",
    "size": (320, 240)
}))
picam2.start()

chunk = 1024
sample_format = pyaudio.paInt16
channels = 2
fs = 44100

p = pyaudio.PyAudio()
output_stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input_device_index=0,
                output=True)

pygame.mixer.init()

def say(text):
    print("Saying")
    tts = gTTS(text)

    audio_bytes = b''
    for chuck in tts.stream():
        audio_bytes += chuck

    audio_io = io.BytesIO(audio_bytes)

    pygame.mixer.music.load(audio_io)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.01)

def capture():
    print("Capturing")
    image = picam2.capture_image()
    image = image.rotate(180)
    image_io = io.BytesIO()
    image.save(image_io, "PNG")
    image.save("a.png")
    return image_io

def llava(image, prompt):
    print("LLAVA")
    output = client.run(
        "yorickvp/llava-13b:e272157381e2a3bf12df3a8edd1f38d1dbd736bbb7437277c8b34175f8fce358",
        input={"image": image, "prompt": prompt}
    )

    response = ""
    for item in output:
        response += item

    return response

while True:
    prompt = input()
    image = capture()
    response = llava(image, prompt)
    print(response)
    say(response)