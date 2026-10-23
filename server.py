# -*- coding: utf-8 -*-
"""Доска: данные лежат в одном файле рядом с программой."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import base64
import calendar
import json
import re
import urllib.request
from datetime import date
import hashlib
import hmac
import os
import sqlite3
import threading
import time
import urllib.parse

ROOT = Path(__file__).resolve().parent
STATE = Path(os.environ.get("DOSKA_STATE") or str(ROOT / "example-board.json"))
SQLITE = os.environ.get("DOSKA_SQLITE") or ""
HOST = os.environ.get("HOST") or "127.0.0.1"
PORT = int(os.environ.get("PORT") or "8765")
_write_lock = threading.Lock()

DEFAULT_HABITS = [
    "Утренняя разминка",
    "Чтение",
    "Планирование дня",
]


def _month_key(day: date | None = None) -> str:
    day = day or date.today()
    return f"{day.year:04d}-{day.month:02d}"


def _days_in(month_key: str) -> int:
    year, month = (int(x) for x in month_key.split("-"))
    return calendar.monthrange(year, month)[1]


def fx_rates() -> dict:
    with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rates = payload["rates"]
    return {"USD": 1, "RUB": float(rates["RUB"]), "EUR": float(rates["EUR"])}


def _days_left(due: str, done: bool) -> int | None:
    if done or not due:
        return None
    try:
        year, month, day = (int(x) for x in due.split("-"))
        return (date(year, month, day) - date.today()).days
    except ValueError:
        return None


def parse_note(text: str) -> dict:
    boards = []
    habits = []
    logs = []
    month = _month_key()
    current = None
    parent = ""
    mode = "tasks"
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("# Привычки"):
            mode = "habits"
            current = None
            continue
        if line.startswith("# Занятость"):
            mode = "time"
            current = None
            continue
        if mode == "habits" and re.match(r"^##\s+\d{4}-\d{2}$", line):
            month = line[3:].strip()
            continue
        if mode == "tasks" and line.startswith("### "):
            current = {"title": line[4:].strip(), "parent": parent, "items": []}
            boards.append(current)
            continue
        if mode == "tasks" and line.startswith("## "):
            parent = line[3:].strip()
            current = {"title": parent, "parent": "", "items": []}
            boards.append(current)
            continue
        if mode == "tasks" and current is not None:
            item = re.match(r"^-\s+\[( |x|X)\]\s+(.+)$", line)
            if not item:
                continue
            done = item.group(1).lower() == "x"
            parts = [p.strip() for p in item.group(2).split("|")]
            title = parts[0]
            due = ""
            comment = ""
            rest = parts[1:]
            if rest and re.match(r"\d{4}-\d{2}-\d{2}$", rest[0]):
                due = rest[0]
                rest = rest[1:]
            if rest:
                comment = "|".join(rest).strip()
            current["items"].append({"text": title, "done": done, "due": due, "comment": comment})
            continue
        if mode == "habits":
            habit = re.match(r"^-\s+([^|]+)\|\s*([01]*)\s*$", line)
            if habit:
                marks = list(habit.group(2))
                habits.append({"name": habit.group(1).strip(), "marks": marks})
            continue
        if mode == "time":
            parts = [p.strip() for p in line[1:].split("|")] if line.startswith("-") else []
            if len(parts) >= 4 and re.match(r"\d{4}-\d{2}-\d{2}$", parts[0]) and parts[1].isdigit():
                clock = ""
                text = ""
                if len(parts) >= 5 and re.match(r"\d{2}:\d{2}$", parts[3]):
                    clock = parts[3]
                    text = "|".join(parts[4:]).strip()
                else:
                    text = "|".join(parts[3:]).strip()
                logs.append({
                    "date": parts[0],
                    "minutes": int(parts[1]),
                    "direction": parts[2],
                    "clock": clock,
                    "text": text,
                })
    if not habits:
        habits = [{"name": name, "marks": []} for name in DEFAULT_HABITS]
    return {"boards": boards, "habits": habits, "month": month, "logs": logs, "journal": {}}


def _sqlite():
    SQLITE_PATH = Path(SQLITE)
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(SQLITE_PATH, timeout=15)
    con.execute("CREATE TABLE IF NOT EXISTS board (id INTEGER PRIMARY KEY CHECK (id = 1), body TEXT NOT NULL)")
    return con


def load_data() -> dict:
    if SQLITE:
        con = _sqlite()
        row = con.execute("SELECT body FROM board WHERE id = 1").fetchone()
        con.close()
        if row:
            data = json.loads(row[0])
            data.setdefault("_rev", 1)
            data.setdefault("updatedAt", "")
            return data
    if STATE.exists():
        data = json.loads(STATE.read_text(encoding="utf-8"))
        if "_rev" not in data:
            data["_rev"] = 1
        if "updatedAt" not in data:
            data["updatedAt"] = ""
        return data
    data = {"boards": [], "habits": [], "month": _month_key(), "logs": [], "journal": {}}
    save_data(data)
    return data


def save_data(data: dict) -> None:
    data.setdefault("_rev", 1)
    data.setdefault("updatedAt", "")
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    if SQLITE:
        con = _sqlite()
        con.execute("INSERT INTO board (id, body) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET body = excluded.body", (raw,))
        con.commit()
        con.close()
        return
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(raw, encoding="utf-8")


def _fal_key() -> str:
    path = Path(os.environ.get("DOSKA_FAL_ENV") or "/var/lib/doska/fal.env")
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, val = line.split("=", 1)
        if name.strip() == "FAL_KEY":
            return val.strip().strip('"').strip("'")
    return ""


def _deepseek_key() -> str:
    path = Path(os.environ.get("DOSKA_DEEPSEEK_ENV") or "/var/lib/doska/deepseek.env")
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, val = line.split("=", 1)
        if name.strip() == "DEEPSEEK_API_KEY":
            return val.strip().strip('"').strip("'")
    return ""


def transcribe_audio(audio: bytes, mime: str) -> str:
    key = _fal_key()
    if not key:
        raise RuntimeError("нет ключа распознавания")
    if not audio or len(audio) > 1_500_000:
        raise RuntimeError("запись пустая или слишком длинная")
    kind = (mime or "audio/webm").split(";")[0].strip() or "audio/webm"
    ext = "m4a" if "mp4" in kind or "m4a" in kind else "webm" if "webm" in kind else "wav"
    init_body = json.dumps({"file_name": "voice." + ext, "content_type": kind}).encode("utf-8")
    init_req = urllib.request.Request(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        data=init_body,
        headers={"Authorization": "Key " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(init_req, timeout=30) as res:
        slot = json.loads(res.read().decode("utf-8"))
    put = urllib.request.Request(slot["upload_url"], data=audio, method="PUT", headers={"Content-Type": kind})
    with urllib.request.urlopen(put, timeout=60):
        pass
    body = json.dumps({
        "audio_url": slot["file_url"],
        "task": "transcribe",
        "language": "ru",
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://fal.run/fal-ai/whisper",
        data=body,
        headers={"Authorization": "Key " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as res:
        payload = json.loads(res.read().decode("utf-8"))
    return (payload.get("text") or "").strip()


def _ask_model(system: str, user: str) -> str:
    key = _deepseek_key()
    if not key:
        raise RuntimeError("нет ключа")
    body = json.dumps({
        "model": "deepseek-flash",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=40) as res:
        payload = json.loads(res.read().decode("utf-8"))
    return (((payload.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()


def _board_brief(data: dict) -> str:
    today = date.today().isoformat()
    lines = ["Сегодня " + today]
    for group in data.get("boards") or []:
        title = group.get("title") or ""
        if group.get("parent"):
            title = group.get("parent") + " / " + title
        for item in group.get("items") or []:
            if item.get("done"):
                continue
            due = (item.get("due") or "").strip()
            text = (item.get("text") or "").replace("\n", " ").strip()
            if not text:
                continue
            if due and due < today:
                lines.append(f"Просрочено | {due} | {title} | {text}")
            elif due == today:
                lines.append(f"Сегодня | {title} | {text}")
    note = ((data.get("journal") or {}).get(today) or "").strip()
    if note:
        lines.append("Заметка: " + note[:800])
    return "\n".join(lines)[:6000]


def _inbox(data: dict) -> dict:
    boards = data.setdefault("boards", [])
    for board in boards:
        if not board.get("parent") and board.get("title") == "Входящие":
            board.setdefault("items", [])
            return board
    board = {"title": "Входящие", "parent": "", "items": []}
    boards.insert(0, board)
    return board


def helper_reply(kind: str, text: str) -> dict:
    data = load_data()
    brief = _board_brief(data)
    today = date.today().isoformat()
    if kind == "today":
        answer = _ask_model(
            "Ты помощник личной доски. Отвечай по-русски, коротко. Используй только переданный список. Не выдумывай задачи. Сначала просроченные, потом дела на сегодня, потом есть ли заметка.",
            brief + "\n\nВопрос: что сегодня на доске?",
        )
        return {"ok": True, "message": answer}
    if kind == "task":
        if not text.strip():
            return {"ok": False, "message": "Напиши, какую задачу поставить."}
        raw = _ask_model(
            "Верни только JSON {\"text\":\"короткая задача\",\"due\":\"YYYY-MM-DD или пусто\"}. due пустой, если срока нет. Не добавляй пояснений.",
            "Сегодня " + today + ".\n" + text.strip(),
        )
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if "\n" in cleaned:
                cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.replace("json", "", 1).strip().strip("`")
        try:
            obj = json.loads(cleaned)
            task = str(obj.get("text") or "").strip() or text.strip()
            due = str(obj.get("due") or "").strip()
        except json.JSONDecodeError:
            task, due = text.strip(), ""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due):
            due = ""
        item = {"text": task, "done": False, "due": due, "comment": ""}
        with _write_lock:
            fresh = load_data()
            _inbox(fresh).setdefault("items", []).append(item)
            fresh["_rev"] = int(fresh.get("_rev") or 1) + 1
            fresh["updatedAt"] = today
            save_data(fresh)
        when = " на " + due if due else ""
        return {"ok": True, "message": "Поставил во входящие" + when + ": " + task}
    if kind == "note":
        if not text.strip():
            return {"ok": False, "message": "Напиши, что записать."}
        note = _ask_model(
            "Оформи короткую заметку в дневник от первого лица. Верни только текст заметки, без заголовка и кавычек.",
            text.strip(),
        ) or text.strip()
        with _write_lock:
            fresh = load_data()
            journal = fresh.setdefault("journal", {})
            old = (journal.get(today) or "").strip()
            journal[today] = (old + "\n\n" + note).strip() if old else note
            fresh["_rev"] = int(fresh.get("_rev") or 1) + 1
            fresh["updatedAt"] = today
            save_data(fresh)
        return {"ok": True, "message": "Записал в дневник на сегодня."}
    return {"ok": False, "message": "Не понял действие."}
    data.setdefault("_rev", 1)
    data.setdefault("updatedAt", "")
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    if SQLITE:
        con = _sqlite()
        con.execute("INSERT INTO board (id, body) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET body = excluded.body", (raw,))
        con.commit()
        con.close()
        return
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(raw, encoding="utf-8")


def render_note(data: dict) -> str:
    boards = data.get("boards") or []
    habits = data.get("habits") or []
    month = data.get("month") or _month_key()
    lines = ["# Доска направлений", ""]
    for board in boards:
        title = (board.get("title") or "").strip()
        if not title:
            continue
        parent = (board.get("parent") or "").strip()
        lines.append(f"### {title}" if parent else f"## {title}")
        for item in board.get("items") or []:
            text = (item.get("text") or "").strip()
            if not text:
                continue
            mark = "x" if item.get("done") else " "
            due = (item.get("due") or "").strip()
            comment = (item.get("comment") or "").replace("\n", " ").strip()
            tail = f" | {due}" if re.match(r"\d{4}-\d{2}-\d{2}$", due) else ""
            if comment:
                if not tail:
                    tail = " |"
                tail += f" | {comment}"
            lines.append(f"- [{mark}] {text}{tail}")
        lines.append("")
    lines.append("# Привычки")
    lines.append(f"## {month}")
    width = _days_in(month)
    for habit in habits:
        name = (habit.get("name") or "").strip()
        if not name:
            continue
        marks = "".join("1" if m in ("1", 1, True) else "0" for m in (habit.get("marks") or []))
        marks = (marks + "0" * width)[:width]
        lines.append(f"- {name} | {marks}")
    lines.append("")
    lines.append("# Занятость")
    for row in data.get("logs") or []:
        text = (row.get("text") or "").replace("|", "/").strip()
        direction = (row.get("direction") or "Другое").replace("|", "/").strip()
        date = (row.get("date") or "").strip()
        try:
            minutes = int(row.get("minutes") or 0)
        except (TypeError, ValueError):
            minutes = 0
        if not re.match(r"\d{4}-\d{2}-\d{2}$", date) or minutes < 0 or not text:
            continue
        clock = (row.get("clock") or "").strip()
        if clock and not re.match(r"\d{2}:\d{2}$", clock):
            clock = ""
        stamp = f" | {clock}" if clock else ""
        lines.append(f"- {date} | {minutes} | {direction}{stamp} | {text}")
    lines.append("")
    lines.append("# Дневник")
    for day, entry in sorted((data.get("journal") or {}).items(), reverse=True):
        text = (entry or "").strip()
        if text:
            lines.append(f"## {day}")
            lines.append(text)
            lines.append("")
    lines.append("# Подписки")
    for item in data.get("subscriptions") or []:
        name = (item.get("name") or "").replace("|", "/").strip()
        if not name:
            continue
        amount = item.get("amount") or 0
        period = "год" if item.get("period") == "yearly" else "месяц"
        next_date = (item.get("next") or "").strip()
        note = (item.get("note") or "").replace("|", "/").strip()
        currency = (item.get("currency") or "RUB").strip()
        lines.append(f"- {name} | {amount} {currency} / {period} | {next_date} | {note}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def auth_on() -> bool:
    return os.environ.get("DOSKA_AUTH") == "1"


def _secret() -> bytes:
    folder = Path(SQLITE).parent if SQLITE else ROOT
    path = Path(os.environ.get("DOSKA_SECRET") or (folder / "session.key"))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(os.urandom(32))
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    return path.read_bytes()


def check_password(stored: str, password: str) -> bool:
    try:
        kind, salt, digest = stored.split("$", 2)
    except ValueError:
        return False
    if kind != "scrypt":
        return False
    got = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt), n=2**14, r=8, p=1, dklen=32)
    return hmac.compare_digest(got.hex(), digest)


def _pack_user(user: str) -> str:
    return base64.urlsafe_b64encode(user.encode("utf-8")).decode("ascii").rstrip("=")


def _unpack_user(packed: str) -> str:
    pad = "=" * (-len(packed) % 4)
    try:
        return base64.urlsafe_b64decode(packed + pad).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return packed


def session_for(user: str) -> str:
    exp = int(time.time()) + 30 * 24 * 3600
    packed = _pack_user(user)
    msg = f"{packed}.{exp}".encode("utf-8")
    sig = hmac.new(_secret(), msg, hashlib.sha256).hexdigest()
    return f"{packed}.{exp}.{sig}"


def user_from_cookie(header: str) -> str:
    token = ""
    for part in (header or "").split(";"):
        part = part.strip()
        if part.startswith("doska="):
            token = urllib.parse.unquote(part.split("=", 1)[1])
    bits = token.split(".")
    if len(bits) != 3:
        return ""
    packed, exp, sig = bits
    msg = f"{packed}.{exp}".encode("utf-8")
    good = hmac.new(_secret(), msg, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(good, sig):
        return ""
    try:
        if int(exp) < time.time():
            return ""
    except ValueError:
        return ""
    return _unpack_user(packed)


def google_cfg() -> dict:
    path = Path(os.environ.get("DOSKA_GOOGLE_ENV") or "/var/lib/doska/google.env")
    cfg = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            cfg[key.strip()] = val.strip().strip('"').strip("'")
    allow = Path("/var/lib/doska/google.allow")
    if allow.is_file() and not cfg.get("DOSKA_GOOGLE_EMAIL"):
        cfg["DOSKA_GOOGLE_EMAIL"] = allow.read_text(encoding="utf-8").strip()
    return cfg


def public_base() -> str:
    return (os.environ.get("DOSKA_PUBLIC_URL") or "http://127.0.0.1:8765").rstrip("/")


def google_ready() -> bool:
    cfg = google_cfg()
    return bool(cfg.get("DOSKA_GOOGLE_CLIENT_ID") and cfg.get("DOSKA_GOOGLE_CLIENT_SECRET"))


def google_userinfo(code: str) -> dict:
    cfg = google_cfg()
    body = urllib.parse.urlencode({
        "code": code,
        "client_id": cfg["DOSKA_GOOGLE_CLIENT_ID"],
        "client_secret": cfg["DOSKA_GOOGLE_CLIENT_SECRET"],
        "redirect_uri": public_base() + "/login/google/callback",
        "grant_type": "authorization_code",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body)
    with urllib.request.urlopen(req, timeout=20) as res:
        token = json.loads(res.read().decode("utf-8"))
    access = token.get("access_token") or ""
    info_req = urllib.request.Request(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": "Bearer " + access},
    )
    with urllib.request.urlopen(info_req, timeout=20) as res:
        return json.loads(res.read().decode("utf-8"))


def google_allowed(info: dict) -> str:
    email = (info.get("email") or "").strip().lower()
    if not email or not info.get("email_verified"):
        return ""
    cfg = google_cfg()
    allowed = (cfg.get("DOSKA_GOOGLE_EMAIL") or "").strip().lower()
    if allowed:
        return email if email == allowed else ""
    if cfg.get("DOSKA_GOOGLE_BIND") == "1":
        path = Path("/var/lib/doska/google.allow")
        path.write_text(email + "\n", encoding="utf-8")
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
        return email
    return ""


def valid_user(name: str, password: str) -> bool:
    if not SQLITE:
        return False
    con = _sqlite()
    con.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, password TEXT NOT NULL)")
    row = con.execute("SELECT password FROM users WHERE name = ?", (name,)).fetchone()
    con.close()
    return bool(row) and check_password(row[0], password)


LOGIN_PAGE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Вход — Доска</title>
<style>
body { margin:0; min-height:100vh; display:grid; place-items:center; background:#14110d; color:#f3ead7; font:16px/1.4 Georgia, serif; }
form { width:min(360px, calc(100vw - 32px)); display:grid; gap:12px; }
h1 { font-weight:500; font-size:28px; margin:0; }
p { margin:0; color:#b7aa96; }
input { font:inherit; padding:10px 12px; border:1px solid #3a3228; background:#1d1914; color:inherit; }
button, a.google { font:inherit; padding:10px 12px; background:#f3ead7; color:#14110d; border:0; cursor:pointer; text-align:center; text-decoration:none; }
a.google { background:transparent; color:#f3ead7; border:1px solid #3a3228; }
.err { color:#e07a5f; min-height:1.2em; }
</style>
</head>
<body>
<form method="post" action="login">
<h1>Доска</h1>
<p>Вход для своих. Новый аккаунт сам не создаётся.</p>
<input name="username" autocomplete="username" placeholder="Логин" required>
<input name="password" type="password" autocomplete="current-password" placeholder="Пароль" required>
<button type="submit">Войти</button>
<a class="google" href="/login/google">Войти через Google</a>
<p class="err">%s</p>
</form>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send(self, code: int, body: bytes, content_type: str, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in extra or []:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str, extra=None):
        self.send_response(302)
        self.send_header("Location", location)
        for key, value in extra or []:
            self.send_header(key, value)
        self.end_headers()

    def _cookie(self, token: str) -> str:
        secure = "; Secure" if os.environ.get("DOSKA_AUTH") == "1" else ""
        if not token:
            return "doska=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0" + secure
        return "doska=" + urllib.parse.quote(token) + "; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000" + secure

    def _state_cookie(self, token: str) -> str:
        secure = "; Secure" if os.environ.get("DOSKA_AUTH") == "1" else ""
        if not token:
            return "gstate=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0" + secure
        return "gstate=" + token + "; HttpOnly; SameSite=Lax; Path=/; Max-Age=600" + secure

    def _google_start(self):
        if not google_ready():
            self._login_page("Google ещё не настроен: нет ключа приложения.")
            return
        state = os.urandom(16).hex()
        cfg = google_cfg()
        query = urllib.parse.urlencode({
            "client_id": cfg["DOSKA_GOOGLE_CLIENT_ID"],
            "redirect_uri": public_base() + "/login/google/callback",
            "response_type": "code",
            "scope": "openid email",
            "state": state,
            "prompt": "select_account",
        })
        self._redirect(
            "https://accounts.google.com/o/oauth2/v2/auth?" + query,
            [("Set-Cookie", self._state_cookie(state))],
        )

    def _google_back(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        state = (query.get("state") or [""])[0]
        code = (query.get("code") or [""])[0]
        got = ""
        for part in (self.headers.get("Cookie") or "").split(";"):
            part = part.strip()
            if part.startswith("gstate="):
                got = part.split("=", 1)[1]
        if not state or not code or not hmac.compare_digest(state, got):
            self._login_page("Вход через Google не сошёлся. Нажми кнопку ещё раз.")
            return
        try:
            info = google_userinfo(code)
        except Exception:
            self._login_page("Google не ответил. Попробуй ещё раз.")
            return
        email = google_allowed(info)
        if not email:
            self._login_page("Этот Google-аккаунт к доске не привязан.")
            return
        self._redirect("/", [
            ("Set-Cookie", self._cookie(session_for("google:" + email))),
            ("Set-Cookie", self._state_cookie("")),
        ])

    def _logged_in(self) -> bool:
        if not auth_on():
            return True
        return bool(user_from_cookie(self.headers.get("Cookie") or ""))

    def _login_page(self, error: str = ""):
        page = (LOGIN_PAGE % error).encode("utf-8")
        self._send(200, page, "text/html; charset=utf-8")

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/login":
            if self._logged_in() and auth_on():
                self._redirect("/")
                return
            self._login_page()
            return
        if path == "/login/google":
            self._google_start()
            return
        if path == "/login/google/callback":
            self._google_back()
            return
        if path == "/logout":
            self._redirect("/login", [("Set-Cookie", self._cookie(""))])
            return
        if not self._logged_in():
            if path.startswith("/api/"):
                self._send(401, b'{"error":"login"}', "application/json; charset=utf-8")
                return
            self._redirect("/login")
            return
        if self.path.startswith("/api/fx"):
            try:
                raw = json.dumps(fx_rates()).encode("utf-8")
            except Exception:
                raw = b'{"error":true}'
            self._send(200, raw, "application/json; charset=utf-8")
            return
        if self.path.startswith("/api/board"):
            data = load_data()
            month = data["month"]
            data["days"] = _days_in(month)
            raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self._send(200, raw, "application/json; charset=utf-8")
            return
        static = {
            "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
            "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
            "/icon.svg": ("icon.svg", "image/svg+xml"),
            "/icon-192.png": ("icon-192.png", "image/png"),
            "/icon-512.png": ("icon-512.png", "image/png"),
            "/vault-guy.png": ("vault-guy.png", "image/png"),
        }
        path = self.path.split("?", 1)[0]
        if path in static:
            name, content_type = static[path]
            self._send(200, (ROOT / name).read_bytes(), content_type)
            return
        self._send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or 0)
        raw_bytes = self.rfile.read(length)
        if path == "/api/voice":
            if not self._logged_in():
                self._send(401, b'{"error":"login"}', "application/json; charset=utf-8")
                return
            try:
                text = transcribe_audio(raw_bytes, self.headers.get("Content-Type") or "audio/webm")
                result = {"ok": True, "text": text, "message": text or "Ничего не разобрал."}
                code = 200
            except Exception:
                result = {"ok": False, "message": "Голос не разобрался. Скажи ещё раз, короче."}
                code = 502
            self._send(code, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return
        raw = raw_bytes.decode("utf-8")
        if path == "/login":
            form = urllib.parse.parse_qs(raw)
            name = (form.get("username") or [""])[0].strip()
            password = (form.get("password") or [""])[0]
            if valid_user(name, password):
                self._redirect("/", [("Set-Cookie", self._cookie(session_for(name)))])
                return
            self._login_page("Не тот логин или пароль.")
            return
        if not self._logged_in():
            self._send(401, b'{"error":"login"}', "application/json; charset=utf-8")
            return
        if path == "/api/helper":
            try:
                payload = json.loads(raw or "{}")
                result = helper_reply(str(payload.get("kind") or ""), str(payload.get("text") or ""))
                code = 200 if result.get("ok") else 400
            except Exception:
                result = {"ok": False, "message": "Помощник сейчас не ответил. Попробуй ещё раз."}
                code = 502
            self._send(code, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return
        if not path.startswith("/api/board"):
            self._send(404, b"", "text/plain")
            return
        payload = json.loads(raw or "{}")
        with _write_lock:
            self._save_board(payload)

    def _save_board(self, payload):
        current = load_data()
        current_rev = int(current.get("_rev") or 1)
        incoming_rev = int(payload.get("_rev") or 1)
        if incoming_rev != current_rev:
            body = json.dumps({
                "ok": False,
                "error": "conflict",
                "message": "Данные изменились в другой вкладке. Обновите страницу.",
                "currentRev": current_rev,
            }, ensure_ascii=False).encode("utf-8")
            self._send(409, body, "application/json; charset=utf-8")
            return
        payload["_rev"] = current_rev + 1
        payload["updatedAt"] = date.today().isoformat()
        save_data(payload)
        body = json.dumps({"ok": True, "rev": payload["_rev"]}, ensure_ascii=False).encode("utf-8")
        self._send(200, body, "application/json; charset=utf-8")


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
