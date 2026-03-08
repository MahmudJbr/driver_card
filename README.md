Project Idea
For this assignment, I designed and implemented a system called the Driver Card System. The purpose of the system is to digitally manage driver identity, driving time, and rest periods through a web-based platform, reducing the dependency on physical driver cards and manual reporting.
Problem Description
Today, professional drivers rely on physical driver cards and vehicle tachographs to record their driving and rest times. This creates several practical and financial problems:
•	Drivers must insert their card into the tachograph to view their driving data
•	If a card is lost or damaged, the driver must manually record driving time, which can lead to cheating
•	Producing and replacing physical driver cards is expensive for both drivers and authorities
•	Drivers cannot easily check their driving and rest time from home
•	Transport companies have limited real-time insight into how their drivers are performing
Because of this, both drivers and transport companies lack a simple and centralized digital solution to monitor driving time, plan work safely, and reduce costs.
Proposed Solution
The Driver Card System provides a digital alternative where drivers can log into a website and view their driving sessions, rest periods, and activities without needing to use a physical driver card.
In the current version of the system:
•	Drivers log in using email and password
•	The system stores driving sessions, rest periods, and activities
•	Drivers can see their own driving and rest time from home
•	Company owners  can monitor their drivers and plan work schedules more safely
Future Vision of the System
In the future, the system is planned to expand and connect multiple stakeholders:
•	Police authorities
•	Transport authorities
•	Drivers
•	Haulage companies
•	Truck manufacturers
The long-term goal is to integrate the system directly with trucks through Bluetooth connectivity, allowing the vehicle to communicate with the website automatically.
Drivers would then log in using BankID instead of email and password, providing secure digital identification. This would remove the need for physical driver cards and reduce administrative costs.
Main Features of the Current System
The system records driving sessions digitally, reducing the risk of cheating or incorrect manual reporting when a physical driver card is not available.
Activity Logging
All activities such as driving, resting, and other work are stored, providing a complete daily overview.
Company Monitoring
Managers can see how much legal driving time each driver has left and plan routes accordingly. Drivers with more available driving time can be assigned longer trips, while drivers with less time can be given shorter routes.
Data Source
The data used in this project is generated for demonstration purposes. Sample drivers, vehicles, and driving sessions are inserted into the database to simulate real-world driver activity.
Logical Data Model
The logical data model represents the main entities in the e-Driver Card System.
The most important entities are User, DriverCard, Vehicle, Driving_sessions, Violation, Event and Activity_log.
The User entity represents both drivers and company managers in the system. Each user has attributes such as userID, first name, last name, email and role.
The DriverCard entity represents the digital driver identity that replaces the traditional physical driver card. Each driver has one digital driver card connected to their account.
The Vehicle entity represents trucks used by drivers. Vehicles have attributes such as vehicleID, registration number, vehicle type, model and brand.
The Driving_sessions entity represents a driving activity performed by a driver with a specific vehicle. Each session records information such as distance, driving time and timestamps.
The Violation entity stores information about illegal driving behaviour, for example exceeding legal driving time limits.
The Event entity represents system notifications or warnings that can be sent to drivers.
The Activity_log entity records driver activities such as driving, resting or other work.
 
Relationships Between Entities
The relationships between the entities are shown in the E/R diagram using diamond shapes. Cardinality is represented using 1 and M.
1.	Each User is associated with one digital DriverCard.
2.	A User can have many Driving_sessions, but each driving session belongs to one user.
3.	A Vehicle can be used in many Driving_sessions, but each session involves one vehicle.
4.	A Driving_session can result in multiple Violations, but each violation is linked to one specific session.
5.	A User can have many Violations, but each violation belongs to one user.
6.	A User can receive multiple Events, such as warnings or notifications.
7.	A User can have many Activity_log entries, but each log entry belongs to one user.
8.	A Vehicle can be connected to many Activity_log entries, but an activity log may or may not involve a vehicle.
The system also uses database triggers to automate important logic in the database. For example, when a new driving session is inserted, a trigger automatically calculates the driving time from the start and end timestamps. If the driving time exceeds the legal limit, another trigger automatically creates a violation record and generates a warning event for the driver.
SQL Queries
1. Show a driver’s driving history including vehicle information
This query shows all driving sessions for a specific driver together with vehicle information. It is a multirelation query because it combines data from the tables driving_sessions and vehicles. The query uses JOIN by matching driving_sessions.vehicleID with vehicles.vehicleID.
SELECT
    ds.sessionID,
    ds.startTid,
    ds.slutTid,
    ds.körtid,
    ds.sträcka,
    v.registreringsnummer,
    v.fordonstyp,
    v.fabrikat
FROM driving_sessions ds
JOIN vehicles v ON ds.vehicleID = v.vehicleID
WHERE ds.userID = ?
ORDER BY ds.startTid DESC;

2. Calculate total driving time between two dates for a driver in hours
This query calculates the total driving time in hours for a specific driver during a selected period. It uses the aggregation function SUM() together with TIME_TO_SEC() to convert the stored driving time into seconds and then into hours.
SELECT
    ROUND(SUM(TIME_TO_SEC(ds.körtid)) / 3600, 2) AS total_drive_hours
FROM driving_sessions ds
WHERE ds.userID = ?
  AND ds.startTid BETWEEN ? AND ?;
3. Show a driver’s violations with session and vehicle context
This query shows all violations for a specific driver and includes related driving session and vehicle information. It is a multirelation query because it combines data from violations, driving_sessions, and vehicles.
SELECT
    vio.violationID,
    vio.violationstyp,
    vio.detaljer,
    vio.datum,
    ds.sessionID,
    ds.startTid,
    ds.slutTid,
    ds.körtid,
    v.registreringsnummer,
    v.fordonstyp
FROM violations vio
LEFT JOIN driving_sessions ds ON vio.sessionID = ds.sessionID
LEFT JOIN vehicles v ON ds.vehicleID = v.vehicleID
WHERE vio.userID = ?
ORDER BY vio.datum DESC;

4. Show dashboard statistics for a driver
This query for a driver dashboard. It counts the total number of driving sessions and sums the total distance driven. The query uses the aggregation functions COUNT() and SUM().
SELECT
    COUNT(sessionID) AS total_sessions,
    COALESCE(SUM(sträcka), 0) AS total_distance_km
FROM driving_sessions
WHERE userID = ?;
5. Show each driver’s total driving time within a selected date range
This query is intended for transport company managers. It calculates the total driving hours for each driver within a selected date range. It uses both JOIN and GROUP BY.
SELECT
    u.userID,
    u.fName,
    u.lName,
    ROUND(SUM(TIME_TO_SEC(ds.körtid)) / 3600, 2) AS total_drive_hours,
    COALESCE(SUM(ds.sträcka), 0) AS total_distance_km
FROM users u
JOIN driving_sessions ds ON u.userID = ds.userID
WHERE ds.startTid BETWEEN ? AND ?
GROUP BY u.userID, u.fName, u.lName
ORDER BY total_drive_hours ASC;
6. Stored Procedure: generate_card_expiry_events
This stored procedure is used to automatically generate warning events for driver cards that are close to their expiry date.
The procedure takes one input parameter, p_days, which specifies how many days ahead the system should check. It searches the driver_cards table for active cards whose expiry date falls within the specified number of days. For each matching card, the procedure inserts a new event into the events table with the event type CARD_EXPIRY_SOON.
The procedure also includes a NOT EXISTS condition to prevent duplicate unresolved expiry warnings for the same user.

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `generate_card_expiry_events`(IN p_days INT)
BEGIN
  INSERT INTO events (userID, event_type, due_date, message)
  SELECT
    dc.userID,
    'CARD_EXPIRY_SOON',
    dc.expiry_date,
    CONCAT('Driver card expires on ', dc.expiry_date, ' (within ', p_days, ' days).')
  FROM driver_cards dc
  WHERE dc.status = 'ACTIVE'
    AND dc.expiry_date <= (CURRENT_DATE + INTERVAL p_days DAY)
    AND NOT EXISTS (
      SELECT 1
      FROM events e
      WHERE e.userID = dc.userID
        AND e.event_type = 'CARD_EXPIRY_SOON'
        AND e.is_resolved = FALSE
    );
END$$
DELIMITER ;
7. Stored Procedure: weekly_report
This stored procedure generates a weekly driving report for all drivers within a specified time period. It takes two input parameters: p_from and p_to, which define the start and end dates for the report.
The procedure retrieves driving session data from the driving_sessions table and joins it with the users table to obtain driver names. It then groups the results by driver and week number using the YEARWEEK() function.
Several aggregation functions are used:
•	SUM() to calculate the total driving time
•	SUM() to calculate the total distance driven
•	COUNT() to count the number of driving sessions

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `weekly_report`(IN p_from DATE, IN p_to DATE)
BEGIN
  SELECT
    u.userID AS user_id,
    CONCAT(u.fName, ' ', u.lName) AS driver_name,
    YEARWEEK(ds.startTid, 1) AS week_no,
    ROUND(SUM(TIME_TO_SEC(ds.körtid)) / 3600, 2) AS total_drive_hours,
    SUM(ds.sträcka) AS total_distance_km,
    COUNT(*) AS session_count
  FROM driving_sessions ds
  JOIN users u ON u.userID = ds.userID
  WHERE DATE(ds.startTid) BETWEEN p_from AND p_to
    AND ds.status = 'avslutad'
  GROUP BY u.userID, YEARWEEK(ds.startTid, 1)
  ORDER BY week_no DESC, total_drive_hours DESC;
END$$
DELIMITER ;
8.	Function: total_kortid_seconds
This function calculates the total driving time in seconds for a specific driver within a selected date range.
The function takes three input parameters:
•	p_userID – the ID of the driver
•	p_from – start date of the time interval
•	p_to – end date of the time interval
The function retrieves all completed driving sessions for the specified driver and time period from the driving_sessions table. It then sums the driving time using the TIME_TO_SEC() function to convert the stored time values into seconds.
The COALESCE() function is used to ensure that the function returns 0 if no driving sessions exist in the selected time period.
DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `total_kortid_seconds`(
    p_userID INT,
    p_from DATE,
    p_to DATE
) RETURNS INT
DETERMINISTIC
BEGIN
  DECLARE total INT;

  SELECT COALESCE(SUM(TIME_TO_SEC(`körtid`)), 0)
  INTO total
  FROM driving_sessions
  WHERE userID = p_userID
    AND DATE(`startTid`) BETWEEN p_from AND p_to
    AND status = 'avslutad';

  RETURN total;
END$$

DELIMITER ;
https://www.transportstyrelsen.se/sv/vagtrafik/yrkestrafik/kor-och-vilotider/Fardskrivarkort/forarkort/
https://github.com/mahmud25-cell/driver_card
http://127.0.0.1:5000
E/R diagram of the e-Driver Card System data model.
 

