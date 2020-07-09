from __future__ import division
import os
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, uic, QtCore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/key23.json"

# Audio recording parameters
RATE = 10000
CHUNK = int(RATE / 10)  # 100ms
pem = open("../config/roots.pem")


class FrenchAppMainPage(QMainWindow):

    """ Class defines the view of the APP"""
    """ Custom Signal to be used by the controller to connect to the model """
    browse_button_pressed_signal = QtCore.pyqtSignal()
    update_text_toplay_signal = QtCore.pyqtSignal()
    convert_signal = QtCore.pyqtSignal()
    clear_live_edit_text_box_signal = QtCore.pyqtSignal()
    clear_tts_text_box_signal = QtCore.pyqtSignal()
    compare_tts_stt_signal = QtCore.pyqtSignal()
    close_app_signal = QtCore.pyqtSignal()
    play_audio_file_signal = QtCore.pyqtSignal()
    live_speech_to_text_signal = QtCore.pyqtSignal()
    rb_live_speech_signal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.player_old_obj = None
        self.title = "Apprends le Français"
        self.left, self.top = 10, 10
        self.width, self.height = 640, 640
        try:
            self.ui = uic.loadUi('../config/Frenchuolingo.ui', self)
        except FileNotFoundError as e:
            print(e)
        self.audio_folder = "../output/audio_output/"
        if not os.path.exists(self.audio_folder):
            os.mkdir(self.audio_folder, mode=0o777)
        self.model = QFileSystemModel()
        self.msg_box = QMessageBox()
        self.operation_group = QButtonGroup(QWidget(self))
        self.selection_group = QButtonGroup(QWidget(self))
        self.msg_box.setIcon(QMessageBox.Information)
        self.selected_file_full_path = None
        self.play_text = None
        self.audio_to_play = ""
        self.init_ui()

    def init_ui(self):

        """Few Initializations"""
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.move(50,50)
        self.ui.browse_pbutton.setEnabled(False)
        # self.ui.pb_play.setEnabled(False)
        self.ui.record_pbutton.setIcon(QtGui.QIcon("./icons8-audio-100.png"))
        self.ui.record_pbutton.setToolTip('Live Speech to Text')
        self.ui.record_pbutton.setEnabled(False)
        self.ui.record_pbutton.setStyleSheet(
            "QPushButton{background-color: orange}")
        self.file_system_model('../')
        self.tree_view_properties('../')
        self.ui.rb_livespeech.setChecked(False)
        self.operation_group.addButton(self.ui.rb_speech2text)
        self.operation_group.addButton(self.ui.rb_text2speech)
        self.selection_group.addButton(self.ui.rb_selectFile)
        self.selection_group.addButton(self.ui.rb_selectFolder)

        """***********  Connections to the slots  *************    """
        self.ui.browse_pbutton.clicked.connect(self.browse_button_pressed)
        # self.ui.pb_play.clicked.connect(self.read_text())
        self.ui.rb_selectFolder.clicked.connect(self.rb_browseslot)
        self.ui.text_to_play.textChanged.connect(self.update_text_toplay_signal)
        self.ui.rb_selectFile.clicked.connect(self.rb_browseslot)
        self.ui.pb_play.clicked.connect(self.convert_signal)
        self.ui.pb_clear_live_edit_text_box.clicked.connect(self.clear_live_edit_text_box_signal)
        self.ui.pb_clear_tts.clicked.connect(self.clear_tts_text_box_signal)
        # self.ui.pb_clearall.clicked.connect(self.clear_text_area)
        self.ui.pb_compare.clicked.connect(self.compare_tts_stt_signal)
        self.ui.pb_close.clicked.connect(self.close_app_signal)
        self.ui.pb_audio_play.clicked.connect(self.play_audio_file_signal)
        self.ui.record_pbutton.clicked.connect(self.live_speech_to_text_signal)
        self.ui.rb_livespeech.toggled.connect(self.rb_live_speech_signal)
        self.ui.rb_livespeech.toggled.connect(lambda: self.btnstate(self.ui.rb_livespeech))


    @QtCore.pyqtSlot()
    def btnstate(self, btn):
        self.ui.record_pbutton.setEnabled(True)
        self.ui.record_pbutton.setStyleSheet(
            "QPushButton{background-color: green}")

    @QtCore.pyqtSlot()
    def browse_button_pressed(self):
        self.ui.editFile_path.clear()
        dialog = QFileDialog()
        options = QFileDialog.Options()
        if self.ui.rb_selectFolder.isChecked():
            folder_path = dialog.getExistingDirectory(
                self, "Choose Folder", '.', options=QFileDialog.DontUseNativeDialog)
            if folder_path != "" or folder_path is not None:
                self.display_browse_path(folder_path)                         
                self.display_folder_content(path=folder_path)                
                return folder_path
            else:
                self.display_msg("Folder Path Error", "Choose a Folder")
                return

        elif self.ui.rb_selectFile.isChecked():
            # if self.ui.rb_text2speech.isChecked():
            options |= QFileDialog.DontUseNativeDialog
            self.selected_file_full_path, _ =\
                QFileDialog.getOpenFileName(self,
                                            "Choose File to convert", ".",
                                            "Text Files (*.txt);;Audio Files(*.wav )"
                                            , options=options)
            self.display_browse_path(self.selected_file_full_path)
            if self.selected_file_full_path.endswith('.txt'):
                self.read_and_set_text()

    def display_browse_path(self, file_path):
        self.ui.editFile_path.setText(file_path)

    def display_folder_content(self, *, path):
        self.file_system_model(path)
        self.tree_view_properties(path)

    def get_pushbutton_text(self, button_name):
        return button_name.text()

    def set_pushbutton_name(self, button_name, text):
        button_name.setText(text)

    def tree_view_properties(self, path):
        self.ui.tree_FolderView.clicked.connect(self.tree_view_on_clicked_slot)
        self.ui.tree_FolderView.setModel(self.model)
        self.ui.tree_FolderView.setRootIndex(self.model.index(path))

    def file_system_model(self, path):
        self.model.setReadOnly(True)
        self.model.setRootPath(path)

    @staticmethod
    def extra_string(text1, text2):
        extra = [str(diff) for diff in text1 if diff not in text2]
        return extra

    def compare_tts_stt(self):
        tts_text = self.play_text
        if tts_text is None or tts_text == "Write Text":
            self.display_msg("Empty Block", "Nothing To compare")
            return
        stt_text = self.ui.livespeech_textbox.toPlainText()
        if stt_text is not None and stt_text != "" and tts_text is not None and tts_text != 'Write Text':
            pattern = [str(diff) for diff in stt_text.lower().split() if diff not in tts_text.lower().split()]

            cursor_pos = self.ui.livespeech_textbox.textCursor()
            highlight_format = QtGui.QTextCharFormat()
            highlight_format.setBackground(QtGui.QBrush(QtGui.QColor("red")))

            for i in range(0, len(pattern)):
                text = pattern[i]
                regex = QtCore.QRegExp(text)
                pos = 0
                index = regex.indexIn(self.ui.livespeech_textbox.toPlainText().lower(), pos)
                while index != -1:
                    cursor_pos.setPosition(index)
                    cursor_pos.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                    cursor_pos.mergeCharFormat(highlight_format)
                    # Move to the next match
                    pos = index + regex.matchedLength()
                    index = regex.indexIn(self.ui.livespeech_textbox.toPlainText().lower(), pos)
            highlight_format.setBackground(QtGui.QBrush(QtGui.QColor("white")))
            self.ui.livespeech_textbox.mergeCurrentCharFormat(highlight_format)


    def read_and_set_text(self):
        if os.stat(self.selected_file_full_path).st_size != 0:
            with open(self.selected_file_full_path, 'r', encoding='utf8') as fd:
                lines = fd.readlines()
                self.play_text = ""
                for i in lines:
                    self.play_text = self.play_text + i
            self.ui.text_to_play.setText(self.play_text)
            # print(self.ui.text_to_play.toPlainText())
            fd.close()
            return self.play_text
        else:
            self.display_msg("File Error", "File is Empty!!")

    @QtCore.pyqtSlot() # called from controller
    def update_text_toplay(self):
        self.play_text = self.ui.text_to_play.toPlainText()

    @QtCore.pyqtSlot()
    def clear_live_edit_text_box(self):
        highlight_format = QtGui.QTextCharFormat()
        highlight_format.setBackground(QtGui.QBrush(QtGui.QColor("white")))
        self.ui.livespeech_textbox.clear()

    def clear_tts_text_box(self):
        self.ui.text_to_play.clear()

    @QtCore.pyqtSlot()
    def rb_browseslot(self):
        # self.readTextfrom = selection_type
        self.ui.browse_pbutton.setEnabled(True)

    def tree_view_on_clicked_slot(self, index):
        index_item = self.model.index(index.row(), 0, index.parent())
        # selected_fileName = self.model.fileName(indexItem)
        self.selected_file_full_path = self.model.filePath(index_item)
        if self.selected_file_full_path.endswith('.txt'):
            self.read_and_set_text()
        if self.selected_file_full_path.endswith(('.wav', '.mp3')):
            self.audio_to_play = self.selected_file_full_path

    # Called by controller
    def display_msg(self, title: str, msg: str):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(title)
        msg_box.setInformativeText(msg)
        msg_box.exec()


if "__main__" == __name__:
    app = QApplication([])
    myapp = FrenchAppMainPage()
    myapp.show()
    app.exec_()
