import json
import urllib.parse
import subprocess
import os
import requests
import time

# sentences are built as following:
# [DISTANCE_PREFIXS] xxxx [DISTANCE_POSTFIXS] [DISTANCE_POSTFIXS] turn right.
# where xxxx are generated on the fly from 3.0, 2.5, 2.0, 1.5, 1.0, 0.5, 450, 400, 350, 300, 250, 200, 150, 100, 50
# you can adjust the distance voice by adjusting MAX_DISTANCE, DISTANCE_ABOVE, DISTANCE_ABOVE_DECREMENT, DISTANCE_BELOW_DECREMENT belows.
# for example:
#
#
# MAX_DISTANCE = 5100
# DISTANCE_ABOVE = 1000
# DISTANCE_ABOVE_DECREMENT = 100
# DISTANCE_BELOW_DECREMENT = 50
#
# distances will be 4.9, 4.8, 4.7, 4.7, 4.5 ..... 1.1, 1.0, 950, 900, 850, 800....


# languages
LANGUAGES = [
  "en",
  "en_uk",
  "zh_tw",
  # "zh_cn",
]

DISTANCE_PREFIXS = {
  "en": "In",
  "en_uk": "In",
  "zh_tw": "在",
  "zh_cn": "在",
}

DISTANCE_POSTFIXS = {
  "en": ",",
  "en_uk": ",",
  "zh_tw": " 後,",
  "zh_cn": " 后,",
}

UNITS = {
  "en": ["mi", "ft"],
  "en_uk": ["km", "m"],
  "zh_tw": ["km", "m"],
  "zh_cn": ["km", "m"],
}

DIRECTION_TABLES = {
  "en": "direction_en.json",
  "en_uk": "direction_en.json",
  "zh_tw": "direction_zh_tw.json",
  "zh_cn": "direction_zh_tw.json",
}

MAX_DISTANCE = 3500  # km / mi
DISTANCE_ABOVE = 500
DISTANCE_ABOVE_DECREMENT = 500
DISTANCE_BELOW_DECREMENT = 50

CURRENT_PATH = os.getcwd()

DELETE_MP3 = True

AUDIO_VOLUME = 2.5

FOLDER_PATH = 'voices'

def generate_tts(wav_file, mp3_file, speech, locale):
  if os.path.exists(wav_file):
    print(wav_file + " already exists.")
    return
  # Construct the URL
  encoded_speech = urllib.parse.quote(speech)
  url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_speech}&tl={locale}&client=tw-ob"
  # Send GET request
  response = requests.get(url, headers={
    "Referer": "http://translate.google.com/",
    "User-Agent": "stagefright/1.2 (Linux;Android 5.0)"
  })

  # Check if the request was successful
  if response.status_code == 200:
    # Save the response content to a file
    with open(mp3_file, "wb") as f:
      f.write(response.content)

    # Use FFmpeg to adjust volume and play
    ffmpeg_process = subprocess.Popen(
      ["ffmpeg", "-i", mp3_file, "-af", f"volume={str(AUDIO_VOLUME)}", "-f", "wav", wav_file],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True  # This ensures the output is returned as text
    )

    stdout, stderr = ffmpeg_process.communicate()

    if stderr:
      print("FFmpeg Error:", stderr)
    if DELETE_MP3:
      os.remove(mp3_file)
    print(mp3_file + " completed")
  else:
    print("Request failed:", response.status_code)
  time.sleep(1)

def build_direction():
  for lang in LANGUAGES:
    file_path = DIRECTION_TABLES[lang]
    with open(file_path, 'r') as json_file:
      data = json.load(json_file)
    for k, v in data.items():
      if v != "":
        speech = v
        file_name = CURRENT_PATH + "/voices/" + lang + "_" + k
        mp3_filename = file_name + ".mp3"
        wav_filename = file_name + ".wav"
        generate_tts(wav_filename, mp3_filename, speech, lang)

def build_distance():
  for lang in LANGUAGES:
    distance = MAX_DISTANCE
    locale_unit = UNITS.get(lang)
    while distance > 0:
      if distance > DISTANCE_ABOVE:
        distance -= DISTANCE_ABOVE_DECREMENT
        dist_text = distance/1000
        if dist_text % 1 != 0.5:
          dist_speech = int(dist_text)
        else:
          dist_speech = dist_text
        unit = locale_unit[0]
      else:
        distance -= DISTANCE_BELOW_DECREMENT
        dist_text = distance
        dist_speech = dist_text
        unit = locale_unit[1]
      if distance > 0:
        speech = DISTANCE_PREFIXS[lang] + " " + str(dist_speech) + unit + DISTANCE_POSTFIXS[lang]
        file_name = CURRENT_PATH + "/voices/" + lang + "_distance_" + str(dist_text) + unit
        mp3_filename = file_name + ".mp3"
        wav_filename = file_name + ".wav"
        generate_tts(wav_filename, mp3_filename, speech, lang)
    pass

def main():
  if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)
    print(f"Folder '{FOLDER_PATH}' created successfully.")
  else:
    print(f"Folder '{FOLDER_PATH}' already exists.")

  build_distance()
  build_direction()
  pass


if __name__ == "__main__":
  main()
