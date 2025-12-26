import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow Vercel frontend to call backend

# ---------------- DATABASE (SUPABASE) ----------------
def db():
    return psycopg2.connect(
        host="db.mvurcmsnxavdsmchruok.supabase.co",
        database="postgres",
        user="postgres",
        password="shakthi@1234",   # move to env later
        port=5432,
        cursor_factory=RealDictCursor
    )

# ---------------------------------------------------
# AUTH APIs
# ---------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE username=%s AND password=%s",
        (data["username"], data["password"])
    )

    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify(success=True)
    return jsonify(success=False, message="Invalid credentials")


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    try:
        conn = db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (data["username"], data["password"])
        )
        conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception:
        return jsonify(success=False, message="Username already exists")

# ---------------------------------------------------
# EVENTS APIs
# ---------------------------------------------------

@app.route("/api/events", methods=["GET"])
def get_events():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY date")
    events = cur.fetchall()
    conn.close()
    return jsonify(events)


@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.json
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO events(name,date,time,venue) VALUES(%s,%s,%s,%s)",
        (data["name"], data["date"], data["time"], data["venue"])
    )

    conn.commit()
    conn.close()
    return jsonify(success=True)

# ---------------------------------------------------
# REGISTRATION API
# ---------------------------------------------------

@app.route("/api/register/<int:event_id>", methods=["POST"])
def register(event_id):
    data = request.json
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO participants(event_id,name,phone,email) VALUES(%s,%s,%s,%s)",
        (event_id, data["name"], data["phone"], data["email"])
    )

    conn.commit()
    conn.close()
    return jsonify(success=True)

# ---------------------------------------------------
# RUN
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
