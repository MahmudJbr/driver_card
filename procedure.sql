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

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `weekly_report`(IN p_from DATE, IN p_to DATE)
BEGIN
  SELECT
    u.userID AS user_id,
    CONCAT(u.fName, ' ', u.lName) AS driver_name,
    YEARWEEK(ds.`startTid`, 1) AS week_no,
    ROUND(SUM(TIME_TO_SEC(ds.`körtid`)) / 3600, 2) AS total_drive_hours,
    SUM(ds.`sträcka`) AS total_distance_km,
    COUNT(*) AS session_count
  FROM driving_sessions ds
  JOIN users u ON u.userID = ds.userID
  WHERE DATE(ds.`startTid`) BETWEEN p_from AND p_to
    AND ds.`status` = 'avslutad'
  GROUP BY u.userID, YEARWEEK(ds.`startTid`, 1)
  ORDER BY week_no DESC, total_drive_hours DESC;
END$$
DELIMITER ;
