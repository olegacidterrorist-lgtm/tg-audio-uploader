import os
import requests
import subprocess
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Проверка, видит ли сервер FFmpeg (откройте в браузере .../check-ffmpeg)
@app.route("/check-ffmpeg")
def check_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return f"✅ FFmpeg найден: {ffmpeg_path}"
    else:
        return "❌ FFmpeg НЕ НАЙДЕН (проверьте Dockerfile)", 500

@app.route("/upload", methods=["POST"])
def upload():
    audio = request.files.get("audio")
    chat_id = request.form.get("chat_id")
    title = request.form.get("title", "Untitled Track")
    performer = request.form.get("performer", "Unknown Artist")
    
    if not audio or not chat_id:
        return jsonify({"error": "Missing data"}), 400

    # Сохраняем входящий файл (WebM) во временный файл
    temp_input = f"/tmp/{audio.filename}"
    temp_output = "/tmp/track.mp3"
    audio.save(temp_input)

    try:
        # Конвертируем WebM в MP3
        # -vn отключает видео, -ar частота, -ab битрейт
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_input, 
            "-vn", "-ar", "44100", "-ab", "192k", 
            "-f", "mp3", temp_output
        ], check=True, capture_output=True)

        # Отправляем MP3 в Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
        
        with open(temp_output, "rb") as mp3_file:
            # ВАЖНО: имя файла строго "track.mp3" и тип "audio/mpeg"
            files = {"audio": ("track.mp3", mp3_file, "audio/mpeg")}
            data = {
                "chat_id": chat_id,
                "title": title,
                "performer": performer
            }
            resp = requests.post(url, files=files, data=data)
            
        return jsonify(resp.json())

    except subprocess.CalledProcessError as e:
        # Если FFmpeg упал, выводим ошибку в логи
        error_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"FFmpeg error: {error_msg}")
        return jsonify({"error": "FFmpeg conversion failed", "details": error_msg}), 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Убираем временные файлы
        if os.path.exists(temp_input): os.remove(temp_input)
        if os.path.exists(temp_output): os.remove(temp_output)

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
