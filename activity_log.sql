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
  FOREIGN KEY (`userID`) REFERENCES `users` (`userID`),
  FOREIGN KEY (`vehicleID`) REFERENCES `vehicles` (`vehicleID`),
  CHECK ((`slutTid` > `startTid`))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
