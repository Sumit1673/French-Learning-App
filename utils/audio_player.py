import os
import pyaudio
import wave
from pynput import keyboard


class AudioPlayer:
    def __init__(self, audio_file):
        self.paused = False
        if isinstance(audio_file, str):
            if os.path.splitext(audio_file)[1] == '.wav' or os.path.splitext(audio_file)[1] == '.mp3':
                self.audio_file = audio_file

    def __enter__(self):
        self._wf = wave.open(self.audio_file, 'rb')

        # instantiate PyAudio
        self._audio_interface = pyaudio.PyAudio()

        # open stream using callback
        self._audio_stream = self._audio_interface.open(
            format=self._audio_interface.get_format_from_width(self._wf.getsampwidth()),
            channels=self._wf.getnchannels(),
            rate=self._wf.getframerate(),
            output=True,
            stream_callback=self.callback)
        return self

    def __exit__(self, exc_ty, exc_val, tb):
        # stop stream
        self.close_audio()

    def close_audio(self):
        # stop stream
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self._wf.close()

        # close PyAudio
        self._audio_interface.terminate()

    def play(self):
        # start the stream
        self._audio_stream.start_stream()

        while self._audio_stream.is_active() or self.paused is True:
            with keyboard.Listener(on_press=self.on_press) as listener:
                listener.join()
        return

    def callback(self, in_data, frame_count, time_info, status):
        data = self._wf.readframes(frame_count)
        return data, pyaudio.paContinue

    def on_press(self, key):
        if key == keyboard.Key.esc:
            if self._audio_stream.is_stopped():  # time to play audio
                self._audio_stream.start_stream()
                self.paused = False
                return False
            elif self._audio_stream.is_active():  # time to pause audio
                self._audio_stream.stop_stream()
                self.paused = False
                return False
        return False


def set_player():
    with AudioPlayer("D:\Speechrecog\V3\Frenchuolinguo\output\\audio_output\\file.wav") as player:
        player.play()


if __name__ == '__main__':
    import threading
    t1 = threading.Thread(target=set_player)
    t1.start()
