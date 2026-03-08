CREATE TABLE `vehicles` (
  `vehicleID` int NOT NULL AUTO_INCREMENT,
  `registreringsnummer` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fordonstyp` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fabrikat` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `årsmodell` int DEFAULT NULL,
  PRIMARY KEY (`vehicleID`),
  UNIQUE KEY `registreringsnummer` (`registreringsnummer`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
