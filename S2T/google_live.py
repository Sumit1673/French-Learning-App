from __future__ import division
import wave
import threading
import os
import pyaudio
import keyboard
from utils.doparallelly import DoThreading
from six.moves import queue
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/key23.json"
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
FORMAT = pyaudio.paInt16


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._data_frame = []
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()
        self.performthreading()

    def performthreading(self):
        t1 = DoThreading(target=self._save_audio_file, name='Save Audio')
        t1.daemon = True
        t1.start()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        frames = in_data
        self._data_frame.append(frames)
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):

        while not self.closed:
            if keyboard.is_pressed('q'):
                break
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    # block=True waits till the duration is not elapsed
                    # block=False ignores the time duration and waits for the voice.
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

    def _save_audio_file(self):
        from datetime import datetime
        now = datetime.now()
        if not os.path.exists("..\\user_recordings"):
            os.mkdir("..\\user_recordings")
        file_name = "..\\user_recordings/ur_" + now.strftime("%b-%d-%H%M") + ".wav"
        out_wav_file = wave.open(file_name, 'wb')
        out_wav_file.setnchannels(1)
        out_wav_file.setsampwidth(self._audio_interface.get_sample_size(FORMAT))
        out_wav_file.setframerate(16000)
        out_wav_file.writeframes(b''.join(self._data_frame))
        out_wav_file.close()

# if __name__ == '__main__':
#     text = main()
