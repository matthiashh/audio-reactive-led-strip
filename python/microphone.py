import time
import numpy as np
import pyaudio
import config


def start_stream(callback):
    p = pyaudio.PyAudio()
    frames_per_buffer = int(config.MIC_RATE / config.FPS)
    print(frames_per_buffer)
    input_device_index = -1
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i)["name"])
        if "usbtv" in p.get_device_info_by_index(i)["name"]:
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
            y = np.reshape(y, (frames_per_buffer, 1))
            y = y[:, 0]
            y = y.astype(np.float32)
            stream.read(stream.get_read_available())
            callback(y)
        except IOError:
            overflows += 1
            if time.time() > prev_ovf_time + 1:
                prev_ovf_time = time.time()
                print('Audio buffer has overflowed {} times'.format(overflows))
    stream.stop_stream()
    stream.close()
    p.terminate()
