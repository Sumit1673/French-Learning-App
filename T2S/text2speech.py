import os
from gtts import gTTS
from datetime import datetime


def convert_text(_text):
    lang = 'fr'
    tts = gTTS(text=_text, lang=lang)
    now = datetime.now()
    file_name = "samp_" + now.strftime("%b-%d-%Y-%H%M%S") + ".mp3"
    return tts, file_name


if __name__ == '__main__':
    text = "Bonjour je m'appelle Antoine et j'habite à Montréal au Québec. Ce soir je serai à " \
           "la maison et je pourrai enfin voir mes enfants."
    convert_text(text)
