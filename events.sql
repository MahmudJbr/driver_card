CREATE TABLE `events` (
  `eventID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `event_type` enum('CARD_EXPIRY_SOON','OVERDRIVE','INFO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `due_date` date DEFAULT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_resolved` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`eventID`),
  KEY `idx_events_user_unresolved` (`userID`,`is_resolved`),
  CONSTRAINT `events_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
