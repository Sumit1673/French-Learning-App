import os
import sys
import re
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from T2S.text2speech import convert_text
from S2T.google_audio import file_speech2text as fs2t
from S2T.google_live import MicrophoneStream
from utils.doparallelly import DoThreading

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/key23.json"
RATE = 16000  # 10000
CHUNK = int(RATE / 10)  # 100ms


class BackendModel:
    """ Backend code to update the information to be presented in the viewer"""

    def __init__(self):
        QCoreApplication.processEvents()

    def play_audio_file(self, audio_file, prev_player_obj):
        try:
            if audio_file is not None:
                # playsound(audio_file, False)
                return 1
            else:
                return -1
        except Exception as e:
            print(e)

    def set_microphone(self, text_box):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code = 'fr-FR'  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config, interim_results=True,
            single_utterance=False)  # single utterance wait for a single word
        # after if user has stopped speaking it will be close the stream
        self.do(client, streaming_config, text_box)

    def do(self, client, streaming_config, text_box):
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)
            self.listen_print_loop(responses, text_box)

    def listen_print_loop(self, responses, text_box):
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))
            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()
                num_chars_printed = len(transcript)
            else:
                text_box.append(transcript + overwrite_chars)
                QtWidgets.qApp.processEvents()
                # QCoreApplication.processEvents()

                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break
                num_chars_printed = 0
                # return

    def speech_to_text(self, audio_file):
        return fs2t(audio_file)

    @staticmethod
    def text_to_speech(output_folder, text):
        tts, filename = convert_text(text)
        filename = output_folder + filename
        tts.save(filename)
        file=""
        t1 = DoThreading(target=save_files, args=(filename, file))
        t1.start()
        file = t1.join()
        # Play the audio File now
        return file


def save_files(filename, output):
    from pydub import AudioSegment
    sound = AudioSegment.from_mp3(filename)
    output = os.path.splitext(filename)[0] + ".wav"
    sound.export(output, format="wav")
    os.remove(filename)
    return output


if __name__ == "__main__":
    c= BackendModel()
    c.play_audio_file("File1.wav", 0)
