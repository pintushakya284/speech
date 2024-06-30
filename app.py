from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import logging
import io

app = Flask(__name__)
translator = Translator()
recognizer = sr.Recognizer()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        audio_data = request.files['audio'].read()
        with io.BytesIO(audio_data) as source:
            audio = recognizer.record(source)
            text = recognize_human_speech(audio)
            return jsonify({'recognized_text': text})
    except Exception as e:
        logger.error(f"Error in recognize: {e}")
        return jsonify({'recognized_text': '', 'error': str(e)})

def recognize_human_speech(audio):
    try:
        text = recognizer.recognize_google(audio, language='en-US', show_all=False)
        return text
    except sr.UnknownValueError:
        return ''
    except sr.RequestError as e:
        return str(e)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('lang', 'en')

    if not text:
        return jsonify({'translated_text': 'No text to translate'})

    try:
        translated_text = translator.translate(text, dest=target_lang).text
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        logger.error(f"Error in translate: {e}")
        return jsonify({'translated_text': 'Translation failed', 'error': str(e)})

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    lang = data.get('lang', 'en')

    if not text:
        return jsonify({'error': 'No text to convert to speech'})

    try:
        tts = gTTS(text=text, lang=lang)
        audio_file = io.BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        return jsonify({'audio': audio_file.read().decode('latin-1')})
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
