from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import os, hashlib, json, base64, hmac, time, re
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = "mega-ctf-secret-2024"

# ─── FLAGS ───────────────────────────────────────────────
FLAGS = {
    1: "FLAG{f1l3_upl04d_pwn3d}",
    2: "FLAG{brut3_f0rc3_succ3ss}",
    3: "FLAG{jwt_4lg_n0n3_byp4ss}",
    4: "FLAG{l0g_4n4lys1s_m4st3r}",
    5: "FLAG{y0u_4r3_4_r34l_h4ck3r}",
}

# ─── USERS for Brute Force level ─────────────────────────
USERS = {
    "admin": "password123",
    "user":  "letmein",
    "test":  "abc123",
}

# ─── JWT helpers (custom, intentionally weak) ─────────────
def b64url(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def make_jwt(payload, secret="supersecret", alg="HS256"):
    header  = b64url(json.dumps({"alg": alg, "typ": "JWT"}))
    body    = b64url(json.dumps(payload))
    sig_input = f"{header}.{body}".encode()
    if alg.upper() == "NONE":
        sig = ""
    else:
        sig = b64url(hmac.new(secret.encode(), sig_input, "sha256").digest())
    return f"{header}.{body}.{sig}"

def decode_jwt(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None, "Invalid token format"
        header  = json.loads(base64.urlsafe_b64decode(parts[0] + "=="))
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
        alg = header.get("alg", "").upper()
        if alg == "NONE":
            return payload, None          # ← intentional vulnerability
        sig_input = f"{parts[0]}.{parts[1]}".encode()
        expected  = b64url(hmac.new(b"supersecret", sig_input, "sha256").digest())
        if parts[2] != expected:
            return None, "Invalid signature"
        return payload, None
    except Exception as e:
        return None, str(e)

# ─── Sample logs ──────────────────────────────────────────
SAMPLE_LOGS = """2024-01-15 08:23:11 INFO  User 'guest' logged in from 192.168.1.10
2024-01-15 08:45:33 WARN  Failed login attempt for user 'admin' from 10.0.0.5
2024-01-15 09:01:02 INFO  File uploaded: report.pdf by user 'guest'
2024-01-15 09:15:44 ERROR Suspicious file upload attempt: shell.php from 10.0.0.5
2024-01-15 09:16:01 WARN  Failed login attempt for user 'admin' from 10.0.0.5
2024-01-15 09:16:45 WARN  Failed login attempt for user 'admin' from 10.0.0.5
2024-01-15 09:17:03 WARN  Failed login attempt for user 'admin' from 10.0.0.5
2024-01-15 09:17:22 SUCCESS User 'admin' logged in from 10.0.0.5
2024-01-15 09:18:05 INFO  Admin panel accessed from 10.0.0.5
2024-01-15 09:19:11 INFO  Secret file read: /etc/passwd from 10.0.0.5
2024-01-15 09:20:00 INFO  FLAG_IN_LOG=FLAG{l0g_4n4lys1s_m4st3r} accessed by attacker
2024-01-15 10:00:00 INFO  System backup completed successfully"""

def get_solved():
    return session.get("solved", [])

def mark_solved(level):
    solved = get_solved()
    if level not in solved:
        solved.append(level)
    session["solved"] = solved

# ══════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", solved=get_solved(), total=5, flags=FLAGS)

# ── LEVEL 1: File Upload ──────────────────────────────────
@app.route("/level/1")
def level1():
    files = os.listdir("uploads/level1") if os.path.exists("uploads/level1") else []
    return render_template("level1.html", solved=get_solved(), files=files, flag=FLAGS[1])

@app.route("/upload/1", methods=["POST"])
def upload1():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    f = request.files["file"]
    filename = secure_filename(f.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    os.makedirs("uploads/level1", exist_ok=True)
    f.save(f"uploads/level1/{filename}")
    shell_exts = ["php","php5","phtml","phar","py","sh","rb","jsp"]
    if ext in shell_exts:
        mark_solved(1)
        return jsonify({"success": True, "flag": FLAGS[1],
                        "message": f"Shell uploaded! Access: /uploads/level1/{filename}"})
    return jsonify({"success": True, "message": f"Uploaded: {filename}"})

@app.route("/uploads/level1/<path:filename>")
def serve_upload(filename):
    path = f"uploads/level1/{filename}"
    if not os.path.exists(path):
        return "Not found", 404
    with open(path, "r", errors="replace") as fh:
        content = fh.read()
    return f"<pre style='background:#111;color:#0f0;padding:20px'>{content}</pre>"

# ── LEVEL 2: Brute Force ──────────────────────────────────
@app.route("/level/2")
def level2():
    return render_template("level2.html", solved=get_solved(), flag=FLAGS[2])

@app.route("/bruteforce/login", methods=["POST"])
def bf_login():
    data = request.get_json() or {}
    username = data.get("username","")
    password = data.get("password","")
    if username in USERS and USERS[username] == password:
        if username == "admin":
            mark_solved(2)
            return jsonify({"success": True, "flag": FLAGS[2],
                            "message": f"Welcome admin! You cracked it."})
        return jsonify({"success": True, "message": f"Logged in as {username} — but find ADMIN!"})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ── LEVEL 3: JWT ──────────────────────────────────────────
@app.route("/level/3")
def level3():
    token = make_jwt({"user": "guest", "role": "user"})
    return render_template("level3.html", solved=get_solved(), token=token, flag=FLAGS[3])

@app.route("/jwt/verify", methods=["POST"])
def jwt_verify():
    data  = request.get_json() or {}
    token = data.get("token","")
    payload, err = decode_jwt(token)
    if err:
        return jsonify({"error": err}), 400
    if payload.get("role") == "admin":
        mark_solved(3)
        return jsonify({"success": True, "flag": FLAGS[3],
                        "message": "Admin access granted!", "payload": payload})
    return jsonify({"success": False,
                    "message": f"Access denied. You are: {payload.get('role','unknown')}",
                    "payload": payload})

# ── LEVEL 4: Log Analysis ─────────────────────────────────
@app.route("/level/4")
def level4():
    return render_template("level4.html", solved=get_solved(),
                           logs=SAMPLE_LOGS, flag=FLAGS[4])

@app.route("/log/answer", methods=["POST"])
def log_answer():
    data = request.get_json() or {}
    answers = {
        "q1": "10.0.0.5",
        "q2": "4",
        "q3": "shell.php",
        "q4": FLAGS[4],
    }
    q  = data.get("question","")
    ans = data.get("answer","").strip()
    correct = answers.get(q,"")
    if ans == correct:
        if q == "q4":
            mark_solved(4)
            return jsonify({"correct": True, "flag": FLAGS[4],
                            "message": "Level 4 complete!"})
        return jsonify({"correct": True, "message": "Correct!"})
    return jsonify({"correct": False, "message": "Wrong answer, try again."})

# ── LEVEL 5: Final CTF ────────────────────────────────────
@app.route("/level/5")
def level5():
    solved = get_solved()
    unlocked = len(solved) >= 4
    return render_template("level5.html", solved=solved,
                           unlocked=unlocked, flag=FLAGS[5])

@app.route("/ctf/submit", methods=["POST"])
def ctf_submit():
    data = request.get_json() or {}
    flag = data.get("flag","").strip()
    # Hidden flag is encoded in base64 in the page source
    if flag == FLAGS[5] or flag == "HACK3R_KING":
        mark_solved(5)
        return jsonify({"success": True, "flag": FLAGS[5],
                        "message": "Congratulations! You are a real hacker!"})
    return jsonify({"success": False, "message": "Wrong flag!"})

@app.route("/reset")
def reset():
    session.clear()
    import shutil
    if os.path.exists("uploads/level1"):
        shutil.rmtree("uploads/level1")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
