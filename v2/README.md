# DAVE 

## Version 2

DAVE 2.0 was primary the work done after HackRPI into better ways to do audio input, output and image processing.
The resulting file is a semi final version of the most optimal choices for different parts of daves main processing.
Here are some of those results.

## Audio Input Processing

Audio is suprisingly complicated. One half of audio is processing input. Audio input is a stream of bytes with each byte representing the
amplitute at the current time step. This amplitude is how we preceive sound. Modern systems use between 44100 to 44800 frames per second. 
This means that every second the input stream produces 44100 bytes of data. To process audio typically instead of reading or writing each byte as its placed on the stream, we wait for a certain chunk to become available. Ex. 1024 is commonly used as a chunk size. We can read fs / chunk size so in this case 44100 / 1024 and that gives us how many chunks per second. This way we can record audio for a certain amount of time.

Additionally outside of audio processing there are several libraries that can open an input/output stream. However after looking into at the internals of many opensource libraries such as pygame mixer or playsound, they all use the native [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) library which is an interface for calling the portaudio core library which handles sound on many operating systems. To reduce many dependencies, directly using PyAudio was prefered and allowed for direct interfacing with the audio processing system.

Another consideration is the audio input device. Audio devices come in many forms including headphones, earbuds, mini microphones and also many microcontroller components which can be added to a microcontroller or microprocessor. Overall this all depends on the stage and requirements for your system. There is also the consideration of bluetooth vs wired connections.

## Audio Output Processing

Audio Output is the same as audio input. Instead of reading bytes off of the stream, we write to the stream. However there are many considerations to consider when outputing the raw audio bytes to other formats such as mp3 or wav. Wav tends to be a simple format to quickly save data and retrieve it back. It is also one of the accepted format types for transfering audio data across the internet such as HTTP. 

## Text to Speech

Text to Speech plays a critical part in DAVE main functions. To provide a device that can be used by the visual impaired, we need to rely on other senses like hearing. Whenever we receive text responses for example in our image explaination process we need to translate that back to speech. In python there is a go to library which is Google Text To Speech or [GTTS](https://github.com/pndurette/gTTS). GTTS provides exceptional fast runtimes and makes for a very responsive system.

## Speech to Text

### Step 1

There has been significant effort into turning speech to text. There are some python modules that aim to accomplish this task for example SpeechRecognition but sadly miss the mark. For this reason some time was spent into creating a custom audio processor that accomplishes this task. 

The processor works by opening an Audio Input stream as discussed earlier. After reading each chunk calculate the root mean spuare ([RMS](https://en.wikipedia.org/wiki/Root_mean_square)) of the chunk. If the RMS falls below a certain threshold (called the silence threshold) this chunk is considered silent. Every second there is about 43 chunks so even in small brief audio there are guarantee to be chunk segments of silence. To account for this we way for about 20 chunks in a row to be marked as silence (about ~0.5 secs). This can accurately determine when there is silence.

Once you can detect silence we can begin capturing phrases. First we wait for no sound and once there is sound we record until we hit silence again. This is considered a phrase. We can then begin step 2 of Speech to Text.

### Step 2

Once we have a phrase we need to translate this into text. This is very a large possibility of models come into play. For many things in DAVE we try to use many open source technologies and that came into play here where we used the [Whisper](https://openai.com/research/whisper) model from OpenAI. However due to internet and the overhead added from making API calls, some research was done into using local models such as [VOSK](https://alphacephei.com/vosk/). 

In total Speech to Text is another fundamental piece in the puzzle of accessiblity. For assiting the visual impaired we had to rely on other senses such as speech to communicate.

## Computing

In V1, the computing was done from my laptop. To make DAVE both affordable and compact, we had to look into more smaller and smaller forms of computing. 

### Attempt 1

The first attempt was to use a microcontroller. The microcontroller of choose was [Arduino Nano 33 BLE Sense](https://store-usa.arduino.cc/products/arduino-nano-33-ble-sense). However this quickly failed as the RAM and CPU Usage was very small but this was to be exepected from a microcontroller like this. 

### Attempt 2

Secondly after further investigation I needed to switch to a more powerful device. I used a micro processor this time which is essentially a mini computer. The micro processor of choose was the [Raspberry Pi Zero 2W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/). Not only did it come with more RAM, better CPU but the price was also less. It also offered a better programming environment where I got to use python vs writing in low level C code. The code in v2 and all the high level processing is done on the Pi including Audio Input, Output, Text to Speech. The Pi however still does not have enough memory for some of the more complex tasks like Speech to Text and Image Processing.

## Image Processing

In Attempt 1, the camera of choice was the [OV7670](https://web.mit.edu/6.111/www/f2016/tools/OV7670_2006.pdf). However the quality was poor. With Attempt 2 the suite of raspberry pi cameras become available for use. The camera that DAVE currently uses is the [Camera Module 2](https://www.raspberrypi.com/products/camera-module-v2/). It also connects to the Raspberry Pi via the CSI/DSI cable connector. This is talked more about later. Raspberry Pi includes an interface to read the camera data.

### Image Processing in depth

Images are read as a grid of bytes. This is known as the resolution. This is commonly seen as 1920 x 1080. This means 1920 is the width and 1080 is the height. At each position there can be 3 bytes one for each color R G B. This is refered to as RGB888. There may sometimes be an additional byte for the alpha value and this is called RGBA888. Another popular form of RBG involves only using 2 bytes to store 3 channels of color. 2 bytes is 16 bits and R is stored in the first 5 bits then G in the next 6 bits and the 5 bits are used for B. Because of all the ways to store color conversion from one color space to another is typically need. The go to for this is [opencv](https://opencv.org/), an open source module for processing images. Conversation can also be accomplished with some fancy bit shifting and numpy [numpy](https://numpy.org/) operations. Once you read the bytes and convert it to the required color space there are a few interesting things you can accomplish including opening to a HDMI via framebuffers or saving to a JPEG or PNG file for data storage and transfer. Images are some of the largest data that can be processed. 1920 * 1080 * 3 is 6.22 Megabytes of data for one frame. So a quick connection is something to consider if you want to transfer image/video data.

## Image Understanding 

Image understanding is at the core. DAVE is only possible due to large improvements of multimodal GPT-4 models that are publicly available through the power of open source. 

The primary model used was [LLaVA](https://llava-vl.github.io/). This model takes images and text as parameters and processes the images based on the prompt. 

Other models where tested with DAVE such as OpenAI GPT-4 vision but the processing time was worst.

Lots of research was done for hosting models on deployed infrastructure such as Amazon SageMaker but the cost where too great. Running and building LLaVA cost almost 30 dollars for 2 hours of running in SageMaker. More research needed in this area.

DAVE runs off of the efforts of these models but the processing time is not quite there yet for these image understanding models. Times are about 3 seconds which make for a cool project but not a viable product.

## Modeling

DAVE V1 was not the most comfortable device. There was significant efforts placed into creating a better wearable. This is when the CAD Design process began. Open Source is an integral part of the processing in DAVE. It is also a cornerstone in the development of DAVE. [freeCad](https://www.freecad.org/) is a very popular open source CAD program used to develop the models for DAVE.

The modelling process began first by learning CAD. Next I began by design initial designs for the glasses. Using the [Forge](https://www.rpiforge.dev/), we where able to turn our CAD models into stl files then to Gcode which is the format that 3D printers read. After several trial and errors we produced a model that was fairly compact and accomplished everything needed for DAVE. The camera and Pi where mounted on. 

The modelling process took several iterations and several hours of 3D printing jobs. 

## Conclusion

There was many hours of work put into understanding and creating Version 2 of DAVE. This is a quick run down of some interesting findings. These findings, code and cad models are all now publicly available.