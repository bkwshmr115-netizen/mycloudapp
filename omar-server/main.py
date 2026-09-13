import os
import base64
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# تحديد المجلد الحالي بشكل صحيح
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=current_dir, static_folder=current_dir)
CORS(app)

# مجلد حفظ صور الدخلاء (يعمل على Termux)
SAVE_DIR = "/sdcard/Download/OmniLock_Captures"

def ensure_save_dir():
    """إنشاء مجلد الحفظ إذا لم يكن موجودًا"""
    global SAVE_DIR
    try:
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR, exist_ok=True)
        # اختبار الكتابة
        test_file = os.path.join(SAVE_DIR, ".test_write")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"⚠️ فشل الوصول لمجلد /sdcard، سيتم الحفظ داخل مجلد المشروع: {e}")
        SAVE_DIR = os.path.join(current_dir, "OmniLock_Captures")
        os.makedirs(SAVE_DIR, exist_ok=True)
        return False

# تجهيز مجلد الحفظ عند التشغيل
ensure_save_dir()

@app.route('/')
def home():
    """عرض واجهة الحماية"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def lock_security():
    """استقبال صورة الدخيل وحفظها سريًا"""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "reply": "لم يتم استلام أي بيانات."
            }), 400

        # التحقق من إشارة التسلل
        if data.get('alert') == 'intrusion_detected':
            img_data = data.get('image')

            if not img_data or "," not in img_data:
                return jsonify({
                    "status": "error",
                    "reply": "صورة غير صالحة."
                }), 400

            try:
                # فصل رأس الـ base64 عن البيانات
                header, encoded = img_data.split(",", 1)
                img_bytes = base64.b64decode(encoded)
            except Exception as decode_error:
                print(f"❌ فشل فك تشفير الصورة: {decode_error}")
                return jsonify({
                    "status": "error",
                    "reply": "تعذر قراءة الصورة."
                }), 400

            # تسمية الملف بالتاريخ والوقت
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"thief_{timestamp}.jpg"
            file_path = os.path.join(SAVE_DIR, file_name)

            # حفظ الصورة
            with open(file_path, "wb") as f:
                f.write(img_bytes)

            print(f"🔒 [أمن] تم رصد دخيل! تم حفظ الصورة في: {file_path}")

            return jsonify({
                "status": "secured",
                "reply": "تم التقاط ملامح الدخيل وحفظها سريًا.",
                "saved_as": file_name
            })

        # في حالة عدم وجود تنبيه تسلل
        return jsonify({
            "status": "idle",
            "reply": "النظام يحرس الهاتف صامتًا."
        })

    except Exception as e:
        print(f"❌ خطأ في النظام الأمني: {e}")
        return jsonify({
            "status": "error",
            "reply": "جدار الحماية نشط ومستقر."
        }), 500

@app.route('/status', methods=['GET'])
def system_status():
    """فحص حالة النظام (اختياري)"""
    return jsonify({
        "status": "online",
        "save_directory": SAVE_DIR,
        "message": "OmniLock AI يعمل بشكل طبيعي"
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🛡️  OmniLock AI - نظام الحماية نشط")
    print(f"📁 مجلد حفظ الصور: {SAVE_DIR}")
    print("🌐 السيرفر يعمل على: http://0.0.0.0:8000")
    print("=" * 50)
    
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=8000, debug=False)
