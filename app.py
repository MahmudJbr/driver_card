import mysql.connector
from mysql.connector import Error
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "eforarkort_user",
    "password": "ADALLA1234",
    "database": "eforarkort",
    "port": 3306
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# =========================
# DB FUNCTIONS
# =========================
def list_users():
    sql = "SELECT userID, fName, lName, email, role FROM users ORDER BY userID;"
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


def get_user_by_email(email: str):
    sql = "SELECT * FROM users WHERE email = %s;"
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (email,))
            return cur.fetchone()
    finally:
        conn.close()


def get_driver_card(user_id: int):
    sql = """
    SELECT cardID, userID, card_number, issued_date, expiry_date, status
    FROM driver_cards
    WHERE userID = %s;
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_driving_history(user_id: int):
    # JOIN driving_sessions + vehicles
    sql = """
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
    ORDER BY ds.startTid DESC;
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()


def add_driving_session(user_id: int, vehicle_id: int, start_tid: str, slut_tid: str, distance_km: int, status: str = "avslutad"):
    """
    INSERT körpass.
    Trigger i DB:
    - räknar körtid
    - skapar violation om > 9h
    - skapar event när violation skapas
    """
    sql = """
    INSERT INTO driving_sessions (userID, vehicleID, startTid, slutTid, `sträcka`, status)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, vehicle_id, start_tid, slut_tid, distance_km, status))
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


def get_violations_for_user(user_id: int):
    # JOIN violations + sessions + vehicles
    sql = """
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
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()


def get_total_hours_for_period(user_id: int, from_date: str, to_date: str) -> float:
    # SQL FUNCTION total_kortid_seconds
    sql = "SELECT total_kortid_seconds(%s, %s, %s) AS total_seconds;"
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (user_id, from_date, to_date))
            row = cur.fetchone()
            seconds = row["total_seconds"] if row and row["total_seconds"] is not None else 0
            return round(seconds / 3600, 2)
    finally:
        conn.close()


def get_weekly_report(from_date: str, to_date: str):
    # PROCEDURE weekly_report
    sql = "CALL weekly_report(%s, %s);"
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (from_date, to_date))
            return cur.fetchall()
    finally:
        conn.close()


def add_activity_log(user_id: int, vehicle_id: int | None, start_tid: str, slut_tid: str, activity: str, source: str = "MANUAL", notes: str = ""):
    """
    Lägg till aktivitet i activity_logs (REST/OTHER/DRIVE).
    """
    sql = """
    INSERT INTO activity_logs (userID, vehicleID, startTid, slutTid, activity, source, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, vehicle_id, start_tid, slut_tid, activity, source, notes))
            conn.commit()
            return cur.lastrowid
    finally:
        conn.close()


def get_activity_logs(user_id: int):
    sql = """
    SELECT
      logID, startTid, slutTid, activity, source, notes, vehicleID
    FROM activity_logs
    WHERE userID = %s
    ORDER BY startTid DESC;
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()


def get_events(user_id: int, only_unresolved: bool = True):
    if only_unresolved:
        sql = """
        SELECT eventID, event_type, created_at, due_date, message, is_resolved
        FROM events
        WHERE userID = %s AND is_resolved = FALSE
        ORDER BY created_at DESC;
        """
    else:
        sql = """
        SELECT eventID, event_type, created_at, due_date, message, is_resolved
        FROM events
        WHERE userID = %s
        ORDER BY created_at DESC;
        """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(sql, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()


def resolve_event(event_id: int):
    sql = "UPDATE events SET is_resolved = TRUE WHERE eventID = %s;"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (event_id,))
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()


def generate_card_expiry_events(days: int):
    sql = "CALL generate_card_expiry_events(%s);"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (days,))
            conn.commit()
    finally:
        conn.close()


# =========================
# CLI HELPERS
# =========================
def prompt_int(msg: str) -> int:
    while True:
        s = input(msg).strip()
        try:
            return int(s)
        except ValueError:
            print(" Skriv ett heltal.")


def prompt_date(msg: str) -> str:
    while True:
        s = input(msg).strip()
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            print(" Format: YYYY-MM-DD (ex: 2026-02-01)")


def prompt_datetime(msg: str) -> str:
    while True:
        s = input(msg).strip()
        try:
            datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            return s
        except ValueError:
            print(" Format: YYYY-MM-DD HH:MM:SS (ex: 2026-02-01 06:00:00)")


def print_active_user(user):
    print(f"\n👤 Aktiv användare: {user['fName']} {user['lName']} (userID={user['userID']}, email={user['email']}, role={user['role']})")


# =========================
# MAIN APP
# =========================
def main():
    print("======================================")
    print(" e-Förarkort – Konsolapp (Python + SQL)")
    print("======================================")

    active_user = None

    while True:
        print("\n--- MENY ---")
        print("1) Lista användare")
        print("2) Välj förare via email")
        print("3) Visa förarkort (driver_cards)")
        print("4) Visa körhistorik (JOIN)")
        print("5) Lägg till körpass (Triggers: körtid + violation + event)")
        print("6) Visa violations (JOIN)")
        print("7) Total körtid mellan datum (FUNCTION)")
        print("8) Weekly report mellan datum (PROCEDURE)")
        print("9) Visa aktivitetslogg (REST/OTHER/DRIVE)")
        print("10) Lägg till aktivitet (activity_logs)")
        print("11) Visa events/varningar")
        print("12) Markera event som resolved")
        print("13) Generera kort-utgår-snart events (PROCEDURE)")
        print("0) Avsluta")

        choice = input("Välj: ").strip()

        try:
            if choice == "1":
                users = list_users()
                print("\n--- USERS ---")
                for u in users:
                    print(f"{u['userID']:>2} | {u['fName']} {u['lName']} | {u['email']} | role={u['role']}")

            elif choice == "2":
                email = input("Email: ").strip()
                user = get_user_by_email(email)
                if not user:
                    print(" Ingen användare hittades.")
                else:
                    active_user = user
                    print_active_user(active_user)

            elif choice == "3":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                card = get_driver_card(active_user["userID"])
                if not card:
                    print("ℹ Ingen driver_card hittades för användaren.")
                else:
                    print("\n--- DRIVER CARD ---")
                    print(f"card_number: {card['card_number']}")
                    print(f"issued_date: {card['issued_date']}")
                    print(f"expiry_date: {card['expiry_date']}")
                    print(f"status: {card['status']}")

            elif choice == "4":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                sessions = get_driving_history(active_user["userID"])
                print("\n--- KÖRHISTORIK ---")
                print(f"Antal sessions: {len(sessions)}")
                for s in sessions:
                    print(f"- sessionID={s['sessionID']} | {s['startTid']} → {s['slutTid']} | körtid={s['körtid']} | {s['sträcka']} km | reg={s['registreringsnummer']}")

            elif choice == "5":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                vehicle_id = prompt_int("vehicleID (ex 1): ")
                start_tid = prompt_datetime("startTid (YYYY-MM-DD HH:MM:SS): ")
                slut_tid = prompt_datetime("slutTid (YYYY-MM-DD HH:MM:SS): ")
                distance_km = prompt_int("sträcka (km): ")
                status = input("status (avslutad/pauserad/aktiv) [avslutad]: ").strip() or "avslutad"

                new_id = add_driving_session(active_user["userID"], vehicle_id, start_tid, slut_tid, distance_km, status)
                print(f" Ny session skapad: sessionID={new_id}")
                print("ℹ  Trigger i DB räknar körtid automatiskt och skapar violation/event om > 9h.")

            elif choice == "6":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                vios = get_violations_for_user(active_user["userID"])
                print("\n--- VIOLATIONS ---")
                print(f"Antal: {len(vios)}")
                for v in vios:
                    print(f"- {v['datum']} | {v['violationstyp']} | {v['detaljer']} | reg={v['registreringsnummer']}")

            elif choice == "7":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                from_date = prompt_date("Från datum (YYYY-MM-DD): ")
                to_date = prompt_date("Till datum (YYYY-MM-DD): ")
                hours = get_total_hours_for_period(active_user["userID"], from_date, to_date)
                print(f" Total körtid: {hours} timmar (SQL FUNCTION total_kortid_seconds)")

            elif choice == "8":
                from_date = prompt_date("Från datum (YYYY-MM-DD): ")
                to_date = prompt_date("Till datum (YYYY-MM-DD): ")
                report = get_weekly_report(from_date, to_date)
                print("\n--- WEEKLY REPORT (PROCEDURE) ---")
                for r in report:
                    print(f"- user={r['user_id']} | {r['driver_name']} | week={r['week_no']} | hours={r['total_drive_hours']} | km={r['total_distance_km']} | sessions={r['session_count']}")

            elif choice == "9":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                logs = get_activity_logs(active_user["userID"])
                print("\n--- ACTIVITY LOGS ---")
                print(f"Antal: {len(logs)}")
                for l in logs[:30]:
                    print(f"- logID={l['logID']} | {l['startTid']} → {l['slutTid']} | {l['activity']} | src={l['source']} | notes={l['notes']}")

            elif choice == "10":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)

                activity = input("activity (DRIVE/REST/OTHER): ").strip().upper()
                if activity not in ("DRIVE", "REST", "OTHER"):
                    print(" activity måste vara DRIVE, REST eller OTHER.")
                    continue

                vehicle_raw = input("vehicleID (valfritt, Enter för NULL): ").strip()
                vehicle_id = int(vehicle_raw) if vehicle_raw else None

                start_tid = prompt_datetime("startTid (YYYY-MM-DD HH:MM:SS): ")
                slut_tid = prompt_datetime("slutTid (YYYY-MM-DD HH:MM:SS): ")
                notes = input("notes (valfritt): ").strip()

                new_id = add_activity_log(active_user["userID"], vehicle_id, start_tid, slut_tid, activity, "MANUAL", notes)
                print(f" Ny aktivitet skapad: logID={new_id}")

            elif choice == "11":
                if not active_user:
                    print(" Välj en användare först (meny 2).")
                    continue
                print_active_user(active_user)
                only_unresolved = input("Endast olösta? (j/n) [j]: ").strip().lower()
                only_unresolved = (only_unresolved != "n")
                evs = get_events(active_user["userID"], only_unresolved=only_unresolved)
                print("\n--- EVENTS ---")
                print(f"Antal: {len(evs)}")
                for e in evs[:50]:
                    print(f"- eventID={e['eventID']} | {e['event_type']} | created={e['created_at']} | due={e['due_date']} | resolved={e['is_resolved']} | {e['message']}")

            elif choice == "12":
                event_id = prompt_int("Skriv eventID att markera som resolved: ")
                changed = resolve_event(event_id)
                if changed == 0:
                    print(" Inget event uppdaterades (fel eventID?).")
                else:
                    print(" Event markerat som resolved.")

            elif choice == "13":
                days = prompt_int("Skapa CARD_EXPIRY_SOON events för kort som går ut inom (dagar): ")
                generate_card_expiry_events(days)
                print(" Events genererade.")

            elif choice == "0":
                print("Hej då!")
                break

            else:
                print(" Ogiltigt val.")

        except Error as e:
            print(" Databasfel:", e)
        except Exception as e:
            print(" Fel:", e)


if __name__ == "__main__":
    main()
