CREATE TABLE `driving_sessions` (
  `sessionID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `vehicleID` int DEFAULT NULL,
  `startTid` datetime NOT NULL,
  `slutTid` datetime NOT NULL,
  `körtid` time DEFAULT NULL,
  `sträcka` int DEFAULT '0',
  `status` enum('avslutad','pauserad','aktiv') COLLATE utf8mb4_unicode_ci DEFAULT 'avslutad',
  PRIMARY KEY (`sessionID`),
  KEY `idx_sessions_user` (`userID`),
  KEY `idx_sessions_vehicle` (`vehicleID`),
  FOREIGN KEY (`userID`) REFERENCES `users` (`userID`),
  FOREIGN KEY (`vehicleID`) REFERENCES `vehicles` (`vehicleID`),
  CONSTRAINT `chk_time_order` CHECK ((`slutTid` > `startTid`))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
