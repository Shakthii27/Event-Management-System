import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import uuid
from utils.qr import generate_qr
from utils.mailer import send_mail
from datetime import date, time


app = Flask(__name__)
CORS(app)

# ---------- DB ----------
def db():
    return psycopg2.connect(
        "postgresql://postgres.mvurcmsnxavdsmchruok:shakthi%401234@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres",
        sslmode="require",
        cursor_factory=RealDictCursor
    )

# ---------- HELPERS ----------
def serialize_event(e):
    return {
        "id": e["id"],
        "name": e["name"],
        "date": e["date"].isoformat() if isinstance(e["date"], date) else e["date"],
        "time": e["time"].strftime("%H:%M") if isinstance(e["time"], time) else e["time"],
        "venue": e["venue"],
        "organiser_id": e["organiser_id"]
    }

# ---------- PAGES ----------
@app.route("/")
@app.route("/login")
def login_page():
    return render_template("index.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/profile")
def get_profile_page():
    return render_template("profile.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/create")
def create_page():
    return render_template("create.html")

@app.route("/event")
def event_page():
    return render_template("event.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

# ---------- AUTH ----------
@app.route("/api/signup", methods=["POST"])
def signup():
    d = request.json
    c = db(); cur = c.cursor()

    cur.execute("SELECT id FROM users WHERE email=%s", (d["email"],))
    if cur.fetchone():
        c.close()
        return jsonify(success=False, message="Account already exists")

    cur.execute(
        "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,'participant')",
        (d["name"], d["email"], d["password"])
    )
    c.commit(); c.close()
    return jsonify(success=True)

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    c = db(); cur = c.cursor()

    cur.execute("SELECT id, role, password FROM users WHERE email=%s", (d["email"],))
    u = cur.fetchone()
    c.close()

    if not u:
        return jsonify(success=False, message="Account does not exist")
    if u["password"] != d["password"]:
        return jsonify(success=False, message="Incorrect password")

    return jsonify(success=True, user_id=u["id"], role=u["role"])

# ---------- PROFILE ----------
@app.route("/api/profile/<int:user_id>")
def get_profile(user_id):
    c=db();cur=c.cursor()
    cur.execute("SELECT id,name,email,role FROM users WHERE id=%s",(user_id,))
    u=cur.fetchone();c.close()
    return jsonify(u)

@app.route("/api/upgrade", methods=["POST"])
def upgrade():
    uid=request.json["user_id"]
    c=db();cur=c.cursor()
    cur.execute("UPDATE users SET role='organiser' WHERE id=%s",(uid,))
    c.commit();c.close()
    return jsonify(success=True)

# ---------- EVENTS ----------
@app.route("/api/events", methods=["GET"])
def get_events():
    c = db(); cur = c.cursor()
    cur.execute("SELECT * FROM events ORDER BY date")
    rows = cur.fetchall()
    c.close()

    # 🔥 FIX: convert date & time to string
    events = []
    for e in rows:
        e["date"] = str(e["date"])
        e["time"] = str(e["time"])
        events.append(e)

    return jsonify(events)

@app.route("/api/events", methods=["POST"])
def create_event():
    d = request.json
    c = db(); cur = c.cursor()

    cur.execute("""
        INSERT INTO events(name,date,time,venue,status,organiser_id)
        VALUES(%s,%s,%s,%s,'published',%s)
        RETURNING id
    """, (
        d["name"],
        d["date"],
        d["time"],
        d["venue"],
        d["user_id"]
    ))

    event_id = cur.fetchone()["id"]
    c.commit(); c.close()

    return jsonify(
        success=True,
        event_id=event_id,
        link=f"http://127.0.0.1:10000/event?id={event_id}"
    )
# ---------- REGISTRATION ----------
@app.route("/api/register", methods=["POST"])
@app.route("/api/register", methods=["POST"])
def register_event():
    d = request.json
    event_id = d["event_id"]
    email = d["email"]

    ticket_id = str(uuid.uuid4())

    c = db()
    cur = c.cursor()

    # Fetch event details
    cur.execute("""
        SELECT name, date, time, venue
        FROM events
        WHERE id=%s
    """, (event_id,))
    event = cur.fetchone()

    if not event:
        c.close()
        return jsonify(success=False, message="Event not found")

    # Prevent duplicate
    cur.execute("""
        SELECT id FROM registrations
        WHERE event_id=%s AND email=%s
    """, (event_id, email))
    if cur.fetchone():
        c.close()
        return jsonify(success=False, message="Already registered")

    # Insert registration
    cur.execute("""
        INSERT INTO registrations (event_id, email, ticket)
        VALUES (%s, %s, %s)
    """, (event_id, email, ticket_id))

    c.commit()
    c.close()

    # Generate QR
    qr_path = generate_qr(ticket_id)

    # Send email with event + QR
    send_mail(email, ticket_id, qr_path, event)

    return jsonify(success=True, ticket_id=ticket_id)


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(port=10000, debug=True)
