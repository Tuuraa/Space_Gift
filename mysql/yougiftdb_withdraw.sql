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
-- Table structure for table `withdraw`
--

DROP TABLE IF EXISTS `withdraw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `withdraw` (
  `card` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `data` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `date` datetime DEFAULT NULL,
  `status` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amount_commission` float DEFAULT NULL,
  `amount_crypt` float DEFAULT NULL,
  `type_crypt` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `withdraw`
--

LOCK TABLES `withdraw` WRITE;
/*!40000 ALTER TABLE `withdraw` DISABLE KEYS */;
INSERT INTO `withdraw` VALUES ('3143434134143','bank',5000,'Rf',855151774,1,'2022-12-09 15:25:58',NULL,NULL,NULL,NULL),('4234','bank',1000,'кар',855151774,2,'2022-12-09 16:09:29','В ожидании',NULL,NULL,NULL),('13131341','bank',1000,'dwdas',855151774,3,'2022-12-09 17:16:54','В ожидании',700,NULL,NULL),('wd123awd34','crypt',1000,'rfwa',855151774,4,'2022-12-09 17:21:01','В ожидании',700,0,'btc'),('dwad123e23','crypt',1000,'rfh',855151774,5,'2022-12-09 17:26:39','В ожидании',700,1000,'btc'),('wdadw123','crypt',1000,'wdawd',855151774,6,'2022-12-09 17:28:35','В ожидании',700,0.000928587,'btc'),('123fefes','crypt',1000,'dwada',855151774,7,'2022-12-09 17:32:23','В ожидании',700,0.000930762,'btc'),('2682836738727','bank',1000,'Карданов Артур Ауесович',855151774,8,'2022-12-17 21:33:06','В ожидании',800,NULL,NULL),('gujy5742:','crypt',10000,'Карданов Артур Ауесович',855151774,9,'2022-12-17 22:03:14','В ожидании',8000,2.42272,'LTC'),('36893','bank',1000,'Кард',855151774,10,'2022-12-17 22:07:31','В ожидании',800,NULL,NULL),('24793 6327 6743 4690','bank',1000,'КАР',855151774,11,'2022-12-17 22:09:29','В ожидании',800,NULL,NULL),('3579','bank',1000,'прон',855151774,12,'2022-12-17 22:15:57','В ожидании',800,NULL,NULL),('3578','bank',1000,'если',855151774,13,'2022-12-17 22:21:45','В ожидании',800,NULL,NULL),('fhnj36794','crypt',5000,'Кард',855151774,14,'2022-12-17 22:28:00','В ожидании',4000,1.20831,'LTC'),('12313421341','bank',1000,'Карл Артур \\',855151774,15,'2022-12-18 15:55:00','В ожидании',800,NULL,NULL),('356677788888999','bank',2000,'Tgftyggyy',628931867,16,'2022-12-29 21:41:29','В ожидании',1600,NULL,NULL);
/*!40000 ALTER TABLE `withdraw` ENABLE KEYS */;
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
