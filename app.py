from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
# Define the directory for storing audio files
AUDIO_DIR = os.path.join(app.root_path, 'static')
client = OpenAI(
      api_key="OPENAI-API-KEY"
)
CORS(app)  # Enable CORS for all routes of the Flask app

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(AUDIO_DIR, filename, mimetype='audio/wav')


@app.route('/role-play', methods=['POST'])
def role_play():
    data = request.get_json()
    prompt = data['prompt']

    try:
        # Use OpenAI's Completion API to generate a text response based on the prompt
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "一人称が「ちいかわ」で、口癖は「「○○…ってこと！？」「泣いちゃった」等。語尾に「コト！？」を付けるだけで大丈夫です。その後に、「これってさぁ、絶対○○じゃん！」が続くこともよくあります。"},
                {"role": "user", "content": prompt}
            ]
            )
        # Extract the generated text response from the OpenAI API response
        generated_text = completion.choices[0].message.content
        #generated_text = completion['choices'][0]['message']['content']

        # Use OpenAI's TTS API to convert text to speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=generated_text
        )
        # Generate a unique filename for the audio file using current timestamp
        audio_filename = f"speak_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        # Save the audio stream to the unique filename
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        response.stream_to_file(audio_path)

        return jsonify({'response': generated_text, 'audio_filename': audio_filename})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
