DELIMITER $$
CREATE DEFINER=`root`@`localhost` FUNCTION `total_kortid_seconds`(p_userID INT, p_from DATE, p_to DATE) RETURNS int
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
