-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: wackopicko
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
-- Current Database: `wackopicko`
--

/*!40000 DROP DATABASE IF EXISTS `wackopicko`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `wackopicko` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `wackopicko`;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `password` char(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'admin','d033e22ae348aeb5660fc2140aec35850c4da997'),(2,'adamd','c533607326f2b815a7c23701be52989dac8bdbb1'),(3,'admin','d033e22ae348aeb5660fc2140aec35850c4da997'),(4,'adam','0ace61762d02afdf98f793d98c37edf696b675b2'),(5,'bob','42a9037223cdbfe0c49ef0032f0a1f3392af3fe3');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_session`
--

DROP TABLE IF EXISTS `admin_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_id` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_session`
--

LOCK TABLES `admin_session` WRITE;
/*!40000 ALTER TABLE `admin_session` DISABLE KEYS */;
INSERT INTO `admin_session` VALUES (23,1,'2025-04-14 10:34:43');
/*!40000 ALTER TABLE `admin_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart`
--

DROP TABLE IF EXISTS `cart`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=47 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart`
--

LOCK TABLES `cart` WRITE;
/*!40000 ALTER TABLE `cart` DISABLE KEYS */;
INSERT INTO `cart` VALUES (45,4,'2026-03-25 21:31:54'),(23,59,'2025-03-09 20:18:42'),(46,76,'2026-03-26 10:10:06');
/*!40000 ALTER TABLE `cart` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_coupons`
--

DROP TABLE IF EXISTS `cart_coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart_coupons` (
  `cart_id` int(11) NOT NULL,
  `coupon_id` int(11) NOT NULL,
  KEY `cart_id` (`cart_id`,`coupon_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_coupons`
--

LOCK TABLES `cart_coupons` WRITE;
/*!40000 ALTER TABLE `cart_coupons` DISABLE KEYS */;
INSERT INTO `cart_coupons` VALUES (0,0),(2,1),(2,1),(2,1),(3,1);
/*!40000 ALTER TABLE `cart_coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cart_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cart_id` int(11) NOT NULL,
  `picture_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=308 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` VALUES (73,23,22),(72,23,22),(71,23,22),(69,23,22),(307,46,24),(306,46,47),(305,46,23),(304,46,18),(303,46,21),(302,46,46),(301,46,20),(300,46,22),(299,46,19),(298,46,22),(297,46,23),(296,46,47),(295,46,24),(294,46,46),(293,46,21),(292,46,20),(291,45,20),(290,45,20),(289,45,20),(288,45,20),(287,45,20),(286,45,20),(285,45,20),(284,45,20),(283,45,20),(282,45,20),(281,45,20),(280,45,20),(279,45,20),(278,45,20);
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `text` varchar(500) NOT NULL,
  `user_id` int(11) NOT NULL,
  `picture_id` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,'blah.	      ',2,3,'2009-01-12 19:05:45'),(2,'That\\\'s an awesome butt...',2,2,'2009-01-12 19:26:21'),(3,'	      testing',2,5,'2009-01-21 15:32:44'),(4,'This is my house, what do you guys think?',2,11,'2009-02-18 14:55:39'),(12,'hhhh',4,24,'2025-04-01 17:24:25'),(11,'',0,0,'0000-00-00 00:00:00'),(10,'scanner1',4,24,'2025-04-01 15:59:17'),(13,'xixixi',4,24,'2025-04-01 17:24:56'),(14,'',0,0,'0000-00-00 00:00:00'),(15,'',0,0,'0000-00-00 00:00:00'),(16,'',0,0,'0000-00-00 00:00:00'),(17,'',0,0,'0000-00-00 00:00:00'),(18,'',0,0,'0000-00-00 00:00:00'),(19,'',0,0,'0000-00-00 00:00:00'),(20,'',0,0,'0000-00-00 00:00:00'),(21,'',0,0,'0000-00-00 00:00:00'),(22,'',76,22,'2026-03-26 10:20:41'),(23,'',0,0,'0000-00-00 00:00:00'),(24,'',76,46,'2026-03-26 10:20:41'),(25,'',0,0,'0000-00-00 00:00:00'),(26,'',0,0,'0000-00-00 00:00:00'),(27,'',0,0,'0000-00-00 00:00:00'),(28,'',0,0,'0000-00-00 00:00:00'),(29,'',0,0,'0000-00-00 00:00:00');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments_preview`
--

DROP TABLE IF EXISTS `comments_preview`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments_preview` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `text` varchar(500) NOT NULL,
  `user_id` int(11) NOT NULL,
  `picture_id` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=79 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments_preview`
--

LOCK TABLES `comments_preview` WRITE;
/*!40000 ALTER TABLE `comments_preview` DISABLE KEYS */;
INSERT INTO `comments_preview` VALUES (1,'blah.	      ',2,3,'2009-01-12 19:01:49'),(2,'blah.	      ',2,3,'2009-01-12 19:02:12'),(3,'blah.	      ',2,3,'2009-01-12 19:02:52'),(4,'blah.	      ',2,3,'2009-01-12 19:05:45'),(5,'You suck. Should I use this?	      ',2,3,'2009-01-12 19:06:43'),(62,'ESg29QWOXz',4,20,'2025-04-04 19:32:33'),(61,'C7TFtuHLG0',4,22,'2025-04-02 20:53:09'),(60,'C7TFtuHLG0',5,22,'2025-04-02 20:49:27'),(59,'EqRO2WYTul',4,19,'2025-04-02 20:21:28'),(58,'EqRO2WYTul',5,19,'2025-04-02 20:14:35'),(57,'xVYLhC0KkD',4,23,'2025-04-02 20:01:55'),(55,'tINbTv3Bfj',4,20,'2025-04-02 17:10:17'),(54,'3MKR8Pxk4L',4,19,'2025-04-02 16:58:37'),(53,'uuu',4,24,'2025-04-02 16:47:42'),(52,'xixixi',4,24,'2025-04-01 17:24:56'),(51,'hhhh',4,24,'2025-04-01 17:24:25'),(50,'scanner1',5,24,'2025-04-01 16:01:18'),(49,'scanner2',4,24,'2025-04-01 15:59:17'),(41,'xPz6ZbvQXL',4,18,'2025-04-01 15:21:56'),(46,'eee',4,24,'2025-04-01 15:41:39');
/*!40000 ALTER TABLE `comments_preview` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conflict_pictures`
--

DROP TABLE IF EXISTS `conflict_pictures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conflict_pictures` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `orig_filename` varchar(255) NOT NULL,
  `new_filename` varchar(255) NOT NULL,
  `new_tag` varchar(255) NOT NULL,
  `new_name` varchar(255) NOT NULL,
  `new_price` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conflict_pictures`
--

LOCK TABLES `conflict_pictures` WRITE;
/*!40000 ALTER TABLE `conflict_pictures` DISABLE KEYS */;
/*!40000 ALTER TABLE `conflict_pictures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coupons`
--

DROP TABLE IF EXISTS `coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) NOT NULL,
  `discount` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coupons`
--

LOCK TABLES `coupons` WRITE;
/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
INSERT INTO `coupons` VALUES (1,'SUPERYOU21',90),(2,'SUPERYOU21',90);
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guestbook`
--

DROP TABLE IF EXISTS `guestbook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guestbook` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `comment` varchar(500) NOT NULL,
  `created_on` datetime NOT NULL,
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=89 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guestbook`
--

LOCK TABLES `guestbook` WRITE;
/*!40000 ALTER TABLE `guestbook` DISABLE KEYS */;
INSERT INTO `guestbook` VALUES (32,'yUsBj3m4','iCk8Aop4qx','2025-03-07 19:51:03'),(51,'EtNzBTZF','A26tTNUglS','2025-03-31 20:25:49'),(50,'woecKYyh','fBpJSrVo78','2025-03-31 20:17:49'),(56,'R9XuLvI7','WjHoal0erX','2025-04-02 20:00:51'),(48,'tuIry18b','deRYEfPnvJ','2025-03-31 20:04:19'),(49,'b4XeAS','123','2025-03-31 20:16:11'),(55,'vSIqrNEM','28e3EicABk','2025-04-02 17:09:17'),(54,'SFPb1VZY','WH1fxeobLG','2025-04-02 16:57:54'),(75,'Sez2FyW5','WdePu4WapV','2026-03-25 20:25:02'),(74,'NyCwpxJE','fPCMHu605U','2026-03-25 20:19:00'),(73,'orUG4fmP','xl7Z9f39oU','2026-03-25 20:16:41'),(72,'MpdzyT','gcx2oQWkyK','2025-09-13 15:01:25'),(71,'cl0pno','Oif7YTsNBF','2025-09-12 21:00:46'),(70,'CR8fdS','4sWjD1iyc6','2025-09-12 20:49:18'),(69,'aWf1L3','TaX2L4fW0C','2025-09-12 20:39:33'),(68,'1PoVYfja','0nxE41vT9e','2025-04-12 14:30:09'),(76,'riZj8TUN','npuzoQedUo','2026-03-25 20:26:26'),(77,'p9qdTiCT','lwzWUJGFZj','2026-03-25 20:27:16'),(78,'Iy6X9ATB','nhehVMNPir','2026-03-25 20:32:40'),(79,'KBYYqTj8','KLARhzvLU1','2026-03-25 20:34:15'),(80,'1m1kg6Ow','LCPlm41UGy','2026-03-25 20:42:57'),(81,'TEZUARaC','pJ86z15Szf','2026-03-25 20:45:59'),(82,'T8KSjOtx','f4Ht8EvEPL','2026-03-25 20:49:14'),(83,'WHblRKVr','3xVXBVnEFe','2026-03-25 20:50:48'),(84,'GG4hPJNu','D0c70Zw6Z7','2026-03-25 21:01:55'),(85,'ZAP','Zaproxy dolore alias impedit expedita quisquam.','2026-03-26 10:02:17'),(86,'ZAP','Zaproxy dolore alias impedit expedita quisquam.','2026-03-26 10:10:05'),(87,'ZAP','Zaproxy dolore alias impedit expedita quisquam.','2026-03-26 10:20:40'),(88,'IAmpGZFv','IAmpGZ','2026-03-26 10:36:43');
/*!40000 ALTER TABLE `guestbook` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `own`
--

DROP TABLE IF EXISTS `own`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `own` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `picture_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=122 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `own`
--

LOCK TABLES `own` WRITE;
/*!40000 ALTER TABLE `own` DISABLE KEYS */;
INSERT INTO `own` VALUES (1,2,3),(2,2,2),(3,11,10),(4,4,23),(5,4,24),(55,4,24),(54,4,24),(53,4,24),(58,5,18),(63,4,23),(62,5,18),(61,5,18),(60,5,18),(59,5,18),(57,5,24),(56,4,24),(52,4,19),(64,4,19),(65,4,20),(66,5,19),(67,5,19),(68,5,19),(69,5,19),(70,4,23),(71,4,23),(72,4,23),(73,4,23),(74,5,22),(75,5,22),(76,5,22),(77,5,22),(78,4,19),(79,4,22),(80,4,20),(81,4,20),(82,4,20),(83,4,24),(84,4,22),(85,4,20),(86,4,23),(87,4,19),(88,4,21),(89,4,22),(90,4,20),(91,4,23),(92,4,19),(93,4,24),(94,4,18),(95,4,21),(96,4,20),(97,4,22),(98,4,24),(99,4,19),(100,4,18),(101,4,23),(102,4,21),(103,4,18),(104,4,23),(105,4,24),(106,4,21),(107,4,20),(108,4,19),(109,4,22),(110,4,18),(111,4,18),(112,4,18),(113,4,18),(114,5,20),(115,5,20),(116,5,20),(117,5,20),(118,5,24),(119,4,21),(120,4,21),(121,4,21);
/*!40000 ALTER TABLE `own` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pictures`
--

DROP TABLE IF EXISTS `pictures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pictures` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `width` int(11) NOT NULL,
  `height` int(11) NOT NULL,
  `tag` varchar(100) NOT NULL,
  `filename` varchar(100) NOT NULL,
  `price` int(11) NOT NULL,
  `high_quality` varchar(250) NOT NULL,
  `created_on` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=48 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pictures`
--

LOCK TABLES `pictures` WRITE;
/*!40000 ALTER TABLE `pictures` DISABLE KEYS */;
INSERT INTO `pictures` VALUES (23,'The house I share',128,128,'house','house/hodjjgld.jpg',20,'MzI0ODk4OA==','2025-02-17 10:25:23',11),(22,'Our house',128,128,'house','house/our_house.jpg',30,'ODE5Mjk0Nw==','2025-02-17 10:23:31',11),(21,'Me and the Girls',128,128,'toga','toga/togas.jpg',10,'NzczMjk4OA==','2025-02-17 10:19:46',9),(20,'The Boys - In costume',128,128,'toga','toga/togasfs.jpg',20,'MTE0MTkyMQ==','2025-02-17 10:17:50',9),(19,'My House',128,128,'house','house/My_House.jpg',15,'NDAxNjQwNA==','2025-02-17 10:15:49',2),(18,'Awesome Flower Pic',128,128,'flowers','flowers/flowers.jpg',25,'NTQ3MTg1Ng==','2025-02-17 10:13:02',2),(24,'This grows outside my house',128,128,'flowers','flowers/flweofoee.jpg',40,'NDg0MDUz','2025-02-17 10:27:00',11),(47,'N3DqKr',128,128,'NiM9mB','NiM9mB/FhGfDp',8,'NTQzNzI3Nw==','2025-09-13 15:00:21',5),(46,'hfMdTb',128,128,'QXZtvl','QXZtvl/w4LQV1',5,'Nzc2ODI2NA==','2025-09-12 20:59:10',4);
/*!40000 ALTER TABLE `pictures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(200) NOT NULL,
  `password` char(40) NOT NULL,
  `salt` char(4) NOT NULL,
  `tradebux` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  `last_login_on` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login` (`login`)
) ENGINE=MyISAM AUTO_INCREMENT=77 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Sample User','Sample','User','3e912f8fc814831804d735dc2fcbc3cfa75c28e3','NjM2',160,'2009-01-05 14:29:00','2009-02-18 14:50:00'),(2,'bob','I Am Bob','Gilbert','abd09072e674720d87ddd27122f67eedbc4b0d08','Mjkx',1066,'2009-01-05 14:51:05','2025-02-17 10:07:05'),(4,'scanner1','Scanner','1','af256af3d4fda990dbe546daa04e5c75eae356ea','ODUy',815,'2009-02-18 14:46:21','2026-09-07 16:19:20'),(5,'scanner2','Scanner','2','f9335d39b2b78018c2b8affa7fc7b0917a3300a7','MzI5',475,'2009-02-18 14:46:34','2025-09-13 15:07:10'),(6,'scanner3','Scanner','3','43754746b4043c852864bb321e4f2648d1421c18','Nzk3',1000,'2009-02-18 14:46:51','2025-03-07 09:13:53'),(7,'scanner4','Number','4','e514a672396679528c766a92a857eac4b22bc667','NjEx',100,'2009-02-18 14:47:04','2009-02-18 14:47:04'),(8,'scanner5','Number','5','f38ae9b0b6b1ad2a2a2721841c0cc89b31e044cb','NTQw',100,'2009-02-18 14:47:18','2009-02-18 14:47:18'),(9,'wanda','Wanda','Granat','4e4465300b14b314384a6375a837f0532822d3c8','Nzcz',480,'2009-02-18 14:53:23','2025-02-17 10:16:25'),(10,'calvinwatters','Calvin','Watters','81418ed6e9bd15076d2f43e17b9f5a27c7e55ef7','Nzc5',100,'2009-02-18 14:56:11','2009-02-18 14:56:11'),(11,'bryce','Bryce','Boe','478fb0b83851b3d16ffc5a2554a4d616f1235156','NjY3',1334,'2009-02-18 14:57:36','2025-02-17 10:21:25'),(76,'ZAP','ZAP','ZAP','fe9ae981f45ff18fe704f002eafd77a8f9e8278f','NDI1',100,'2026-03-26 10:02:17','2026-03-26 10:20:40'),(75,'fRheN6Na','aa8zwu6V','EuMHLHRX','e72cf398e0f5bc5155733745f675cc5448604bff','NDY=',100,'2026-03-25 20:34:26','2026-03-25 20:34:26'),(74,'FfajikNR','COIm3vKq','yVLNvq43','cd74f246f176e8624da773926c7b5e63e31ff420','NTM3',100,'2026-03-25 20:34:20','2026-03-25 20:34:20'),(73,'4qSfHi','FOgCbW','B7h4Wa','1dd543ba8d9e4be9b88a6d4822d7f48b62b10fed','Mjc5',100,'2025-09-12 20:40:04','2025-09-12 20:40:04'),(72,'KFVovAGn','j6blx9HM','ynYE1UaG','d79c30d6892fb7b3028658f0b136acf5c03b8928','NjU3',100,'2025-04-12 14:31:33','2025-04-12 14:31:33'),(71,'ClEiyTDt','KM4beStG','OklHoQtR','c0379a656d1c8fd89c912867744f597778cbda04','NDY2',100,'2025-04-12 14:31:23','2025-04-12 14:31:23'),(70,'Uh1CxR2j','tTn5A9NL','K3fkrgot','20af7d7e430c064525edbf84b1bec480412af8f1','NjA4',100,'2025-04-04 19:33:19','2025-04-04 19:33:19');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'wackopicko'
--

--
-- Dumping routines for database 'wackopicko'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-07 16:47:46
