from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"

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
    return query_one(
        "SELECT userID, fName, lName, email, role FROM users WHERE userID=%s",
        (uid,)
    )


def login_required():
    return bool(session.get("user_id"))


@app.route("/", methods=["GET"])
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("role_select.html")


@app.route("/login/<role_key>", methods=["GET", "POST"])
def login(role_key):
    role_map = {
        "driver": "förare",
        "admin": "admin"
    }

    selected_role = role_map.get(role_key)
    if not selected_role:
        flash("Ogiltig roll.")
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()

        user = query_one(
            "SELECT userID, fName, lName, email, role FROM users WHERE email=%s",
            (email,)
        )

        if not user:
            flash("Ingen användare hittades med den emailen.")
            return redirect(url_for("login", role_key=role_key))

        if user["role"] != selected_role:
            flash("Fel roll vald för den här användaren.")
            return redirect(url_for("login", role_key=role_key))

        session["user_id"] = user["userID"]
        session["role"] = user["role"]

        return redirect(url_for("dashboard"))

    return render_template("login.html", selected_role=selected_role, role_key=role_key)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("home"))

    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("home"))

    if user["role"] == "förare":
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

        events = query_all("""
            SELECT eventID, event_type, created_at, due_date, message, is_resolved
            FROM events
            WHERE userID=%s AND is_resolved=FALSE
            ORDER BY created_at DESC
            LIMIT 10
        """, (user["userID"],))

        return render_template(
            "dashboard.html",
            user=user,
            card=card,
            stats=stats,
            events=events,
            drivers=[],
            all_stats=[],
            all_violations=[]
        )

    elif user["role"] == "admin":
        drivers = query_all("""
            SELECT userID, fName, lName, email
            FROM users
            WHERE role='förare'
            ORDER BY fName, lName
        """)

        all_stats = query_all("""
            SELECT
                u.userID,
                u.fName,
                u.lName,
                COUNT(ds.sessionID) AS sessions,
                COALESCE(SUM(ds.`sträcka`), 0) AS total_km
            FROM users u
            LEFT JOIN driving_sessions ds ON u.userID = ds.userID
            WHERE u.role='förare'
            GROUP BY u.userID, u.fName, u.lName
            ORDER BY total_km DESC
        """)

        all_violations = query_all("""
            SELECT
                u.fName,
                u.lName,
                vio.violationstyp,
                vio.detaljer,
                vio.datum
            FROM violations vio
            JOIN users u ON u.userID = vio.userID
            ORDER BY vio.datum DESC
            LIMIT 20
        """)

        return render_template(
            "dashboard.html",
            user=user,
            card=None,
            stats=None,
            events=[],
            drivers=drivers,
            all_stats=all_stats,
            all_violations=all_violations
        )

    flash("Ogiltig roll.")
    session.clear()
    return redirect(url_for("home"))


@app.route("/sessions")
def sessions_page():
    if not login_required():
        return redirect(url_for("home"))

    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("home"))

    # Förare ser bara sina egna körpass
    if user["role"] == "förare":
        sessions_list = query_all("""
            SELECT
                ds.sessionID,
                ds.startTid,
                ds.slutTid,
                ds.`körtid`,
                ds.`sträcka`,
                ds.status,
                v.registreringsnummer,
                v.fordonstyp,
                v.fabrikat
            FROM driving_sessions ds
            LEFT JOIN vehicles v ON ds.vehicleID = v.vehicleID
            WHERE ds.userID = %s
            ORDER BY ds.startTid DESC
        """, (user["userID"],))

    # Admin ser alla förares körpass
    else:
        sessions_list = query_all("""
            SELECT
                ds.sessionID,
                ds.startTid,
                ds.slutTid,
                ds.`körtid`,
                ds.`sträcka`,
                ds.status,
                v.registreringsnummer,
                v.fordonstyp,
                v.fabrikat,
                u.fName,
                u.lName
            FROM driving_sessions ds
            LEFT JOIN vehicles v ON ds.vehicleID = v.vehicleID
            JOIN users u ON ds.userID = u.userID
            ORDER BY ds.startTid DESC
        """)

    return render_template("sessions.html", user=user, sessions=sessions_list)


@app.route("/sessions/new", methods=["GET", "POST"])
def add_session_page():
    if not login_required():
        return redirect(url_for("home"))

    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("home"))

    if user["role"] != "förare":
        flash("Bara förare kan lägga till körpass här.")
        return redirect(url_for("dashboard"))

    vehicles = query_all("""
        SELECT vehicleID, registreringsnummer
        FROM vehicles
        ORDER BY vehicleID
    """)

    if request.method == "POST":
        vehicle_id = request.form.get("vehicle_id")
        startTid = request.form.get("startTid")
        slutTid = request.form.get("slutTid")
        stracka = request.form.get("stracka")
        status = request.form.get("status", "avslutad")

        rest_start = request.form.get("rest_start", "").strip()
        rest_end = request.form.get("rest_end", "").strip()
        rest_notes = request.form.get("rest_notes", "").strip()

        # 1. Spara körpass
        execute("""
            INSERT INTO driving_sessions (userID, vehicleID, startTid, slutTid, `sträcka`, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user["userID"], vehicle_id, startTid, slutTid, stracka, status))

        # 2. Om rast är ifylld -> spara rast i activity_logs
        if rest_start and rest_end:
            execute("""
                INSERT INTO activity_logs (userID, vehicleID, startTid, slutTid, activity, source, notes)
                VALUES (%s, %s, %s, %s, 'REST', 'MANUAL', %s)
            """, (
                user["userID"],
                vehicle_id,
                rest_start,
                rest_end,
                rest_notes if rest_notes else "Rast kopplad till körpass"
            ))

            flash("Körpass och rast sparade.")
        else:
            flash("Körpass sparat.")

        return redirect(url_for("sessions_page"))

    return render_template("add_session.html", user=user, vehicles=vehicles)

@app.route("/violations")
def violations_page():
    if not login_required():
        return redirect(url_for("home"))

    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("home"))

    if user["role"] == "förare":
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
    else:
        vios = query_all("""
            SELECT
                vio.violationID, vio.violationstyp, vio.detaljer, vio.datum,
                ds.startTid, ds.slutTid, ds.`körtid`,
                v.registreringsnummer,
                u.fName,
                u.lName
            FROM violations vio
            LEFT JOIN driving_sessions ds ON ds.sessionID = vio.sessionID
            LEFT JOIN vehicles v ON v.vehicleID = ds.vehicleID
            LEFT JOIN users u ON u.userID = vio.userID
            ORDER BY vio.datum DESC
        """)

    return render_template("violations.html", user=user, violations=vios)


@app.route("/events", methods=["GET", "POST"])
def events_page():
    if not login_required():
        return redirect(url_for("home"))

    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("home"))

    if request.method == "POST":
        event_id = request.form.get("event_id")

        if user["role"] == "admin":
            execute(
                "UPDATE events SET is_resolved=TRUE WHERE eventID=%s",
                (event_id,)
            )
        else:
            execute(
                "UPDATE events SET is_resolved=TRUE WHERE eventID=%s AND userID=%s",
                (event_id, user["userID"])
            )

        flash("Event markerat som resolved.")
        return redirect(url_for("events_page"))

    # FÖRARE: bara egna events + egna activity_logs
    if user["role"] == "förare":
        events = query_all("""
            SELECT
                eventID,
                event_type,
                created_at,
                due_date,
                message,
                is_resolved
            FROM events
            WHERE userID = %s
            ORDER BY created_at DESC
        """, (user["userID"],))

        activity_logs = query_all("""
            SELECT
                al.logID,
                al.startTid,
                al.slutTid,
                al.activity,
                al.source,
                al.notes,
                v.registreringsnummer
            FROM activity_logs al
            LEFT JOIN vehicles v ON v.vehicleID = al.vehicleID
            WHERE al.userID = %s
            ORDER BY al.startTid DESC
        """, (user["userID"],))

    # ADMIN: alla events + alla activity_logs
    else:
        events = query_all("""
            SELECT
                e.eventID,
                e.event_type,
                e.created_at,
                e.due_date,
                e.message,
                e.is_resolved,
                u.fName,
                u.lName
            FROM events e
            JOIN users u ON u.userID = e.userID
            ORDER BY e.created_at DESC
        """)

        activity_logs = query_all("""
            SELECT
                al.logID,
                al.startTid,
                al.slutTid,
                al.activity,
                al.source,
                al.notes,
                v.registreringsnummer,
                u.fName,
                u.lName
            FROM activity_logs al
            JOIN users u ON u.userID = al.userID
            LEFT JOIN vehicles v ON v.vehicleID = al.vehicleID
            ORDER BY al.startTid DESC
        """)

    return render_template(
        "events.html",
        user=user,
        events=events,
        activity_logs=activity_logs
    )

@app.route("/report", methods=["GET", "POST"])
def report_page():
    if not login_required():
        return redirect(url_for("home"))

    user = current_user()
    if not user:
        session.clear()
        return redirect(url_for("home"))

    report_rows = []
    from_date = ""
    to_date = ""

    if request.method == "POST":
        from_date = request.form.get("from_date")
        to_date = request.form.get("to_date")

        conn = get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("CALL weekly_report(%s, %s);", (from_date, to_date))
            all_rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        # Förare ser bara sin egen rapport
        if user["role"] == "förare":
            report_rows = [r for r in all_rows if r["user_id"] == user["userID"]]
        else:
            # Admin ser alla
            report_rows = all_rows

    return render_template(
        "report.html",
        user=user,
        report=report_rows,
        from_date=from_date,
        to_date=to_date
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)