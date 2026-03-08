CREATE TABLE `users` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `fName` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `lName` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `DOB` date NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('förare','admin') COLLATE utf8mb4_unicode_ci DEFAULT 'förare',
  `dateMod` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
