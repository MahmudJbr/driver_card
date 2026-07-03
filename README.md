# e-DriverCard

e-DriverCard is a Flask and MySQL web application for managing digital driver cards, driving sessions, rest periods, violations, and weekly driving reports.

The idea behind the project is simple: drivers and transport managers should be able to check driving-time data from a browser instead of relying only on a physical driver card or manual notes. The current version is a working local demo with separate views for drivers and company admins.

## Demo

Demo video placeholder:

[Watch the e-DriverCard walkthrough](docs/demo/e-drivercard-demo.mp4)

Planned walkthrough:

- choosing a role and signing in
- viewing the driver dashboard
- adding a driving session and rest period
- reviewing violations and events
- generating a weekly report

## Screenshots

Replace these placeholders with screenshots from the working interface.

| Role selection | Driver dashboard | Add driving session |
| --- | --- | --- |
| ![Role selection screenshot placeholder](docs/screenshots/role-selection.png) | ![Driver dashboard screenshot placeholder](docs/screenshots/driver-dashboard.png) | ![Add session screenshot placeholder](docs/screenshots/add-session.png) |

| Admin overview | Violations | Weekly report |
| --- | --- | --- |
| ![Admin overview screenshot placeholder](docs/screenshots/admin-overview.png) | ![Violations screenshot placeholder](docs/screenshots/violations.png) | ![Weekly report screenshot placeholder](docs/screenshots/weekly-report.png) |

## What It Does

e-DriverCard gives drivers and transport managers a shared place to work with driving-time information.

Drivers can:

- view their digital driver card details
- review completed driving sessions
- add a new driving session from the web interface
- record a connected rest period
- see unresolved events and warnings
- generate a weekly report for their own driving time

Admins can:

- see all registered drivers
- compare driving-session statistics across drivers
- review recent violations
- inspect events and activity logs
- generate weekly reports for the whole company

## Why I Built It

Professional drivers use physical driver cards and tachographs to record driving and rest time. That works, but it also creates a few practical problems:

- drivers cannot easily check their data from home
- companies do not always have a quick overview of driver availability
- missing or damaged cards can lead to manual reporting
- manual reporting increases the risk of mistakes or misuse
- replacing physical cards costs time and money

This project explores what a digital driver-card workflow could look like as a web system. It is not a replacement for official tachograph systems, but it shows the core flow: identity, driving sessions, rest periods, warnings, and reports in one place.

## Features

- Role-based entry for drivers and admins
- Driver dashboard with card status, total distance, session count, and open events
- Admin dashboard with driver list, company-wide statistics, and recent violations
- Driving-session history joined with vehicle details
- Manual session creation with optional rest-period logging
- Events page for warnings, card-expiry notices, and resolved/unresolved status
- Violation view with session and vehicle context
- Weekly report generation through a stored procedure
- SQL function for calculating driving time inside a date range

## Tech Stack

- Python
- Flask
- MySQL
- mysql-connector-python
- Jinja templates
- HTML and CSS

## Project Structure

```text
driverCard/
├── web_app.py              # Flask web application
├── app.py                  # CLI-style helper/demo entry point
├── db_functions.py         # Database helper functions
├── templates/              # Jinja HTML templates
├── static/truck.jpg        # Interface background image
├── users.sql               # Users table
├── driver_cards.sql        # Digital driver-card table
├── vehicles.sql            # Vehicle table
├── driving_sessions.sql    # Driving-session table
├── activity_log.sql        # Rest/drive/other activity log table
├── events.sql              # Events and warnings table
├── function.sql            # SQL function for total driving time
├── procedure.sql           # Stored procedures for reports and card-expiry events
└── demo_seed.sql           # Realistic demo data for portfolio walkthroughs
```

## Data Model

The database is built around the main objects needed by a digital driver-card system:

- `users` stores drivers and admins.
- `driver_cards` stores each driver's digital card details and expiry status.
- `vehicles` stores truck registration and vehicle metadata.
- `driving_sessions` stores start time, end time, driving time, distance, status, driver, and vehicle.
- `activity_logs` stores rest, driving, and other work activities.
- `events` stores warnings and messages that can be resolved from the interface.
- `violations` is used by the application to show driving-time violations with session and vehicle context.

E/R diagram placeholder:

![E/R diagram placeholder](docs/diagrams/er-diagram.png)

## Database Logic

Some of the business logic is handled directly in MySQL so the application can keep the route code focused on the user flow.

The included SQL routines are:

- `total_kortid_seconds(p_userID, p_from, p_to)`  
  Calculates the total completed driving time for one driver in a selected date range.

- `generate_card_expiry_events(p_days)`  
  Creates unresolved card-expiry warnings for active cards that expire soon.

- `weekly_report(p_from, p_to)`  
  Groups completed driving sessions by driver and week, returning total hours, distance, and session count.

## Representative SQL

Driver history with vehicle information:

```sql
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
WHERE ds.userID = ?
ORDER BY ds.startTid DESC;
```

Total driving time for a driver in a date range:

```sql
SELECT total_kortid_seconds(?, ?, ?) AS total_seconds;
```

Weekly company report:

```sql
CALL weekly_report(?, ?);
```

Card-expiry warning generation:

```sql
CALL generate_card_expiry_events(?);
```

## Running Locally

The app is set up for local development with MySQL.

1. Create and activate a virtual environment.

```bash
cd driverCard
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the Python dependencies.

```bash
pip install flask mysql-connector-python
```

3. Create a MySQL database.

```sql
CREATE DATABASE eforarkort
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

4. Import the SQL files from this project and then load the demo data.

The demo seed file creates realistic drivers, vehicles, driver cards, driving sessions, rest logs, events, and violations for recording a portfolio walkthrough.

```bash
mysql -u root -p eforarkort < demo_seed.sql
```

Demo accounts included in the seed:

- Driver: `anna.driver@demo.se`
- Driver: `omar.driver@demo.se`
- Driver: `lina.driver@demo.se`
- Admin: `sara.manager@demo.se`

The Flask app expects the database connection values in `web_app.py` to match your local MySQL setup.

5. Start the web app.

```bash
python web_app.py
```

6. Open the local site.

```text
http://127.0.0.1:5001
```

## Current Limitations

- Login is intentionally lightweight for the demo flow and currently uses role selection plus email lookup.
- The project is designed for local development, not production deployment.
- Database credentials are stored in the app configuration and should be moved to environment variables before deployment.
- The violation workflow depends on the expected database table and automation being present in the local database.

## Future Improvements

- Add proper authentication and password handling.
- Move configuration to environment variables.
- Add a full setup script for rebuilding the database from scratch.
- Add exportable PDF/CSV reports for managers.
- Improve driving-time rule checks with more detailed compliance logic.
- Explore BankID-style identification for a more realistic Swedish driver-card flow.
- Add vehicle integration as a future proof of concept, for example through Bluetooth or an onboard unit API.

## Reference

- Swedish Transport Agency information about driver cards:  
  https://www.transportstyrelsen.se/sv/vagtrafik/yrkestrafik/kor-och-vilotider/Fardskrivarkort/forarkort/
- Project repository:  
  https://github.com/mahmud25-cell/driver_card
