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
