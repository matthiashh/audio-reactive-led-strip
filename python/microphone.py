import time
import numpy as np
import pyaudio
import config


def start_stream(callback):
    p = pyaudio.PyAudio()
    buffer_multiplier = 1
    frames_per_buffer = buffer_multiplier*int(config.MIC_RATE / config.FPS)
    print(frames_per_buffer)
    input_device_index = -1
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i)["name"])
        if "USB PnP" in p.get_device_info_by_index(i)["name"]:
            input_device_index = i
            break
    if input_device_index == -1 :
         raise IOError("usbtv device wasn't found")
    stream = p.open(format=pyaudio.paInt16, input_device_index = input_device_index,
                    channels=1,
                    rate=config.MIC_RATE,
                    input=True,
                    frames_per_buffer=frames_per_buffer)
    overflows = 0
    prev_ovf_time = time.time()
    while True:
        try:
            y = np.fromstring(stream.read(frames_per_buffer), dtype=np.int16)
#            y = np.reshape(y, (frames_per_buffer, 1))
#            y = y[:, 0]
#            y = y[:y.shape[0]/(2*buffer_multiplier)]
#            y = np.fromstring(stream.read(frames_per_buffer, exception_on_overflow=False), dtype=np.int16)
            y = y.astype(np.float32)
            print("In Buffer: " + str(stream.get_read_available()))
            stream.read(stream.get_read_available())
#            stream.read(stream.get_read_available(), exception_on_overflow=False)
            callback(y)
        except IOError:
            overflows += 1
            if time.time() > prev_ovf_time + 1:
                prev_ovf_time = time.time()
                print('Audio buffer has overflowed {} times'.format(overflows))
    stream.stop_stream()
    stream.close()
    p.terminate()
