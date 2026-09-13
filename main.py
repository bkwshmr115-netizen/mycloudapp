import os
import base64
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=current_dir, static_folder=current_dir)
CORS(app)

# مكان حفظ الصور ليظهر في تطبيق الصور (Gallery)
SAVE_DIR = "/sdcard/DCIM/OmniLock"

def ensure_save_dir():
    global SAVE_DIR
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        test_file = os.path.join(SAVE_DIR, ".test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"⚠️ فشل إنشاء مجلد DCIM، التحويل لمجلد بديل: {e}")
        SAVE_DIR = os.path.join(current_dir, "OmniLock_Captures")
        os.makedirs(SAVE_DIR, exist_ok=True)
        return False

ensure_save_dir()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def lock_security():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "reply": "لا توجد بيانات"}), 400

        alert_type = data.get('alert')

        if alert_type in ['intrusion_detected', 'panic_mode', 'failed_login']:
            img_data = data.get('image')
            if img_data and "," in img_data:
                try:
                    header, encoded = img_data.split(",", 1)
                    img_bytes = base64.b64decode(encoded)

                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    prefix = "panic" if alert_type == "panic_mode" else "thief"
                    file_name = f"{prefix}_{timestamp}.jpg"
                    file_path = os.path.join(SAVE_DIR, file_name)

                    with open(file_path, "wb") as f:
                        f.write(img_bytes)

                    print(f"🔒 تم حفظ صورة ({alert_type}) في: {file_path}")

                    return jsonify({
                        "status": "secured",
                        "reply": "تم التقاط وحفظ الصورة بنجاح",
                        "saved_as": file_name,
                        "path": file_path
                    })
                except Exception as e:
                    print(f"❌ خطأ في حفظ الصورة: {e}")
                    return jsonify({"status": "error", "reply": "فشل حفظ الصورة"}), 500

        return jsonify({"status": "idle", "reply": "النظام يحرس صامتًا"})

    except Exception as e:
        print(f"❌ خطأ عام: {e}")
        return jsonify({"status": "error", "reply": "النظام مستقر"}), 500

@app.route('/status', methods=['GET'])
def system_status():
    return jsonify({
        "status": "online",
        "save_directory": SAVE_DIR,
        "message": "OmniLock Neural Core يعمل"
    })

if __name__ == '__main__':
    print("=" * 55)
    print("🛡️  OmniLock Neural Core - Backend Active")
    print(f"📁 مجلد الصور: {SAVE_DIR}")
    print("🌐 http://0.0.0.0:8000")
    print("=" * 55)
    app.run(host='0.0.0.0', port=8000, debug=False)
