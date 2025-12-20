from flask import Flask, request, redirect, session, render_template_string
import sqlite3, os

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "event.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        time TEXT,
        venue TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS participants(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        name TEXT,
        phone TEXT,
        email TEXT
    )
    """)

    conn.commit()
    conn.close()

init()

# ---------------- STYLE (FONT IMPROVED ONLY) ----------------
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@500;600;700&display=swap');

body{
  margin:0;
  font-family:'Inter',sans-serif;
  background:
    linear-gradient(180deg, rgba(6,10,30,.6), rgba(6,10,30,.9)),
    url('https://images.unsplash.com/photo-1492684223066-81342ee5ff30');
  background-size:cover;
  background-attachment:fixed;
  color:#e5e7eb;
}

h1, h2, h3{
  font-family:'Playfair Display', serif;
  letter-spacing:0.3px;
}

.page{ padding:90px 9%; }

header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:70px;
}

header h1{ font-size:40px; }

nav a{
  margin-left:32px;
  color:#c7d2fe;
  text-decoration:none;
  font-weight:500;
}

.glass{
  background:linear-gradient(180deg, rgba(255,255,255,.16), rgba(255,255,255,.05));
  backdrop-filter:blur(24px);
  border-radius:36px;
  padding:50px;
  box-shadow:0 50px 140px rgba(0,0,0,.45);
}

input{
  width:100%;
  padding:16px;
  margin-bottom:18px;
  border-radius:20px;
  border:1px solid rgba(255,255,255,.25);
  background:rgba(255,255,255,.1);
  color:white;
  font-family:'Inter',sans-serif;
}

input::placeholder{ color:#c7d2fe; }

button{
  width:100%;
  padding:16px;
  border:none;
  border-radius:26px;
  background:linear-gradient(135deg,#6366f1,#8b5cf6);
  color:white;
  font-size:15px;
  font-family:'Inter',sans-serif;
  cursor:pointer;
}

.event{
  margin-bottom:36px;
  padding:40px;
  border-radius:36px;
  background:linear-gradient(180deg, rgba(255,255,255,.18), rgba(255,255,255,.05));
  backdrop-filter:blur(22px);
}

.meta{
  font-size:13px;
  color:#c7d2fe;
  font-family:'Inter',sans-serif;
  margin:10px 0;
}

.link{
  color:#a5b4fc;
  font-size:14px;
  word-break:break-all;
  font-family:'Inter',sans-serif;
}
</style>
"""

# ---------------- LOGIN + SIGNUP ----------------
@app.route("/", methods=["GET","POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form["u"]
        password = request.form["p"]
        action = request.form["action"]

        conn = db()
        c = conn.cursor()

        if action == "login":
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )
            if c.fetchone():
                session["user"] = username
                conn.close()
                return redirect("/dashboard")
            else:
                error = "Invalid username or password"

        elif action == "signup":
            try:
                c.execute(
                    "INSERT INTO users(username,password) VALUES(?,?)",
                    (username, password)
                )
                conn.commit()
                session["user"] = username
                conn.close()
                return redirect("/dashboard")
            except sqlite3.IntegrityError:
                error = "Username already exists"

        conn.close()

    return render_template_string(f"""
    {STYLE}
    <div class="page">
      <div class="glass" style="max-width:900px;margin:auto;display:grid;grid-template-columns:1fr 1fr;gap:60px">
        <div>
          <h1>Event Manager</h1>
          <p style="color:#c7d2fe">
            Create, publish, and manage events.<br>
            Share links and track registrations.
          </p>
        </div>

        <form method="post">
          <input name="u" placeholder="Username" required>
          <input type="password" name="p" placeholder="Password" required>

          <button name="action" value="login">Sign in</button>
          <button name="action" value="signup"
                  style="margin-top:12px;background:rgba(255,255,255,.14)">
            Create account
          </button>

          <p style="color:#fca5a5;margin-top:14px">{error}</p>
        </form>
      </div>
    </div>
    """)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    events = db().execute("SELECT * FROM events ORDER BY date").fetchall()

    html = f"""
    {STYLE}
    <div class="page">
      <header>
        <h1>Dashboard</h1>
        <nav>
          <a href="/create">Create Event</a>
          <a href="/events">View Events</a>
          <a href="/logout">Logout</a>
        </nav>
      </header>
    """

    for e in events:
        html += f"""
        <div class="event">
          <h3>{e['name']}</h3>
          <div class="meta">{e['date']} · {e['time']} · {e['venue']}</div>
          <a href="/register/{e['id']}">Open registration</a>
        </div>
        """

    html += "</div>"
    return html

# ---------------- CREATE EVENT ----------------
@app.route("/create", methods=["GET","POST"])
def create():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        conn = db()
        conn.execute(
            "INSERT INTO events(name,date,time,venue) VALUES(?,?,?,?)",
            (request.form["name"], request.form["date"],
             request.form["time"], request.form["venue"])
        )
        conn.commit()
        conn.close()
        return redirect("/dashboard")

    return render_template_string(f"""
    {STYLE}
    <div class="page">
      <header>
        <h1>Create Event</h1>
        <nav>
          <a href="/dashboard">Dashboard</a>
          <a href="/logout">Logout</a>
        </nav>
      </header>

      <div class="glass" style="max-width:520px">
        <form method="post">
          <input name="name" placeholder="Event name">
          <input type="date" name="date">
          <input type="time" name="time">
          <input name="venue" placeholder="Venue / Platform">
          <button>Create Event</button>
        </form>
      </div>
    </div>
    """)

# ---------------- VIEW EVENTS ----------------
@app.route("/events")
def events():
    events = db().execute("SELECT * FROM events ORDER BY date").fetchall()

    html = f"""
    {STYLE}
    <div class="page">
      <header>
        <h1>All Events</h1>
        <nav>
          <a href="/dashboard">Dashboard</a>
          <a href="/logout">Logout</a>
        </nav>
      </header>
    """

    for e in events:
        link = f"http://127.0.0.1:10000/register/{e['id']}"
        html += f"""
        <div class="event">
          <h3>{e['name']}</h3>
          <div class="meta">{e['date']} · {e['time']} · {e['venue']}</div>
          <div class="meta">Share link:</div>
          <div class="link">{link}</div>
          <a href="/register/{e['id']}">Open registration</a>
        </div>
        """

    html += "</div>"
    return html

# ---------------- REGISTER ----------------
@app.route("/register/<int:event_id>", methods=["GET","POST"])
def register(event_id):
    if request.method == "POST":
        conn = db()
        conn.execute(
            "INSERT INTO participants(event_id,name,phone,email) VALUES(?,?,?,?)",
            (event_id, request.form["name"],
             request.form["phone"], request.form["email"])
        )
        conn.commit()
        conn.close()

        return render_template_string(f"""
        {STYLE}
        <div class="page">
          <div class="glass" style="max-width:520px;margin:auto;text-align:center">
            <h2>Registration Confirmed</h2>
            <p style="color:#c7d2fe">You’re successfully registered.</p>
            <a href="/" class="link">Back to home</a>
          </div>
        </div>
        """)

    return render_template_string(f"""
    {STYLE}
    <div class="page">
      <div class="glass" style="max-width:420px;margin:auto">
        <h2>Register for Event</h2>
        <form method="post">
          <input name="name" placeholder="Full name">
          <input name="phone" placeholder="Phone number">
          <input name="email" placeholder="Email address">
          <button>Register</button>
        </form>
      </div>
    </div>
    """)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
