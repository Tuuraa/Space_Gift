-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: yougiftdb
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `referrer_id` int DEFAULT NULL,
  `name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date` date DEFAULT NULL,
  `money` decimal(10,0) DEFAULT '0',
  `date_now` datetime DEFAULT NULL,
  `link_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `depozit` double DEFAULT '0',
  `gift_value` double DEFAULT '0',
  `now_depozit` double DEFAULT '0',
  `planet` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '0',
  `step` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '1',
  `first_dep` tinyint DEFAULT '1',
  `status` tinyint DEFAULT '0',
  `count_ref` int DEFAULT '0',
  `active` tinyint DEFAULT '0',
  `gift_money` double DEFAULT '0',
  `amount_gift_money` double DEFAULT '0',
  `ref_money` double DEFAULT '0',
  `jump` tinyint DEFAULT '0',
  `last_withd` datetime DEFAULT NULL,
  `code` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `percent_ref_money` float DEFAULT '0',
  `reinvest` float DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (14,378632841,NULL,'Dan?','2022-12-10',25000,'2022-12-28 20:36:06','linkbrt',0,0,0,'0','1',0,0,3,0,1020,20000,5000,0,'2022-12-10 16:50:08',NULL,0,0),(93,932803482,NULL,'BANG','2022-12-25',110000,'2022-12-28 20:36:07','Bang_Bros007',5000,0,0,'1','1',0,0,2,0,20060,100000,0,0,'2022-12-25 14:25:47','jj',0,0),(94,288113313,NULL,'Михаил','2022-12-25',15000,'2022-12-25 18:18:49','zeusmisha',0,0,5000,'1','1',0,0,0,0,10000,10000,0,0,'2022-12-25 18:18:49','Й',0,0),(106,628931867,NULL,'meow','2022-12-29',0,'2022-12-29 17:20:38',NULL,0,0,0,'0','1',1,0,0,0,0,0,0,0,'2022-12-29 17:20:38','123',0,0),(107,415321692,NULL,'?','2022-12-29',5000,'2022-12-29 17:20:47','teaeye',5000,0,0,'0','1',1,0,0,0,0,0,0,0,'2022-12-29 17:20:47','12434324',0,0),(108,855151774,NULL,'Tura','2022-12-29',0,'2022-12-29 17:35:10','bluabitch',0,0,15000,'1','1',0,1,0,0,10000,-5000,0,0,'2022-12-29 17:35:10','⬅ Вернуться',0,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-29 20:58:36
