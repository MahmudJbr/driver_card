import mysql.connector
from mysql.connector import Error
from datetime import datetime, date

# Inställningar för databasen
DB_CONFIG = {
    "host": "localhost",
    "user": "eforarkort_user",
    "password": "EttProjektLosenord!",
    "database": "eforarkort",
    "port": 3306
}


def get_connection():
    """Skapa en ny anslutning till databasen"""
    return mysql.connector.connect(**DB_CONFIG)


def get_user_by_email(email: str):
    """Hämta en användare baserat på e-postadress"""
    query = "SELECT * FROM users WHERE email = %s"
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_driving_history(user_id: int):
    """Hämta körhistorik för en förare (JOIN mot vehicles)"""
    query = """
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
        v.årsmodell
    FROM driving_sessions ds
    LEFT JOIN vehicles v ON ds.vehicleID = v.vehicleID
    WHERE ds.userID = %s
    ORDER BY ds.startTid DESC
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def add_driving_session(user_id: int, vehicle_id: int, start_tid: str, slut_tid: str, stracka_km: int, status: str = "avslutad"):
    """
    Lägg till ett körpass.
    - start_tid/slut_tid: 'YYYY-MM-DD HH:MM:SS'
    - Trigger i DB räknar körtid automatiskt.
    - Om passet > 9h skapas violation automatiskt (trigger).
    """
    insert_sql = """
    INSERT INTO driving_sessions (userID, vehicleID, startTid, slutTid, `sträcka`, status)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql, (user_id, vehicle_id, start_tid, slut_tid, stracka_km, status))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def get_violations_for_user(user_id: int):
    """Hämta violations för en förare (JOIN mot driving_sessions + vehicles)"""
    query = """
    SELECT
        vio.violationID,
        vio.violationstyp,
        vio.detaljer,
        vio.datum,
        ds.startTid,
        ds.slutTid,
        ds.`körtid`,
        v.registreringsnummer
    FROM violations vio
    LEFT JOIN driving_sessions ds ON ds.sessionID = vio.sessionID
    LEFT JOIN vehicles v ON v.vehicleID = ds.vehicleID
    WHERE vio.userID = %s
    ORDER BY vio.datum DESC;
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def get_total_hours_for_period(user_id: int, from_date: str, to_date: str) -> float:
    """
    Använder SQL FUNCTION total_kortid_seconds.
    from_date/to_date: 'YYYY-MM-DD'
    Returnerar timmar (float).
    """
    query = "SELECT total_kortid_seconds(%s, %s, %s) AS total_seconds;"
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (user_id, from_date, to_date))
            row = cursor.fetchone()
            seconds = row["total_seconds"] if row and row["total_seconds"] is not None else 0
            return round(seconds / 3600, 2)
    finally:
        conn.close()


def get_weekly_report(from_date: str, to_date: str):
    """
    Anropar stored procedure weekly_report.
    from_date/to_date: 'YYYY-MM-DD'
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.callproc("weekly_report", [from_date, to_date])

            # I mysql-connector kommer resultat från callproc via stored_results()
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            return results
    finally:
        conn.close()


# ===== TEST / DEMO =====
if __name__ == "__main__":
    try:
        print("TEST 1: Hämta användare via email")
        user = get_user_by_email("anna@example.com")
        if not user:
            raise RuntimeError("Ingen användare hittades med den emailen.")
        print(f"Hittade: {user['fName']} {user['lName']} (userID={user['userID']})")

        print("\nTEST 2: Körhistorik (JOIN mot vehicles)")
        sessions = get_driving_history(user["userID"])
        print(f"{user['fName']} har {len(sessions)} körningar")
        for s in sessions:
            print(f"  - {s['startTid']} → {s['slutTid']} | körtid={s['körtid']} | {s['sträcka']} km | reg={s['registreringsnummer']}")

        print("\nTEST 3: Lägg in ett långt pass (ska trigga violation > 9h)")
        new_id = add_driving_session(
            user_id=user["userID"],
            vehicle_id=1,
            start_tid="2026-02-01 06:00:00",
            slut_tid="2026-02-01 16:30:00",  # 10.5h
            stracka_km=600,
            status="avslutad"
        )
        print(f"La in driving_session med sessionID={new_id}")

        print("\nTEST 4: Violations för användaren (JOIN mot sessions/vehicles)")
        violations = get_violations_for_user(user["userID"])
        print(f"Antal violations: {len(violations)}")
        for v in violations[:5]:
            print(f"  - [{v['datum']}] {v['violationstyp']} | {v['detaljer']} | reg={v['registreringsnummer']}")

        print("\nTEST 5: Total körtid för januari (SQL FUNCTION)")
        hours_jan = get_total_hours_for_period(user["userID"], "2026-01-01", "2026-01-31")
        print(f"Totala timmar i jan: {hours_jan} h")

        print("\nTEST 6: Weekly report (Stored procedure)")
        report = get_weekly_report("2026-01-01", "2026-02-02")
        for r in report:
            print(f"  - user={r['user_id']} | {r['driver_name']} | week={r['week_no']} | hours={r['total_drive_hours']} | km={r['total_distance_km']} | sessions={r['session_count']}")

    except Error as e:
        print("Databasfel:", e)
    except Exception as e:
        print("Fel:", e)
