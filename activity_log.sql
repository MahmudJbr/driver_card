CREATE TABLE `activity_logs` (
  `logID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `vehicleID` int DEFAULT NULL,
  `startTid` datetime NOT NULL,
  `slutTid` datetime NOT NULL,
  `activity` enum('DRIVE','REST','OTHER') COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` enum('MANUAL','SYSTEM') COLLATE utf8mb4_unicode_ci DEFAULT 'MANUAL',
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`logID`),
  KEY `vehicleID` (`vehicleID`),
  KEY `idx_activity_user_time` (`userID`,`startTid`),
  CONSTRAINT `activity_logs_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`),
  CONSTRAINT `activity_logs_ibfk_2` FOREIGN KEY (`vehicleID`) REFERENCES `vehicles` (`vehicleID`),
  CONSTRAINT `chk_activity_time` CHECK ((`slutTid` > `startTid`))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
