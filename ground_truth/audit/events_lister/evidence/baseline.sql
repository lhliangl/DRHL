-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: events_lister
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
-- Current Database: `events_lister`
--

/*!40000 DROP DATABASE IF EXISTS `events_lister`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `events_lister` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `events_lister`;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin` (
  `id` int(1) NOT NULL AUTO_INCREMENT,
  `uname` varchar(255) NOT NULL,
  `pword` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'admin@qq.com','ed057c7f79e1f896f641242d834ed2b1'),(2,'user1@qq.com','ed057c7f79e1f896f641242d834ed2b1'),(3,'user2@qq.com','ed057c7f79e1f896f641242d834ed2b1');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `id` int(6) NOT NULL AUTO_INCREMENT,
  `event` text NOT NULL,
  `hour` varchar(2) NOT NULL,
  `minute` varchar(2) NOT NULL,
  `ampm` varchar(2) NOT NULL,
  `hour_end` varchar(2) NOT NULL,
  `minute_end` varchar(2) NOT NULL,
  `ampm_end` varchar(2) NOT NULL,
  `month` varchar(2) NOT NULL,
  `day` varchar(2) NOT NULL,
  `year` varchar(4) NOT NULL,
  `month_end` varchar(2) NOT NULL,
  `day_end` varchar(2) NOT NULL,
  `year_end` varchar(4) NOT NULL,
  `month_show` varchar(2) NOT NULL,
  `day_show` varchar(2) NOT NULL,
  `year_show` varchar(4) NOT NULL,
  `location` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `link` varchar(255) NOT NULL,
  `link_name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `html` int(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'Test Event','12','00','PM','02','00','PM','12','31','2026','12','31','2026','12','31','2026','Test location','you@yourwebsite.com','415-555-1212','http://www.yourwebsite.com','Your web site','This is the test event description.  You can either delete this event, by clicking the delete link in the all events section, or you can edit the event, and set the date in the past.  All events that are scheduled in the past, will automatically disappear from the publicly viewable events page.',0),(2,'DRHL Test Event 01','09','00','AM','10','00','AM','07','01','2026','07','01','2026','07','01','2026','DRHL Test Room 01','event01@example.test','13800130001','','','Seeded DRHL test event 01 for crawling and access-control testing.',0),(3,'DRHL Test Event 02','10','30','AM','11','30','AM','07','02','2026','07','02','2026','07','02','2026','DRHL Test Room 02','event02@example.test','13800130002','','','Seeded DRHL test event 02 for crawling and access-control testing.',0),(4,'DRHL Test Event 03','11','00','AM','12','00','PM','07','03','2026','07','03','2026','07','03','2026','DRHL Test Room 03','event03@example.test','13800130003','','','Seeded DRHL test event 03 for crawling and access-control testing.',0),(5,'DRHL Test Event 04','12','30','PM','13','30','PM','07','04','2026','07','04','2026','07','04','2026','DRHL Test Room 04','event04@example.test','13800130004','','','Seeded DRHL test event 04 for crawling and access-control testing.',0),(6,'DRHL Test Event 05','13','00','PM','14','00','PM','07','05','2026','07','05','2026','07','05','2026','DRHL Test Room 05','event05@example.test','13800130005','','','Seeded DRHL test event 05 for crawling and access-control testing.',0),(7,'DRHL Test Event 06','14','30','PM','15','30','PM','07','06','2026','07','06','2026','07','06','2026','DRHL Test Room 06','event06@example.test','13800130006','','','Seeded DRHL test event 06 for crawling and access-control testing.',0),(8,'DRHL Test Event 07','15','00','PM','16','00','PM','07','07','2026','07','07','2026','07','07','2026','DRHL Test Room 07','event07@example.test','13800130007','','','Seeded DRHL test event 07 for crawling and access-control testing.',0),(9,'DRHL Test Event 08','16','30','PM','17','30','PM','07','08','2026','07','08','2026','07','08','2026','DRHL Test Room 08','event08@example.test','13800130008','','','Seeded DRHL test event 08 for crawling and access-control testing.',0),(10,'DRHL Test Event 09','08','00','AM','09','00','AM','07','09','2026','07','09','2026','07','09','2026','DRHL Test Room 09','event09@example.test','13800130009','','','Seeded DRHL test event 09 for crawling and access-control testing.',0),(11,'DRHL Test Event 10','09','30','AM','10','30','AM','07','10','2026','07','10','2026','07','10','2026','DRHL Test Room 10','event10@example.test','13800130010','','','Seeded DRHL test event 10 for crawling and access-control testing.',0),(12,'DRHL Test Event 11','10','00','AM','11','00','AM','08','11','2026','08','11','2026','08','11','2026','DRHL Test Room 11','event11@example.test','13800130011','','','Seeded DRHL test event 11 for crawling and access-control testing.',0),(13,'DRHL Test Event 12','11','30','AM','12','30','PM','08','12','2026','08','12','2026','08','12','2026','DRHL Test Room 12','event12@example.test','13800130012','','','Seeded DRHL test event 12 for crawling and access-control testing.',0),(14,'DRHL Test Event 13','12','00','PM','13','00','PM','08','13','2026','08','13','2026','08','13','2026','DRHL Test Room 13','event13@example.test','13800130013','','','Seeded DRHL test event 13 for crawling and access-control testing.',0),(15,'DRHL Test Event 14','13','30','PM','14','30','PM','08','14','2026','08','14','2026','08','14','2026','DRHL Test Room 14','event14@example.test','13800130014','','','Seeded DRHL test event 14 for crawling and access-control testing.',0),(16,'DRHL Test Event 15','14','00','PM','15','00','PM','08','15','2026','08','15','2026','08','15','2026','DRHL Test Room 15','event15@example.test','13800130015','','','Seeded DRHL test event 15 for crawling and access-control testing.',0),(17,'DRHL Test Event 16','15','30','PM','16','30','PM','08','16','2026','08','16','2026','08','16','2026','DRHL Test Room 16','event16@example.test','13800130016','','','Seeded DRHL test event 16 for crawling and access-control testing.',0),(18,'DRHL Test Event 17','16','00','PM','17','00','PM','08','17','2026','08','17','2026','08','17','2026','DRHL Test Room 17','event17@example.test','13800130017','','','Seeded DRHL test event 17 for crawling and access-control testing.',0),(19,'DRHL Test Event 18','08','30','AM','09','30','AM','08','18','2026','08','18','2026','08','18','2026','DRHL Test Room 18','event18@example.test','13800130018','','','Seeded DRHL test event 18 for crawling and access-control testing.',0),(20,'DRHL Test Event 19','09','00','AM','10','00','AM','08','19','2026','08','19','2026','08','19','2026','DRHL Test Room 19','event19@example.test','13800130019','','','Seeded DRHL test event 19 for crawling and access-control testing.',0),(21,'DRHL Test Event 20','10','30','AM','11','30','AM','08','20','2026','08','20','2026','08','20','2026','DRHL Test Room 20','event20@example.test','13800130020','','','Seeded DRHL test event 20 for crawling and access-control testing.',0);
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `no_events`
--

DROP TABLE IF EXISTS `no_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `no_events` (
  `id` int(1) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `no_events`
--

LOCK TABLES `no_events` WRITE;
/*!40000 ALTER TABLE `no_events` DISABLE KEYS */;
INSERT INTO `no_events` VALUES (1,'There are no events scheduled at this time.  Please check back later. Thank you');
/*!40000 ALTER TABLE `no_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'events_lister'
--

--
-- Dumping routines for database 'events_lister'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-06 12:58:04
