from flask import Flask, render_template_string, request, session, redirect, url_for
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import hashlib
import base64
import os




app = Flask(__name__)
app.secret_key = "super_secret_key"  # ใช้สำหรับจัดการ session

# ฟังก์ชันเข้ารหัส AES
def encrypt_aes(key, plaintext, iv):
    """เข้ารหัสข้อความด้วย AES (โหมด CBC)"""
    if len(iv) != 16:
        raise ValueError("IV must be 16 bytes long")

    # แปลง IV จาก str เป็น bytes
    iv_bytes = bytes.fromhex(iv) if isinstance(iv, str) else iv

    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv_bytes)  # ใช้โหมด CBC
    padded_plaintext = pad(plaintext)  # เพิ่ม Padding
    ciphertext = cipher.encrypt(padded_plaintext.encode('utf-8'))  # เข้ารหัส
    return base64.b64encode(iv_bytes + ciphertext).decode('utf-8')  # รวม IV และ Ciphertext

def decrypt_aes(key, encrypted):
    encrypted_data = base64.b64decode(encrypted)  # ถอด Base64
    iv = encrypted_data[:16]  # แยก IV
    ciphertext = encrypted_data[16:]  # แยก Ciphertext
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)  # ใช้โหมด CBC
    plaintext = cipher.decrypt(ciphertext).decode('utf-8')  # ถอดรหัส
    return unpad(plaintext)

# ฟังก์ชันเข้ารหัส RSA
def encrypt_rsa(public_key, plaintext):
    rsa_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(rsa_key)
    ciphertext = cipher.encrypt(plaintext.encode('utf-8'))
    return base64.b64encode(ciphertext).decode('utf-8')

# ฟังก์ชันสร้าง RSA Key Pair
def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# ฟังก์ชันสร้าง Hash
def hash_sha256(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def pad(data):
    pad_length = 16 - (len(data) % 16)
    return data + chr(pad_length) * pad_length

# ฟังก์ชัน Unpadding
def unpad(data):
    pad_length = ord(data[-1])
    return data[:-pad_length]

# ด่านทั้งหมด
private_key, public_key = generate_rsa_keys()

QUESTIONS = [
    {
        "id": 1,
        "type": "HASH",
        "question": "นำหลักการ Hash Function มาใช้ในการเข้ารหัสข้อความ",
        "data": lambda: {
            "answer":"Flag(62b31846df8db8abf5c31870eb5563f707a3ddb5fe543df8b193a4dfe98eb055)"
        }
    },
    {
    "id": 2,
    "type": "AES",
    "question": "คำตอบถูกซ่อนในข้อความที่เข้ารหัส ผู้เล่นต้องหา Key เพื่อถอดรหัส",
    "data": lambda: {
        "answer":"Flag(CyberSUT)"
    }
    },
    {
    "id": 3,
    "type": "RSA",
    "question": "ถอดรหัสข้อความในไฟล์ CipherText.pdf ด้วย PublicKey.pdf",
    "data": lambda: {
        "answer":"Flag(ENG4054AA-06)"
        # "answer": "Flag{YOUR_ANSWER}"  # แทนด้วยคำตอบที่ได้หลังถอดรหัส
    }
    },
    {
    "id": 4,
    "type": "AES",
    "question": "ถอดรหัสไฟล์รูป Answer.dat ที่เข้ารหัสด้วย AES",
    "data": lambda: {
        "key_hint": (
            "Key: 256 bit\n"
            "Mode: 43 54 42 (ฐาน 16)\n"
            "Hash: MD5\n"
            "อย่าลืมเปลี่ยนชื่อไฟล์เป็น .png หลังถอดรหัสสำเร็จ"
        ),
        "hint": "ใช้ AES-256 และเว็บไซต์ https://emn178.github.io/online-tools/aes/decrypt/ เพื่อถอดรหัส",
        "file_name": "Answer.dat",  # ไฟล์เข้ารหัสที่ผู้เล่นต้องถอดรหัส
        "answer":"Flag(วิไลศิลา)"
        # "answer": "Flag{YOUR_ANSWER}"  # แทนที่ด้วยคำตอบที่ได้จากการถอดรหัสไฟล์
    }
}
]
@app.route("/", methods=["GET"])
def story_page1():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>เริ่มภารกิจ</title>
        <style>
            /* พื้นหลังวิดีโอ */
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: Arial, sans-serif;
                color: #fff;
            }
            .video-background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: -1;
            }

            /* กล่องเนื้อหา */
            .container {
                max-width: 800px;
                margin: 100px auto;
                background: rgba(0, 0, 0, 0.7);
                padding: 30px 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
                animation: fadeIn 1.5s ease-in-out;
                text-align: left; /* จัดตำแหน่งเนื้อหาและปุ่มให้ชิดซ้าย */
            }

            h1 {
                font-size: 2.8em;
                color: #ffcc00;
                margin-bottom: 20px;
                text-align: center; /* หัวข้อยังคงอยู่ตรงกลาง */
            }

            p {
                font-size: 1.2em;
                line-height: 1.8;
                margin-bottom: 20px;
                text-align: justify;
            }

            /* ปุ่ม */
            button {
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(45deg, #ff9800, #e65100);
                color: #fff;
                font-size: 1.2rem;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                margin-top: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }

            button:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            }

            /* เอฟเฟกต์เฟดอิน */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .container {
                    margin: 50px 10px;
                    padding: 20px;
                }

                h1 {
                    font-size: 2.2em;
                }

                p {
                    font-size: 1rem;
                }

                button {
                    font-size: 1rem;
                    padding: 10px 20px;
                }
            }
        </style>
    </head>
    <body>
        <!-- วิดีโอพื้นหลัง -->
        <video autoplay muted loop class="video-background">
            <source src="static/images/33974-399148659.mp4" type="video/mp4">
            เบราว์เซอร์ของคุณไม่รองรับวิดีโอ
        </video>

        <!-- เนื้อหา -->
        <div class="container">
    <h1>ในปี ค.ศ. 2095 โลกเข้าสู่ยุคมืด</h1>
    <p>โลกได้เข้าสู่ยุคมืดหลังการล่มสลายครั้งใหญ่ ซึ่งเกิดจากการทดลองขององค์กรลับที่พัฒนาวิทยาการด้านอาวุธชีวภาพ แต่ความทะเยอทะยานของพวกเขากลับกลายเป็นโศกนาฏกรรม เมื่อเกิดการรั่วไหลของเชื้อไวรัสร้ายแรงที่พวกเขาสร้างขึ้น</p>
    <p>เชื้อไวรัสนี้แพร่กระจายอย่างรวดเร็วและรุนแรงกว่าการระบาดใดที่มนุษยชาติเคยเผชิญ ผู้ติดเชื้อจะมีอาการหายใจลำบากจนถึงขั้นหัวใจวายเฉียบพลัน ส่งผลให้สังคมล่มสลาย และความกลัวเข้าครอบงำมนุษยชาติ</p>
    <button onclick="window.location.href='/story/page2'">ถัดไป</button>
</div>

    </body>
    </html>
    """


@app.route("/story/page2", methods=["GET"])
def story_page2():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CTF Story - Page 2</title>
        <style>
            /* พื้นหลัง */
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-image: url('https://cdn.pixabay.com/photo/2020/03/16/16/29/virus-4937553_1280.jpg');
                background-size: cover;
                background-attachment: fixed;
                background-position: center;
                color: #f0f0f0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
            }

            /* กล่องเนื้อหา */
            .container {
                max-width: 800px;
                margin: 100px auto;
                background: rgba(0, 0, 0, 0.6);
                padding: 20px 30px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7);
                animation: fadeIn 1.5s ease-in-out;
            }

            h1 {
                font-size: 2.5em;
                text-align: center;
                color: #ff9800;
                margin-bottom: 20px;
            }

            p {
                font-size: 1.2rem;
                line-height: 1.8;
                margin-bottom: 20px;
            }

            button {
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(45deg, #ff9800, #e65100);
                color: #fff;
                font-size: 1.2rem;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                margin-top: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }

            button:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            }

            /* Keyframe Animation */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .container {
                    margin: 50px 10px;
                    padding: 20px;
                }

                h1 {
                    font-size: 2rem;
                }

                p {
                    font-size: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ความหวังสุดท้าย</h1>
            <p>ท่ามกลางความสิ้นหวังที่ปกคลุมโลกหลังการระบาดของโรคร้ายไนท์ชาโดว์ข่าวลือหนึ่งเริ่มแพร่สะพัดในหมู่ผู้รอดชีวิต มันคือเรื่องราวของงานวิจัยลับที่ถูกจัดทำขึ้นเมื่อหลายสิบปีก่อน ณ มหาวิทยาลัยเทคโนโลยีสุรนารี</p>
            <p>งานวิจัยชิ้นนี้เป็นผลงานของ ศ.ดร.ปณชัย นักวิทยาศาสตร์อัจฉริยะผู้เป็นที่เลื่องลือในด้านการพัฒนายารักษาโรคระบาด ว่ากันว่าเขาเคยคาดการณ์ถึงการเกิดโรคร้ายแรงนี้ไว้ล่วงหน้ก _และได้ค้นพบวิธีรักษาโรคไนท์ชาโดว์ที่สามารถช่วยมนุษยชาติได้</p>
            <p>อย่างไรก็ตาม เพื่อป้องกันไม่ให้ข้อมูลสำคัญตกไปอยู่ในมือของผู้ไม่หวังดี ศ.ดร.ปณชัย จึงได้ขอความร่วมมือกับ ศ.ดร.ศิขเรศ ผู้เชี่ยวชาญด้านความปลอดภัยทางไซเบอร์ระดับโลก ให้เข้ารหัสข้อมูลงานวิจัยนี้อย่างซับซ้อน โดยเรียกโปรเจคลับนี้ว่า "โปรเจคไนท์โค้ด" และซ่อนมันไว้ในห้องลับ ณ สถาบันวิจัยแสงซินโครตรอน</p>
            <button onclick="window.location.href='/story/page3'">ถัดไป</button>
        </div>
    </body>
    </html>
    """
@app.route("/story/page3", methods=["GET"])
def story_page3():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>เริ่มภารกิจ</title>
        <style>
            /* พื้นหลังวิดีโอ */
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: Arial, sans-serif;
                color: #fff;
            }
            .video-background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: -1;
            }

            /* กล่องเนื้อหา */
            .container {
                max-width: 800px;
                margin: 100px auto;
                background: rgba(0, 0, 0, 0.7);
                padding: 30px 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
                animation: fadeIn 1.5s ease-in-out;
                text-align: left; /* จัดตำแหน่งเนื้อหาและปุ่มให้ชิดซ้าย */
            }

            h1 {
                font-size: 2.8em;
                color: #ffcc00;
                margin-bottom: 20px;
                text-align: center; /* หัวข้อยังคงอยู่ตรงกลาง */
            }

            p {
                font-size: 1.2em;
                line-height: 1.8;
                margin-bottom: 20px;
                text-align: justify;
            }

            /* ปุ่ม */
            button {
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(45deg, #ff9800, #e65100);
                color: #fff;
                font-size: 1.2rem;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                margin-top: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }

            button:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            }

            /* เอฟเฟกต์เฟดอิน */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .container {
                    margin: 50px 10px;
                    padding: 20px;
                }

                h1 {
                    font-size: 2.2em;
                }

                p {
                    font-size: 1rem;
                }

                button {
                    font-size: 1rem;
                    padding: 10px 20px;
                }
            }
        </style>
    </head>
    <body>
        <!-- วิดีโอพื้นหลัง -->
        <video autoplay muted loop class="video-background">
            <source src="/static/images/201625-916080356_small.mp4" type="video/mp4">
            เบราว์เซอร์ของคุณไม่รองรับวิดีโอ
        </video>

        <!-- เนื้อหา -->
        <div class="container">
            <h1>โครงข่ายไนท์โค้ด</h1>
            <p>เพื่อปกป้องข้อมูลงานวิจัย ศ.ดร.ศิขเรศ ได้เข้ารหัสงานวิจัยดังกล่าวด้วยวิธีที่ซับซ้อน โดยผสานการเข้ารหัส Symmetric, Asymmetric Cryptography และ Hash Function เข้าไว้ด้วยกัน</p>
            <p>ความซับซ้อนของโปรเจคไนท์โค้ดทำให้งานวิจัยนี้แทบจะเป็นไปไม่ได้ในการเข้าถึง อย่างไรก็ตาม ศ.ดร.ศิขเรศ ได้มอบรหัสสำคัญสำหรับเข้าสู่ห้องลับให้กับ ศ.ดร.ปณชัย เพียงผู้เดียว เพื่อให้แน่ใจว่าข้อมูลจะถูกปกป้องอย่างปลอดภัยสูงสุด</p>
            <button onclick="window.location.href='/story/page4'">ถัดไป</button>
        </div>
    </body>
    </html>
    """
@app.route("/story/page4", methods=["GET"])
def story_page4():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CTF Story - Page 3</title>
        <style>
            /* พื้นหลังและฟอนต์ */
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-image: url('https://cdn.pixabay.com/photo/2020/03/12/06/12/coronavirus-4924022_1280.jpg');
                background-size: cover;
                background-attachment: fixed;
                background-position: center;
                color: #f0f0f0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
            }

            /* กล่องเนื้อหา */
            .container {
                max-width: 800px;
                margin: 100px auto;
                background: rgba(0, 0, 0, 0.7);
                padding: 30px 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
                animation: fadeIn 1.5s ease-in-out;
            }

            h1 {
                font-size: 2.8em;
                text-align: center;
                color: #ffcc00;
                margin-bottom: 20px;
            }

            p {
                font-size: 1.2em;
                line-height: 1.8;
                margin-bottom: 20px;
                text-align: justify;
            }

            /* ปุ่ม */
            button {
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(45deg, #ff9800, #e65100);
                color: #fff;
                font-size: 1.2em;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                transition: transform 0.3s, box-shadow 0.3s;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                margin-top: 20px;
            }

            button:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
            }

            /* เอฟเฟกต์เฟดอิน */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .container {
                    margin: 50px 10px;
                    padding: 20px;
                }

                h1 {
                    font-size: 2.2em;
                }

                p {
                    font-size: 1rem;
                }

                button {
                    font-size: 1rem;
                    padding: 10px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>บทบาทของคุณ</h1>
            <p>คุณคือ ธนวัฒน์ หนุ่มวัยกลางคน ผู้เชี่ยวชาญด้านการเข้ารหัสและระบบความปลอดภัยทางดิจิทัล ด้วยความสามารถและประสบการณ์คุณเป็นหนึ่งในไม่กี่คนที่ยังคงรักษาความหวังของมนุษยชาติผ่านทักษะด้านเทคโนโลยี</p>
            <p>วันหนึ่งคุณได้รับการติดต่อจาก ศ.ดร.ปณชัย ณ ขณะนี้เป็นชายชราอาศัยอยู่ในเขตปลอดภัยสำหรับผู้ลี้ภัย แต่ด้วยผลกระทบจากความเครียดในยุคหลังวันสิ้นโลกและอายุที่มากขึ้น เขาได้สูญเสียความทรงจำบางส่วนเกี่ยวกับรหัสที่ใช้ในการเข้าถึงงานวิจัยลับ</p>
            <p> "ฉันลืมมันไปเกือบหมดแล้ว... แต่ฉันยังเชื่อว่ายังมีผู้ที่ถอดรหัสมันได้" ศ.ดร.ปณชัย กล่าวด้วยน้ำเสียงที่สะท้อนถึงทั้งความหวังและความกังวล </p>
            <p> และมอบหมายภารกิจสำคัญ เพื่อเข้าถึงงานวิจัยที่อาจเป็นกุญแจสำคัญในการฟื้นฟูโลก </p>
            <button onclick="window.location.href='/start_ctf'">เริ่มภารกิจ</button>
        </div>
    </body>
    </html>
    """
@app.route("/start_ctf", methods=["GET", "POST"])
def start_ctf():
    # ตรวจสอบสถานะปัจจุบันใน session
    if "current_level" not in session or session["current_level"] >= len(QUESTIONS):
        session["current_level"] = 0  # เริ่มที่ข้อแรกเสมอ

    # หากทำครบทุกข้อแล้ว ให้เปลี่ยนเส้นทางไปยังหน้าความสำเร็จ
    if session["current_level"] >= len(QUESTIONS):
        return redirect(url_for("congratulations"))

    # หน้า HTML สำหรับเริ่มภารกิจพร้อมวิดีโอพื้นหลัง
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>เริ่มภารกิจ</title>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: Arial, sans-serif;
                color: #fff;
            }
            .video-background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                z-index: -1;
            }
            .container {
                position: relative;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
                color: #4caf50;
            }
            p {
                font-size: 1.2em;
                line-height: 1.6;
                margin-bottom: 20px;
            }
            button {
                background: #4caf50;
                color: white;
                padding: 15px 30px;
                font-size: 1.2em;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <!-- วิดีโอพื้นหลัง -->
        <video autoplay muted loop class="video-background">
            <source src="static/images/153079-804706258_small.mp4" type="video/mp4">
            เบราว์เซอร์ของคุณไม่รองรับวิดีโอ
        </video>

        <!-- เนื้อหา -->
        <div class="container">
            <h1>ภารกิจเริ่มต้นแล้ว!</h1>
            <p>คุณพร้อมที่จะถอดรหัสและช่วยโลกหรือยัง?</p>
            <button onclick="window.location.href='/ctf_challenge'">เริ่มภารกิจ</button>
        </div>
    </body>
    </html>
    """


@app.route("/ctf_challenge", methods=["GET", "POST"])
def ctf_challenge():
    current_level = session.get("current_level", 0)

    if current_level >= len(QUESTIONS):
        return redirect(url_for("congratulations"))

    question_data = QUESTIONS[current_level]
    data = question_data["data"]()

    result = None
    if request.method == "POST":
        user_answer = request.form.get("answer")
        if user_answer == data["answer"]:
            session["current_level"] += 1
            if session["current_level"] >= len(QUESTIONS):
                return redirect(url_for("congratulations"))
            return redirect(url_for("popup"))
        else:
            result = "❌ คำตอบไม่ถูกต้อง ลองอีกครั้ง!"

    html_template = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CTF Challenge</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
            }}
            .container {{
                max-width: 700px;
                padding: 30px;
                background: rgba(0, 0, 0, 0.85);
                border-radius: 12px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
                animation: fadeIn 1.2s ease-in-out;
            }}
            h1 {{
                font-size: 2.5rem;
                color: #ffcc00;
                margin-bottom: 15px;
            }}
            p, ul {{
                font-size: 1.2rem;
                color: #e0e0e0;
                margin-bottom: 20px;
                text-align: left;
            }}
            ul {{
                padding-left: 20px;
            }}
            form {{
                margin-top: 20px;
            }}
            input[type="text"] {{
                width: 100%;
                max-width: 500px;
                padding: 10px;
                margin-bottom: 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 1rem;
            }}
            button {{
                background: linear-gradient(45deg, #ff9800, #e65100);
                padding: 12px 30px;
                border: none;
                color: #fff;
                font-size: 1rem;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            button:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
            }}
            .feedback {{
                font-size: 1.2rem;
                color: #ff5555;
                margin-top: 20px;
            }}
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CTF Challenge</h1>
    """

    if question_data["id"] == 1:
        html_template += f"""
            <p>-----------------------------------------------------------------------------------------------</p>
            <p><b>ลองค้นหาวันที่ที่เกี่ยวข้องกับการเริ่มต้นของ มทส. รูปแบบ DDMMYYYY แล้วนำไปแปลงเป็นรหัส hash แบบ SHA-256</b></p>
            <p>เว็บไซต์: <a href="https://emn178.github.io/online-tools/sha256.html" target="_blank">Online hash calculator</a></p>
            <p>-----------------------------------------------------------------------------------------------</p>
            <p>รูปแบบคำตอบ: "Flag(Your_Answer)"</p>
        """
    elif question_data["id"] == 2:
        html_template += f"""
            <p>ข้อความถูกเข้ารหัสไว้ในรูปแบบ Base64: <b>h5HY9Wyh/3u426gjUX6zOw==</b></p>
            <p>-----------------------------------------------------------------------------------------------</p>
            <p>วิธีการเข้ารหัส: AES-128</p>
            <p>โหมด: CBC</p>
            <p>Initialization Vector (IV): <b>58C7C87AD161ABBD</b></p>
            <p>คำใบ้สำหรับกู้คืนคีย์: <b>834E4__FA38AAA39</b> (รหัสหายไป 2 ตัว)</p>
            <ul>
                <li><a href="static/images/image2.png" download>ดาวน์โหลด รูปไขปริศนา.pdf</a></li>
            </ul>
            <p>เว็บไซต์: <a href="https://www.devglan.com/online-tools/aes-encryption-decryption" target="_blank">online-tools/aes</a></p>
            <p>-----------------------------------------------------------------------------------------------</p>
            <p>รูปแบบคำตอบ: "Flag(Your_Answer)"</p>
        """
    elif question_data["id"] == 3:
        html_template += f"""
            <p>ถอดรหัสไฟล์ PublicKey.pdf และ CipherText.pdf</p>
            <p>-----------------------------------------------------------------------------------------------</p>
            <p>คำใบ้: </p>
            <ul>
                <li><a href="static/images/PublicKey.pdf" download>ดาวน์โหลด PublicKey.pdf</a></li>
                <li><a href="static/images/CipherText.pdf" download>ดาวน์โหลด CipherText.pdf</a></li>
            </ul>
            <p>ตำแหน่งแรกของ ID: จำนวน Router ในพื้นที่ F11 ชั้น 4</p>
            <p>ตำแหน่งสุดท้ายของ ID: ตัวเลขตำแหน่งสุดท้ายของ Mac Address ของ Router ที่อยู่ในพื้นที่วงกลมที่สูงที่สุด ณ สถานที่ที่เต็มไปด้วยหนังสือ</p>
            <p><a href="https://apmap.sut.ac.th/" target="_blank">SUT Router</a></p>
            <p>ถูกเข้ารหัสแบบ: RSA </p>
             <p>เว็บไซต์: <a href="https://www.devglan.com/online-tools/rsa-encryption-decryption" target="_blank">online-tools/rsa</a></p>
            <p>-----------------------------------------------------------------------------------------------</p>
            <p>คุณต้องหา Public Key จากไฟล์ PublicKey.pdf และนำไปถอดรหัสไฟล์ CipherText.pdf ในไฟล์นั้นจะมี Answer และ Sign ให้นำทั้งสองส่วนมาต่อกันเพื่อสร้างรหัสผ่านสำหรับเข้าสู่ขั้นตอนถัดไป</p>
            
            <p>รูปแบบคำตอบ: "Flag(Your_Answer) โดยไม่มีเว้นวรรค"</p>
        """
    elif question_data["id"] == 4:
        html_template += f"""
            <p>คุณได้รับไฟล์ที่เข้ารหัส AES-256</p>
            <p>-----------------------------------------------------------------------------------------------</p>
            <li><a href="static/images/Answer.dat" download>ดาวน์โหลด Answer.dat</a></li>
            <p>แนะนำ: <a href="https://emn178.github.io/online-tools/aes/decrypt/" target="_blank">AES Decrypt Tool</a></p>
            <p>คำใบ้: </p>
            <ul>
                <li>Input type: File</li>
                <li>File Name: เปลี่ยนชื่อไฟล์เป็น .png</li>
                <li>Key: 256 bit</li>
                <li>Mode: : 43 54 42 ฐาน 16 </li>
                <li>Hash: MD5</li>
            </ul>
            <p>-----------------------------------------------------------------------------------------------</p>
            <p>รูปแบบคำตอบ: "Flag(Your_Answer) ภาษาไทย"</p>
        """

    html_template += """
            <form method="POST">
                <input type="text" name="answer" placeholder="กรอกคำตอบของคุณที่นี่" required>
                <button type="submit">ส่งคำตอบ</button>
            </form>
    """
    if result:
        html_template += f"<div class='feedback'>{result}</div>"
    html_template += """
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)



# ฟังก์ชันสำหรับ Popup
@app.route("/popup")
def popup():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CTF Challenge</title>
        <script>
            alert("Congratulations! You passed this level!");
            window.location.href = "/ctf_challenge";
        </script>
    </head>
    <body></body>
    </html>
    """

# ฟังก์ชันแสดงความยินดี
@app.route("/congratulations")
def congratulations():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ภารกิจสำเร็จ</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(to bottom, #121212, #1e1e1e);
                color: #ffffff;
                text-align: center;
            }
            .container {
                max-width: 800px;
                margin: 100px auto;
                padding: 40px;
                background: rgba(0, 0, 0, 0.9);
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
                animation: fadeIn 1.5s ease-in-out;
            }
            h1 {
                font-size: 3rem;
                color: #ffc107;
                text-shadow: 0px 5px 15px rgba(255, 193, 7, 0.6);
                margin-bottom: 20px;
            }
            p {
                font-size: 1.2rem;
                line-height: 1.8;
                margin-bottom: 30px;
                color: #e0e0e0;
            }
            img {
                width: 80%;
                max-width: 500px;
                height: auto;
                margin: 20px auto;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 15px 30px;
                font-size: 1.2rem;
                font-weight: bold;
                text-decoration: none;
                color: #fff;
                background: linear-gradient(45deg, #28a745, #218838);
                border-radius: 8px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.5);
                transition: all 0.3s ease-in-out;
            }
            a:hover {
                background: linear-gradient(45deg, #34d058, #28a745);
                transform: translateY(-5px);
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            @media (max-width: 768px) {
                .container {
                    margin: 50px 10px;
                    padding: 20px;
                }
                h1 {
                    font-size: 2rem;
                }
                p {
                    font-size: 1rem;
                }
                img {
                    width: 90%;
                }
                a {
                    font-size: 1rem;
                    padding: 10px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1><b>คุณถอดรหัสสำเร็จ!!!</b></h1>
            <p>แต่มีสิ่งที่ไม่คากคิด ไฟล์งานวิจัยลับ ทั้งหมดถูกกลุ่มไม่หวังดีได้ทำการเปลี่ยนข้อมูลภายใน</p>
            <img src="/static/images/image.png" alt="Congratulations Image">
            <p>นี่คือไฟล์ที่กลุ่มผู้ไม่หวังดีทิ้งเอาไว้</p>
            <p>โปรดติดตามตอนต่อไป</p>
            <a href="/">เริ่มต้นใหม่</a>
        </div>
    </body>
    </html>
    """



if __name__ == "__main__":
    app.run(port=5000, debug=True)
