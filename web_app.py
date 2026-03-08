from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"  # för session cookies (demo)

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "eforarkort_user",
    "password": "ADALLA1234",
    "database": "eforarkort",
    "port": 3306
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def query_one(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()

def query_all(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return query_one("SELECT userID, fName, lName, email, role FROM users WHERE userID=%s", (uid,))

def login_required():
    if not session.get("user_id"):
        return False
    return True


@app.route("/", methods=["GET"])
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        user = query_one("SELECT userID, fName, lName, email, role FROM users WHERE email=%s", (email,))
        if not user:
            flash("Ingen användare hittades med den emailen.")
            return redirect(url_for("login"))
        session["user_id"] = user["userID"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()

    card = query_one("""
        SELECT card_number, issued_date, expiry_date, status
        FROM driver_cards
        WHERE userID=%s
    """, (user["userID"],))

    stats = query_one("""
        SELECT
        COUNT(*) AS sessions_count,
        COALESCE(SUM(`sträcka`), 0) AS total_km
        FROM driving_sessions
        WHERE userID=%s AND status='avslutad'
    """, (user["userID"],))

    # olösta events
    events = query_all("""
        SELECT eventID, event_type, created_at, due_date, message, is_resolved
        FROM events
        WHERE userID=%s AND is_resolved=FALSE
        ORDER BY created_at DESC
        LIMIT 10
    """, (user["userID"],))

    return render_template("dashboard.html", user=user, card=card, stats=stats, events=events)

@app.route("/sessions")
def sessions_page():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    sessions_list = query_all("""
        SELECT 
        ds.sessionID, ds.startTid, ds.slutTid, ds.`körtid`, ds.`sträcka`, ds.status,
        v.registreringsnummer, v.fordonstyp, v.fabrikat
        FROM driving_sessions ds
        LEFT JOIN vehicles v ON v.vehicleID = ds.vehicleID
        WHERE ds.userID=%s
        ORDER BY ds.startTid DESC
    """, (user["userID"],))

    return render_template("sessions.html", user=user, sessions=sessions_list)

@app.route("/sessions/new", methods=["GET", "POST"])
def add_session_page():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    vehicles = query_all("SELECT vehicleID, registreringsnummer FROM vehicles ORDER BY vehicleID;")

    if request.method == "POST":
        vehicle_id = request.form.get("vehicle_id")
        startTid = request.form.get("startTid")
        slutTid = request.form.get("slutTid")
        stracka = request.form.get("stracka")
        status = request.form.get("status", "avslutad")

        # INSERT -> triggers räknar körtid + skapar violation/event
        execute("""
            INSERT INTO driving_sessions (userID, vehicleID, startTid, slutTid, `sträcka`, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user["userID"], vehicle_id, startTid, slutTid, stracka, status))

        flash("Körpass sparat! (DB trigger kan ha skapat violation/event om > 9h)")
        return redirect(url_for("sessions_page"))

    return render_template("add_session.html", user=user, vehicles=vehicles)

@app.route("/violations")
def violations_page():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    vios = query_all("""
        SELECT
        vio.violationID, vio.violationstyp, vio.detaljer, vio.datum,
        ds.startTid, ds.slutTid, ds.`körtid`,
        v.registreringsnummer
        FROM violations vio
        LEFT JOIN driving_sessions ds ON ds.sessionID = vio.sessionID
        LEFT JOIN vehicles v ON v.vehicleID = ds.vehicleID
        WHERE vio.userID=%s
        ORDER BY vio.datum DESC
    """, (user["userID"],))

    return render_template("violations.html", user=user, violations=vios)

@app.route("/events", methods=["GET", "POST"])
def events_page():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()

    if request.method == "POST":
        event_id = request.form.get("event_id")
        execute("UPDATE events SET is_resolved=TRUE WHERE eventID=%s AND userID=%s", (event_id, user["userID"]))
        flash("Event markerat som resolved.")
        return redirect(url_for("events_page"))

    evs = query_all("""
        SELECT eventID, event_type, created_at, due_date, message, is_resolved
        FROM events
        WHERE userID=%s
        ORDER BY created_at DESC
    """, (user["userID"],))

    return render_template("events.html", user=user, events=evs)

@app.route("/report", methods=["GET", "POST"])
def report_page():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    report_rows = []
    from_date = ""
    to_date = ""

    if request.method == "POST":
        from_date = request.form.get("from_date")
        to_date = request.form.get("to_date")

        # CALL stored procedure
        conn = get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("CALL weekly_report(%s, %s);", (from_date, to_date))
            report_rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

    return render_template("report.html", user=user, report=report_rows, from_date=from_date, to_date=to_date)


if __name__ == "__main__":
    app.run(debug=True)
