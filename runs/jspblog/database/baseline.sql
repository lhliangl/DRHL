-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: portal
-- ------------------------------------------------------
-- Server version	5.5.53

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `portal`
--

/*!40000 DROP DATABASE IF EXISTS `portal`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `portal` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `portal`;

--
-- Table structure for table `etc`
--

DROP TABLE IF EXISTS `etc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `etc` (
  `header` varchar(250) NOT NULL DEFAULT '',
  `footer` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`header`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etc`
--

LOCK TABLES `etc` WRITE;
/*!40000 ALTER TABLE `etc` DISABLE KEYS */;
INSERT INTO `etc` VALUES ('<h1>JSP Test</h1>','<i>Made by Anthony</i>');
/*!40000 ALTER TABLE `etc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news` (
  `headline` varchar(250) NOT NULL DEFAULT '',
  `author` varchar(50) DEFAULT NULL,
  `body` longtext,
  `date` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`headline`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
INSERT INTO `news` VALUES ('Java','admin@qq.com','','Wed Mar 12 10:18:10 CST 2025'),('vbnvbn','3dvrem','','Fri Mar 27 10:17:18 CST 2026'),('vbndfg','3dvrem','','Thu Mar 26 21:58:34 CST 2026'),('z7BjqL','p5WyxO','','Mon Sep 22 20:15:39 CST 2025'),('k6Hwta','DfaCFIVv','','Mon Sep 22 20:12:35 CST 2025'),('hzCQPk','user','','Mon Sep 22 19:39:20 CST 2025'),('ZAP','ada','','Fri Mar 27 11:18:44 CST 2026'),('ghj','3dvrem','','Fri Mar 27 10:22:25 CST 2026'),('GwbCTc','DfaCFIVv','','Mon Sep 22 16:07:39 CST 2025'),('The First New','admin@qq.com','','Mon Sep 22 11:23:00 CST 2025'),('daweadew','3dvrem','','Thu Mar 26 20:41:24 CST 2026'),('','3dvrem','','Fri Mar 27 11:27:15 CST 2026'),('JNROku','3dvrem','','Fri Mar 27 11:27:16 CST 2026'),('QvfSPO','','','Fri Mar 27 11:27:30 CST 2026'),('AokwZT','3dvrem','','Wed Jul 01 16:40:36 CST 2026'),('qbSfOd','','','Wed Jul 01 16:48:06 CST 2026');
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `name` varchar(50) DEFAULT NULL,
  `author` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`author`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('admin','admin@qq.com'),('lhl','user'),('mTbs39cj','DfaCFIVv'),('TiudCD','LpM1H2'),('zk3Oh9','p5WyxO'),('R8LQoT','3dvrem'),('null','null'),('L8FXoa','wuk5fG'),('asd','ada'),('tttt','tttt'),('oooo','oooo'),('zxcwad','zxcz'),('mmmmmm','mmmmm'),('bnm','bnm'),('hjk','hjk'),('dfg','dfg'),('ZAP','ZAP'),('BoSUhmuz','BoSUhm'),('',''),('wAHAKRqt','wAHAKR'),('CcwtLIUJ','CcwtLI');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'portal'
--

--
-- Dumping routines for database 'portal'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-01 21:05:04
