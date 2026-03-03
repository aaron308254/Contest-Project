import requests
import io
import speech_recognition as sr
from datetime import datetime
from pydub import AudioSegment
import imageio_ffmpeg
import os
import time

#WPR Midday Quiz: 18004427106 Around 12:30 PM CST
#Email answer to midday@wpr.org
#Maybe add a way to auto send emails
#Preemptive message to chatgpt: Answer this quiz question concisely, ideally with only the answer:
#Create 10 email addresses to send emails
#Append Aaron Jones, Madison WI to end

# Radio Stream URL
STREAM_URL = "https://wpr-ice.streamguys1.com/wpr-music-mp3-96"

# File Paths
mp3_path = "radio_audio.mp3"  # Save MP3 chunk in project folder
wav_path = "radio_audio.wav"  # Converted WAV file

# Keywords to detect
KEYWORDS = ["contest", "giveaway", "call now", "win tickets", "quiz"]

def download_radio_chunk():
    """Downloads a small chunk of radio audio for processing."""
    response = requests.get(STREAM_URL, stream=True)
    buffer = io.BytesIO()

    with open(mp3_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
            if f.tell() > 500000:  # Stop after ~500KB (~30 sec audio)
                break

def listen_to_radio():
    recognizer = sr.Recognizer()
    download_radio_chunk()

    if not os.path.exists(mp3_path):
        print(f"❌ Error: MP3 file {mp3_path} does not exist!")
        return False
    # Convert MP3 to WAV
    time.sleep(2)
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    audio.export(wav_path, format="wav")

    with sr.AudioFile(wav_path) as source:
        try:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio).lower()
            print(f"[{datetime.now()}] Transcribed: {text}")
            
            # Check for contest keywords
            for keyword in KEYWORDS:
                if keyword in text:
                    print(f"🎉 Contest Alert! Keyword '{keyword}' detected at {datetime.now()}")
                    with open("contest_log.txt", "a") as log_file:
                        log_file.write(f"{text}")
                    break

        except sr.UnknownValueError:
            print("Could not understand audio")
            pass  # Ignore unrecognized speech
        except sr.RequestError as e:
            print(f"Speech Recognition Error: {e}")

    audio_buffer = io.BytesIO()  # Reset buffer

if __name__ == "__main__":
    while True:
        print("\n Listening for contest....")
        listen_to_radio()