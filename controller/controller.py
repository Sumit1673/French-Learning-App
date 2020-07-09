from view.french_app_view import *
from model.model import BackendModel
import sys
from PyQt5 import QtWidgets
from utils.qt_thread import Worker
from PyQt5.QtCore import QThreadPool
from utils.audio_player import AudioPlayer

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/key23.json"
RATE = 10000  # 10000
CHUNK = int(RATE / 10)  # 100ms


class Controller:
    """ Class to control the flow of the view and pass it to the model"""

    def __init__(self):
        self.old_player_obj = None
        self.audio_file_timer = QtCore.QTimer()
        self._app = QtWidgets.QApplication(sys.argv)
        self._main_view = FrenchAppMainPage()
        self.thread_status = False
        self._backend = BackendModel()
        self._main_view.show()
        self.threadpool = QThreadPool()
        self.init()

    def init(self):
        """ Initializing the emitted signals from the viewer to their slots"""
        self.audio_file_timer.timeout.connect(self.on_timeout)
        self._main_view.browse_button_pressed_signal.connect(self._main_view.browse_button_pressed)
        self._main_view.update_text_toplay_signal.connect(self._main_view.update_text_toplay)
        self._main_view.convert_signal.connect(self.convert)
        self._main_view.clear_live_edit_text_box_signal.connect(self._main_view.clear_live_edit_text_box)
        self._main_view.clear_tts_text_box_signal.connect(self._main_view.clear_tts_text_box)
        self._main_view.compare_tts_stt_signal.connect(self._main_view.compare_tts_stt)
        self._main_view.close_app_signal.connect(self.close_app)
        self._main_view.play_audio_file_signal.connect(self.play_audio)
        self._main_view.rb_live_speech_signal.connect(lambda: self._main_view.btnstate(
            self._main_view.ui.rb_livespeech))
        self._main_view.live_speech_to_text_signal.connect(self.live_speech_to_text)

    def on_thread_finish(self):
        self._main_view.ui.record_pbutton.setEnabled(True)
        self._main_view.set_pushbutton_name(self._main_view.ui.record_pbutton, "Live Speech")
        self.thread_status = False

    def close_app(self):
        if os.path.exists("../output/audio_output"):
            import threading
            import shutil
            threading.Thread(target=shutil.rmtree, args=("../output/audio_output",), daemon=True).start()
        self._main_view.close()

    def play_audio(self):
        if self._main_view.audio_to_play.lower().endswith('.wav'):
            if self._main_view.get_pushbutton_text(self._main_view.ui.pb_audio_play) == "Play Audio":

                self.initialize_audio_player(self._main_view.audio_to_play.lower())

    def live_speech_to_text(self):
        # Change button text and color for notifying that its pressed and process is running
        self._main_view.ui.record_pbutton.setStyleSheet(
            "QPushButton{background-color: green}")
        if self.thread_status is False:
            self.thread_status = True
            self._main_view.ui.record_pbutton.setEnabled(False)
            self._main_view.set_pushbutton_name(self._main_view.ui.record_pbutton, "Speak Now")
            QApplication.processEvents()
            worker = Worker(self._backend.set_microphone, self._main_view.ui.livespeech_textbox)
            worker.signals.finished.connect(self.on_thread_finish)
            self.threadpool.start(worker)

    def run(self):
        self._main_view.show()
        return self._app.exec_()

    def on_timeout(self):
        if str(self.old_player_obj.get_state()) == "State.Ended":
            self.audio_file_timer.stop()
            self._main_view.set_pushbutton_name(self._main_view.ui.pb_audio_play, "Play Audio")

    def convert(self):
        if self._main_view.ui.rb_text2speech.isChecked():
            text = self.get_text_for_speech()
            if text != None and text != "":
                audio_file = self._backend.text_to_speech("../output/audio_output/", text)
                self.initialize_audio_player(audio_file)
            else:
                self._main_view.display_msg("Invalid Input", "Select a file or write text to convert")

        elif self._main_view.ui.rb_speech2text.isChecked():
            if self._main_view.selected_file_full_path.endswith('.wav'):
                self._main_view.ui.pb_play.setEnabled(False)
                QApplication.processEvents()

                response = self._backend.speech_to_text(self._main_view.selected_file_full_path)
                self._main_view.ui.text_to_play.setText(response)
                self._main_view.ui.pb_play.setEnabled(True)
            else:
                self._main_view.display_msg("Invalid File Type", "Choose '.wav' file")

        # Convert text speech to text directly from the edit box
        elif self._main_view.play_text is not None and self._main_view.play_text != "":
            audio_file = self._backend.text_to_speech("../output/audio_output/", self._main_view.play_text)
            self.initialize_audio_player(audio_file)
        else:
            self._main_view.display_msg("unknown Operation", "Try Again!!")

    def get_text_for_speech(self):
        if self._main_view.play_text is None or self._main_view.play_text == "":
            self._main_view.display_msg("Invalid File Error", "Check you selected file !!")
        else:
            return self._main_view.play_text

    def initialize_audio_player(self, audio_file):
        self._main_view.ui.pb_play.setEnabled(False)
        self.threadpool_audio = QThreadPool()
        worker = Worker(self.play_wave_audio, audio_file)
        worker.signals.finished.connect(self.on_audio_end)
        self.threadpool_audio.start(worker)

    def on_audio_end(self):
        self._main_view.ui.pb_play.setEnabled(True)
        QApplication.processEvents()

    def play_wave_audio(self, audio_file):
        with AudioPlayer(audio_file) as player:
            player.play()


if __name__ == "__main__":
    c_obj = Controller()
    sys.exit(c_obj.run())
