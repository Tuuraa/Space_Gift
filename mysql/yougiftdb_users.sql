-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: localhost    Database: yougiftdb
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
  `user_id` text COLLATE utf8mb4_unicode_ci,
  `referrer_id` text COLLATE utf8mb4_unicode_ci,
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
  `refgift` tinyint DEFAULT '0',
  `is_space_money` tinyint DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (10,'415321692','855151774','?','2022-12-29',75000,'2022-12-29 20:17:39','teaeye',55000,0,0,'1','1',0,1,0,0,0,15000,0,0,'2022-12-29 20:17:39','676787',0,10000,1),(12,'628931867','855151774','meow','2022-12-29',15000,'2022-12-29 20:29:22','EluciferE',0,0,0,'1','1',0,0,0,0,8000,15000,0,0,'2022-12-29 20:29:22','? Реферальная ссылка',0,0,1),(23,'1328872217',NULL,'Матвей','2022-12-30',-40000,'2022-12-29 22:32:07','m_kravts',0,0,15000,'1','1',1,1,1,0,0,0,0,0,'2022-12-29 22:32:07','1234',0,0,0),(24,'1396645031','1328872217','??‍? Hermes оператор | Обмен BTC, EXMO, ETH, LTC ?','2022-12-30',0,'2022-12-29 22:32:24','hermes_btc_admin',0,0,15000,'1','1',0,1,0,0,10000,0,0,0,'2022-12-29 22:32:24','Про',0,0,1);
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

-- Dump completed on 2022-12-30  1:38:45
