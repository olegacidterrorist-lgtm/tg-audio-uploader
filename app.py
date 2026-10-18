import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

TOKEN = os.environ.get("TELEGRAM_TOKEN")

@app.route("/upload", methods=["POST"])
def upload():
    audio = request.files.get("audio")
    chat_id = request.form.get("chat_id")
    
    if not audio or not chat_id:
        return jsonify({"error": "Missing data"}), 400

    url = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
    files = {"audio": (audio.filename, audio.stream, "audio/webm")}
    data = {
        "chat_id": chat_id,
        "title": "My Matrix Track",
        "performer": "Hacker Groovebox"
    }
    
    try:
        resp = requests.post(url, files=files, data=data)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
