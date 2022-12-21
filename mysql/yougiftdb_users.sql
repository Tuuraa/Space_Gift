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
  `name` varchar(60) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date` date DEFAULT NULL,
  `money` decimal(10,0) DEFAULT '0',
  `date_now` datetime DEFAULT NULL,
  `link_name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `depozit` double DEFAULT '0',
  `gift_value` double DEFAULT '0',
  `now_depozit` double DEFAULT '0',
  `planet` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT '0',
  `step` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT '1',
  `first_dep` tinyint DEFAULT '1',
  `status` tinyint DEFAULT '0',
  `count_ref` int DEFAULT '0',
  `active` tinyint DEFAULT '0',
  `gift_money` double DEFAULT '0',
  `amount_gift_money` double DEFAULT '0',
  `ref_money` double DEFAULT '0',
  `jump` tinyint DEFAULT '0',
  `last_withd` datetime DEFAULT NULL,
  `code` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `percent_ref_money` float DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (14,378632841,NULL,'Dan?','2022-12-10',5000,'2022-12-21 15:19:44','linkbrt',0,0,0,'0','1',1,0,1,0,180,0,5000,0,'2022-12-10 16:50:08',NULL,0),(29,1328872217,NULL,'Матвей','2022-12-14',10,'2022-12-14 15:54:21','m_kravts',10,0,0,'0','1',1,0,0,0,10,0,0,0,'2022-12-14 15:54:21',NULL,0),(42,668776362,NULL,'Nikolay','2022-12-15',10000,'2022-12-21 15:19:45','dolgocom',10000,0,0,'1','1',0,1,2,1,240,0,0,0,'2022-12-15 17:27:09',NULL,0),(45,1167759105,NULL,'Ivan','2022-12-15',0,'2022-12-15 18:16:39','huff_g',0,0,0,'0','1',1,0,0,0,0,0,0,0,'2022-12-15 18:16:39',NULL,0),(53,932803482,NULL,'BANG','2022-12-16',35000,'2022-12-21 15:19:45','Bang_Bros007',55000,0,0,'1','1',1,0,0,0,10750,15000,0,0,'2022-12-16 16:17:12','Тех',0),(73,NULL,NULL,NULL,NULL,0,NULL,NULL,0,0,0,'0','1',1,0,0,0,0,0,0,0,NULL,NULL,0),(74,288113313,NULL,'Михаил','2022-12-19',30,'2022-12-19 17:17:02','zeusmisha',30,0,0,'0','1',1,0,0,0,30,0,0,0,'2022-12-19 17:17:02','Корвет',0),(75,288113313,NULL,'Михаил','2022-12-19',30,'2022-12-19 17:18:21','zeusmisha',30,0,0,'0','1',1,0,0,0,30,0,0,0,'2022-12-19 17:18:21','Корвет',0),(78,855151774,NULL,'Tura','2022-12-21',20000,'2022-12-21 18:32:22','bluabitch',0,0,0,'1','1',1,0,0,0,10000,0,0,0,'2022-12-21 18:32:22','dwaw',0);
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

-- Dump completed on 2022-12-21 21:52:23
