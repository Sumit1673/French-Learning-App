import io
import concurrent.futures as con
from os import listdir
import os
# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../config/key23.json"


def file_speech2text(audio_path):
	# Instantiates a client
	client = speech.SpeechClient()
	if os.path.isfile(audio_path):
		text = read_file(client, audio_path)
	else:
		for each_audio_file in listdir(audio_path):
			audio_file = audio_path + each_audio_file
			text = read_file(client, audio_file)
	# return text
	# Loads the audio into memory
		with io.open(audio_file, 'rb') as file:
			content = file.read()
			audio = types.RecognitionAudio(content=content)

			config = types.RecognitionConfig(
				encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
				sample_rate_hertz=16000,
				language_code='fr-FR', audio_channel_count=2)

		# Detects speech in the audio file
		print("Hey Sumit Shimona here")
		with con.ThreadPoolExecutor() as executor:
			converted_data = executor.submit(client.recognize, [config, audio])
			response = converted_data.result()
			# response = client.recognize(config, audio)
		for result in response.results:
			text = result.alternatives[0].transcript
			print('Transcript: {}'.format(result.alternatives[0].transcript))
	return text


def read_file(client, audio_file):
	with io.open(audio_file, 'rb') as file:
		content = file.read()
		audio = types.RecognitionAudio(content=content)

		config = types.RecognitionConfig(
			encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
			sample_rate_hertz=44100,
			language_code='fr-FR', audio_channel_count=2)

		# Detects speech in the audio file

	response = client.recognize(config, audio)
	text = None
	for result in response.results:
		text = result.alternatives[0].transcript
		# print('Transcript: {}'.format(result.alternatives[0].transcript))
		print("\n")
	return text


if __name__ == '__main__':
	audio_dir = 'D:\\Speechrecog\\test_app\\file.mp3'
	response = file_speech2text(audio_dir)
