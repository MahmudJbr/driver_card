CREATE TABLE `driver_cards` (
  `cardID` int NOT NULL AUTO_INCREMENT,
  `userID` int NOT NULL,
  `card_number` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `issued_date` date NOT NULL,
  `expiry_date` date NOT NULL,
  `status` enum('ACTIVE','EXPIRED','LOST','REPLACED') COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVE',
  PRIMARY KEY (`cardID`),
  UNIQUE KEY `userID` (`userID`),
  UNIQUE KEY `card_number` (`card_number`),
  KEY `idx_cards_user` (`userID`),
  CONSTRAINT `driver_cards_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
SELECT * FROM eforarkort.driver_cards;