import time
import numpy as np
import pyaudio
import config

def start_stream(in_q_l, in_q_r):
    p = pyaudio.PyAudio()
    frames_per_buffer = int(config.MIC_RATE / config.FPS)
    print("Frames per buffer expected: " + str(frames_per_buffer))
    input_device_index = -1
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i)["name"])
        if "usbtv" in p.get_device_info_by_index(i)["name"]:
            input_device_index = i
            break
    if input_device_index == -1 :
         raise IOError("usbtv device wasn't found")
    
    def data_callback(in_data, frame_count, time_info, status):
        y = np.fromstring(in_data, dtype=np.int16)
        if status != 0:
            print(" frames_count: " + str(frame_count) + " status: " + str(status))
        y = np.reshape(y, (frames_per_buffer, 2))
        y = y.astype(np.float32)
        y_l = y[:, 0]
        y_r = y[:, 1]
        in_q_l.put(y_l)
        in_q_r.put(y_r)
        return (None, pyaudio.paContinue)
    
    stream = p.open(format=pyaudio.paInt16, input_device_index = input_device_index,
                    channels=2,
                    rate=config.MIC_RATE,
                    input=True,
                    frames_per_buffer=frames_per_buffer,
                    stream_callback=data_callback)
    print("Set microphone thread up. Looping.")
    while stream.is_active():
        time.sleep(0.0001)  
        
    stream.stop_stream()
    stream.close()
    p.terminate()
