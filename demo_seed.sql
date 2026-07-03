-- Demo data for e-DriverCard.
-- Import this after the base tables have been created.
-- The IDs are fixed so this file can be imported multiple times.

CREATE TABLE IF NOT EXISTS `violations` (
  `violationID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `sessionID` int DEFAULT NULL,
  `violationstyp` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `detaljer` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `datum` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`violationID`),
  KEY `idx_violations_user` (`userID`),
  KEY `idx_violations_session` (`sessionID`),
  CONSTRAINT `violations_user_fk` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`),
  CONSTRAINT `violations_session_fk` FOREIGN KEY (`sessionID`) REFERENCES `driving_sessions` (`sessionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (`userID`, `fName`, `lName`, `email`, `DOB`, `password`, `role`)
VALUES
  (101, 'Anna', 'Andersson', 'anna.driver@demo.se', '1988-04-12', 'demo-password', 'förare'),
  (102, 'Omar', 'Nilsson', 'omar.driver@demo.se', '1991-09-23', 'demo-password', 'förare'),
  (103, 'Lina', 'Berg', 'lina.driver@demo.se', '1985-12-07', 'demo-password', 'förare'),
  (900, 'Sara', 'Lindström', 'sara.manager@demo.se', '1982-06-18', 'demo-password', 'admin')
ON DUPLICATE KEY UPDATE
  `fName` = VALUES(`fName`),
  `lName` = VALUES(`lName`),
  `email` = VALUES(`email`),
  `DOB` = VALUES(`DOB`),
  `password` = VALUES(`password`),
  `role` = VALUES(`role`);

INSERT INTO `vehicles` (`vehicleID`, `registreringsnummer`, `fordonstyp`, `fabrikat`, `årsmodell`)
VALUES
  (201, 'ABC123', 'Dragbil', 'Volvo FH16', 2022),
  (202, 'TRK845', 'Fjärrbil', 'Scania R 450', 2021),
  (203, 'NXT512', 'Distributionsbil', 'Mercedes Actros', 2023)
ON DUPLICATE KEY UPDATE
  `registreringsnummer` = VALUES(`registreringsnummer`),
  `fordonstyp` = VALUES(`fordonstyp`),
  `fabrikat` = VALUES(`fabrikat`),
  `årsmodell` = VALUES(`årsmodell`);

INSERT INTO `driver_cards` (`cardID`, `userID`, `card_number`, `issued_date`, `expiry_date`, `status`)
VALUES
  (301, 101, 'SE-DRV-2026-0101', '2023-02-10', '2027-02-10', 'ACTIVE'),
  (302, 102, 'SE-DRV-2026-0102', '2022-11-14', '2026-08-14', 'ACTIVE'),
  (303, 103, 'SE-DRV-2026-0103', '2021-05-20', '2026-07-28', 'ACTIVE')
ON DUPLICATE KEY UPDATE
  `userID` = VALUES(`userID`),
  `card_number` = VALUES(`card_number`),
  `issued_date` = VALUES(`issued_date`),
  `expiry_date` = VALUES(`expiry_date`),
  `status` = VALUES(`status`);

INSERT INTO `driving_sessions` (`sessionID`, `userID`, `vehicleID`, `startTid`, `slutTid`, `körtid`, `sträcka`, `status`)
VALUES
  (1001, 101, 201, '2026-01-05 06:15:00', '2026-01-05 14:20:00', '08:05:00', 482, 'avslutad'),
  (1002, 101, 202, '2026-01-08 05:45:00', '2026-01-08 16:10:00', '10:25:00', 641, 'avslutad'),
  (1003, 101, 201, '2026-01-12 07:00:00', '2026-01-12 13:45:00', '06:45:00', 338, 'avslutad'),
  (1004, 102, 202, '2026-01-06 06:30:00', '2026-01-06 15:00:00', '08:30:00', 517, 'avslutad'),
  (1005, 102, 203, '2026-01-10 08:00:00', '2026-01-10 16:20:00', '08:20:00', 296, 'avslutad'),
  (1006, 103, 203, '2026-01-07 05:50:00', '2026-01-07 14:15:00', '08:25:00', 412, 'avslutad'),
  (1007, 103, 201, '2026-01-14 06:10:00', '2026-01-14 15:55:00', '09:45:00', 588, 'avslutad')
ON DUPLICATE KEY UPDATE
  `userID` = VALUES(`userID`),
  `vehicleID` = VALUES(`vehicleID`),
  `startTid` = VALUES(`startTid`),
  `slutTid` = VALUES(`slutTid`),
  `körtid` = VALUES(`körtid`),
  `sträcka` = VALUES(`sträcka`),
  `status` = VALUES(`status`);

INSERT INTO `activity_logs` (`logID`, `userID`, `vehicleID`, `startTid`, `slutTid`, `activity`, `source`, `notes`)
VALUES
  (4001, 101, 201, '2026-01-05 06:15:00', '2026-01-05 14:20:00', 'DRIVE', 'SYSTEM', 'Stockholm to Malmö delivery'),
  (4002, 101, 201, '2026-01-05 10:35:00', '2026-01-05 11:20:00', 'REST', 'MANUAL', 'Lunchrast vid Jönköping'),
  (4003, 101, 202, '2026-01-08 05:45:00', '2026-01-08 16:10:00', 'DRIVE', 'SYSTEM', 'Long haul with delay at terminal'),
  (4004, 102, 202, '2026-01-06 06:30:00', '2026-01-06 15:00:00', 'DRIVE', 'SYSTEM', 'Göteborg route'),
  (4005, 102, 203, '2026-01-10 12:15:00', '2026-01-10 13:00:00', 'REST', 'MANUAL', 'Scheduled break'),
  (4006, 103, 203, '2026-01-07 05:50:00', '2026-01-07 14:15:00', 'DRIVE', 'SYSTEM', 'Regional delivery route'),
  (4007, 103, 201, '2026-01-14 06:10:00', '2026-01-14 15:55:00', 'DRIVE', 'SYSTEM', 'Extended route due to traffic diversion')
ON DUPLICATE KEY UPDATE
  `userID` = VALUES(`userID`),
  `vehicleID` = VALUES(`vehicleID`),
  `startTid` = VALUES(`startTid`),
  `slutTid` = VALUES(`slutTid`),
  `activity` = VALUES(`activity`),
  `source` = VALUES(`source`),
  `notes` = VALUES(`notes`);

INSERT INTO `events` (`eventID`, `userID`, `event_type`, `created_at`, `due_date`, `message`, `is_resolved`)
VALUES
  (7001, 101, 'OVERDRIVE', '2026-01-08 16:12:00', NULL, 'Driving session exceeded the 9 hour daily driving limit.', FALSE),
  (7002, 103, 'OVERDRIVE', '2026-01-14 15:57:00', NULL, 'Driving session exceeded the recommended daily driving time.', FALSE),
  (7003, 103, 'CARD_EXPIRY_SOON', '2026-01-15 09:00:00', '2026-07-28', 'Driver card expires soon. Renewal should be planned before summer routes.', FALSE),
  (7004, 102, 'INFO', '2026-01-10 16:45:00', NULL, 'Weekly route completed without open violations.', TRUE)
ON DUPLICATE KEY UPDATE
  `userID` = VALUES(`userID`),
  `event_type` = VALUES(`event_type`),
  `created_at` = VALUES(`created_at`),
  `due_date` = VALUES(`due_date`),
  `message` = VALUES(`message`),
  `is_resolved` = VALUES(`is_resolved`);

INSERT INTO `violations` (`violationID`, `userID`, `sessionID`, `violationstyp`, `detaljer`, `datum`)
VALUES
  (8001, 101, 1002, 'MAX_DAILY_DRIVE', '10h 25m driving time recorded on session 1002.', '2026-01-08 16:12:00'),
  (8002, 103, 1007, 'MAX_DAILY_DRIVE', '9h 45m driving time recorded on session 1007.', '2026-01-14 15:57:00')
ON DUPLICATE KEY UPDATE
  `userID` = VALUES(`userID`),
  `sessionID` = VALUES(`sessionID`),
  `violationstyp` = VALUES(`violationstyp`),
  `detaljer` = VALUES(`detaljer`),
  `datum` = VALUES(`datum`);
