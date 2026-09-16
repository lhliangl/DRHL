-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: forum
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
-- Current Database: `forum`
--

/*!40000 DROP DATABASE IF EXISTS `forum`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `forum` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `forum`;

--
-- Table structure for table `forum_forums`
--

DROP TABLE IF EXISTS `forum_forums`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_forums` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `forum_id` int(10) NOT NULL,
  `title` text NOT NULL,
  `forum_info` text NOT NULL,
  PRIMARY KEY (`id`,`forum_id`)
) ENGINE=MyISAM AUTO_INCREMENT=180 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_forums`
--

LOCK TABLES `forum_forums` WRITE;
/*!40000 ALTER TABLE `forum_forums` DISABLE KEYS */;
INSERT INTO `forum_forums` VALUES (164,22,'aZnEqJ7P','sGjP1u7lqh'),(176,34,'LR6wLA3B','uIFumH9mUH'),(162,20,'PNoBKI0L','B8H8rDUnlz'),(161,19,'osIjoc7u','miyPYurC30'),(160,18,'MRBIBsva','QAiHE4C4m8'),(159,17,'J89usBt7','vT8ZdNIhgJ'),(155,13,'QS6bJ32c','D2Fi60lyH9'),(158,16,'dyOSsTOa','Xl0pXih5K7'),(152,12,'Kgv483f4','GA9mXMb2w8'),(145,7,'QEz0vyYV','THqDkCEBZR'),(141,3,'Of0oL52N','b2mPNn2TfV'),(157,15,'l7Lvfo6e','P0TcPpEYdM'),(156,14,'wavjEqW6','HT7OkQwRXm'),(175,33,'WHhVzpLP','uu9t8hukyE'),(165,23,'vvcSWtbc','9fEdFFQtb6'),(177,35,'NBNaWKs7','4XTuHVKzYS'),(167,25,'lmnSUFTm','qG7TyMKceS'),(168,26,'h12FTecd','PXV7xS7QaZ'),(169,27,'CaZ3HetA','pxqmQ1SDry'),(170,28,'8e6HoJ5r','r59oTwWyd7'),(171,29,'CK8tq6id','Z2f0CobU8k'),(174,32,'BCgz6TY3','sw3JlDWL3b'),(173,31,'9Y5FaaPW','Z5B0Vndcuq'),(178,36,'ZAP','');
/*!40000 ALTER TABLE `forum_forums` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_message`
--

DROP TABLE IF EXISTS `forum_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_message` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `forum_id` int(10) NOT NULL,
  `thread_id` int(10) NOT NULL,
  `reply_id` int(10) NOT NULL,
  `message` text NOT NULL,
  `user` text NOT NULL,
  `date_time` datetime NOT NULL,
  PRIMARY KEY (`id`,`forum_id`,`thread_id`,`reply_id`)
) ENGINE=MyISAM AUTO_INCREMENT=468 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_message`
--

LOCK TABLES `forum_message` WRITE;
/*!40000 ALTER TABLE `forum_message` DISABLE KEYS */;
INSERT INTO `forum_message` VALUES (464,7,57,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(465,7,58,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(466,28,59,0,'aaa','admin','2026-03-27 17:57:04'),(467,28,59,0,'aaa','user1','2026-03-27 17:57:32'),(463,7,56,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(344,7,8,2,'CT997j71oiysOZCkDN8sS9GvVD6mNa8M1TNkhqNhcKYHPgstX9h7aGQDCguLdD7SgvaNJETG0T2Arwiw<!-- begin --!><BR><BR><I>Edited by admin - Fri Mar 27 17:00:21 CST 2026 (48%)</I><!-- end --!>','admin','2026-03-27 16:59:36'),(345,7,11,0,'9JILzgD53W','admin','2026-03-27 16:59:38'),(346,7,12,0,'g0j31sUmeh','admin','2026-03-27 16:59:40'),(347,7,8,3,'syVcW0enh3','admin','2026-03-27 16:59:41'),(348,7,13,0,'rRHWh52C6W','admin','2026-03-27 16:59:42'),(349,7,14,0,'hxU3ZBJqb7','admin','2026-03-27 16:59:45'),(350,7,8,4,'xxvq4jAjNq','admin','2026-03-27 16:59:47'),(351,7,15,0,'5Qmn3kBRth','admin','2026-03-27 16:59:48'),(352,7,16,0,'m2CEoYT49z','admin','2026-03-27 16:59:51'),(353,7,8,5,'ZaPJcVHcTs','admin','2026-03-27 16:59:53'),(354,7,17,0,'yRLKhHXogH','admin','2026-03-27 16:59:54'),(355,7,18,0,'41UVcSIzzP','admin','2026-03-27 16:59:57'),(356,7,8,6,'G8hRBCoqOrgO6uUGgKvpelgC4sqXAF5RIniZamKv<!-- begin --!><BR><BR><I>Edited by admin - Fri Mar 27 17:00:46 CST 2026 (32%)</I><!-- end --!>','admin','2026-03-27 16:59:59'),(357,7,19,0,'yZfZQSGvIF','admin','2026-03-27 17:00:01'),(358,7,20,0,'hcHKMwWqIO','admin','2026-03-27 17:00:04'),(359,7,8,7,'xGRfswxvoy','admin','2026-03-27 17:00:06'),(360,7,21,0,'TjmHl5GuTQ','admin','2026-03-27 17:00:07'),(361,7,22,0,'rh7xljWDv9','admin','2026-03-27 17:00:09'),(362,7,8,8,'SvKMod3OqH','admin','2026-03-27 17:00:11'),(363,7,23,0,'noLWSx87BP','admin','2026-03-27 17:00:12'),(364,7,24,0,'SsyVh3QQOu','admin','2026-03-27 17:00:15'),(365,7,8,9,'HOYV5TLfDF','admin','2026-03-27 17:00:16'),(366,7,25,0,'PBTrVHe9sw','admin','2026-03-27 17:00:18'),(367,7,26,0,'tYLjsZqNyN','admin','2026-03-27 17:00:20'),(368,7,8,10,'GAZjpLi3Cv','admin','2026-03-27 17:00:22'),(369,7,27,0,'b018sA2fCQ','admin','2026-03-27 17:00:23'),(370,7,28,0,'chleam4uMz','admin','2026-03-27 17:00:26'),(371,7,8,10,'kjb3JeeElK','admin','2026-03-27 17:00:28'),(372,7,8,10,'FYJzh3HTRj','admin','2026-03-27 17:00:29'),(373,7,29,0,'ZsNn9gtvwz','admin','2026-03-27 17:00:31'),(374,7,30,0,'Mroqz0vuAX','admin','2026-03-27 17:00:36'),(375,7,8,10,'r9UvFQFGTl','admin','2026-03-27 17:00:38'),(376,7,8,10,'U2S04mD6i6','admin','2026-03-27 17:00:39'),(377,7,31,0,'H1W4JsyBkP','admin','2026-03-27 17:00:41'),(378,7,32,0,'0nIn0k8kMF','admin','2026-03-27 17:00:45'),(379,7,8,10,'RK9BswlQts','admin','2026-03-27 17:00:48'),(380,7,8,10,'BrDUQzmQVV','admin','2026-03-27 17:00:48'),(381,7,33,0,'CPZKEefxKp','admin','2026-03-27 17:00:50'),(382,7,34,0,'wkNLVfBBQW','admin','2026-03-27 17:00:53'),(386,19,37,0,'3cowomoPnR','admin','2026-03-27 17:11:19'),(385,19,36,0,'7HKv3Ri5qO','admin','2026-03-27 17:11:16'),(393,31,42,0,'ybhx3QFMsV','admin','2026-03-27 17:18:06'),(390,13,40,0,'yphZes1lbh','admin','2026-03-27 17:12:00'),(462,7,55,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(389,13,39,0,'HIOie3eSu7','admin','2026-03-27 17:11:56'),(394,31,43,0,'cHctqnrLJQ','admin','2026-03-27 17:18:09'),(398,15,46,0,'8KvTGXzdWA','admin','2026-03-27 17:23:24'),(399,27,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(397,15,45,0,'TGA4rNTOq7','admin','2026-03-27 17:23:20'),(400,33,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(401,35,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(402,3,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(403,20,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(404,16,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(405,22,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(406,23,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(407,18,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(408,12,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(409,26,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(410,34,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(411,14,47,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(412,15,48,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(413,31,48,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(414,19,48,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(415,13,49,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:05'),(416,31,43,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(417,15,46,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(418,15,45,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(419,19,36,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(420,19,37,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(421,31,42,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(422,13,40,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(423,13,39,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(424,15,50,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(425,31,50,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(426,19,50,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(427,13,50,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(428,19,48,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(429,13,49,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(430,7,51,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(431,7,28,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(432,7,32,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(433,7,34,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(434,7,19,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(435,7,16,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(436,7,17,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(437,7,29,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(438,7,22,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(439,7,15,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(440,7,14,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(441,7,25,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(442,7,24,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(443,7,33,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(444,7,13,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(445,7,23,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(446,7,12,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(447,7,11,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(448,7,20,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(449,7,9,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(450,7,8,11,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(451,7,21,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(452,7,10,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(453,7,27,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(454,7,18,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(455,7,26,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(456,7,31,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(457,7,30,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:06'),(458,7,52,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(459,7,53,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(460,7,51,1,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(461,7,54,0,'Zaproxy alias impedit expedita quisquam pariatur exercitationem. Nemo rerum eveniet dolores rem quia dignissimos.','ZAP','2026-03-27 17:39:09'),(343,7,10,0,'1Tfu4QSYGf','admin','2026-03-27 16:59:35'),(342,7,8,1,'ry1PVDu4Co','admin','2026-03-27 16:59:32'),(341,7,9,0,'QRZPz847iv','admin','2026-03-27 16:59:31'),(340,7,8,0,'mUJOjpFDhuUFkFPa8H7DEOwUtaB2dL<!-- begin --!><BR><BR><I>Edited by admin - Fri Mar 27 16:59:40 CST 2026 (25%)</I><!-- end --!>','admin','2026-03-27 16:59:29');
/*!40000 ALTER TABLE `forum_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_settings`
--

DROP TABLE IF EXISTS `forum_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_settings` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `dbName` text NOT NULL,
  `dbLogin` text NOT NULL,
  `dbPassword` text NOT NULL,
  `forumPath` text NOT NULL,
  `forumName` text NOT NULL,
  `messagePerPage` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_settings`
--

LOCK TABLES `forum_settings` WRITE;
/*!40000 ALTER TABLE `forum_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `forum_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_threads`
--

DROP TABLE IF EXISTS `forum_threads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_threads` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `forum_id` int(10) NOT NULL,
  `thread_id` int(10) NOT NULL,
  `title` text NOT NULL,
  `views` int(10) NOT NULL,
  PRIMARY KEY (`id`,`forum_id`,`thread_id`)
) ENGINE=MyISAM AUTO_INCREMENT=265 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_threads`
--

LOCK TABLES `forum_threads` WRITE;
/*!40000 ALTER TABLE `forum_threads` DISABLE KEYS */;
INSERT INTO `forum_threads` VALUES (204,7,21,'mMCEuKfq',1),(203,7,20,'EBwQaDB1',1),(202,7,19,'mA1mr8Wm',1),(200,7,17,'kRin4uBW',1),(201,7,18,'6c2QY5Yu',1),(213,7,30,'C8BmgB5M',1),(212,7,29,'y3FCP3zm',1),(211,7,28,'RyhYg08q',1),(210,7,27,'yPjDBko3',1),(209,7,26,'0lPI5Yn2',1),(208,7,25,'3kgZHppP',1),(195,7,12,'glGTWh2J',1),(196,7,13,'fCYmxPse',1),(197,7,14,'F0G5ifnn',1),(198,7,15,'emQ38BMv',1),(199,7,16,'vPv1Was6',1),(194,7,11,'SeAbPC2Y',1),(193,7,10,'c1bz5nJO',1),(192,7,9,'IvKsiLfb',1),(191,7,8,'bBKgBE5Z',79),(190,8,7,'sad',0),(189,5,6,'awd',0),(188,0,5,'jk',2),(187,0,4,'rjnsxdfr',0),(186,0,3,'vbn',0),(184,1,1,'123',0),(185,1,2,'kuftyj',2),(207,7,24,'XgTr2wvR',1),(183,1,0,'dhrf',0),(214,7,31,'sDTlPTL3',1),(205,7,22,'PisDtieq',1),(206,7,23,'4cIScNKH',1),(215,7,32,'8Kp8tQSU',1),(216,7,33,'b4FRxMvG',1),(217,7,34,'eRrTiIu9',1),(220,19,37,'WcwQtLxJ',1),(219,19,36,'ELf8h3nd',1),(223,13,40,'3nD8HnF2',1),(222,13,39,'MCYTY3Rt',1),(226,31,43,'MGS1NJOy',1),(225,31,42,'VhN9hUci',1),(229,15,46,'JifjCneJ',1),(228,15,45,'AkFoL2Se',1),(230,27,47,'ZAP',0),(231,33,47,'ZAP',0),(232,32,47,'ZAP',0),(233,35,47,'ZAP',0),(234,3,47,'ZAP',0),(235,20,47,'ZAP',0),(236,17,47,'ZAP',0),(237,16,47,'ZAP',0),(238,12,47,'ZAP',0),(239,25,47,'ZAP',0),(240,29,47,'ZAP',0),(241,22,47,'ZAP',0),(242,23,47,'ZAP',0),(243,18,47,'ZAP',0),(244,26,47,'ZAP',0),(245,14,47,'ZAP',0),(246,34,47,'ZAP',0),(247,15,48,'ZAP',1),(248,31,48,'ZAP',1),(249,19,48,'ZAP',1),(250,13,49,'ZAP',1),(251,15,50,'ZAP',0),(252,31,50,'ZAP',0),(253,19,50,'ZAP',0),(254,13,50,'ZAP',0),(255,7,51,'ZAP',1),(256,7,52,'ZAP',0),(257,7,53,'ZAP',0),(258,7,54,'ZAP',0),(259,7,55,'ZAP',0),(260,7,56,'ZAP',0),(261,7,57,'ZAP',0),(262,7,58,'ZAP',0),(263,28,59,'ww',2),(264,28,59,'ww',2);
/*!40000 ALTER TABLE `forum_threads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_users`
--

DROP TABLE IF EXISTS `forum_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `forum_users` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `user_name` text NOT NULL,
  `password` text NOT NULL,
  `email` text NOT NULL,
  `registerdate` datetime NOT NULL,
  `TYPE` text NOT NULL,
  `avatar` text NOT NULL,
  `member_title` text NOT NULL,
  `signature` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=97 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_users`
--

LOCK TABLES `forum_users` WRITE;
/*!40000 ALTER TABLE `forum_users` DISABLE KEYS */;
INSERT INTO `forum_users` VALUES (1,'user1','*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9','user1@qq.com','2025-03-17 10:23:57','user','./avatars/avatar_34.jpg','New Member','hahaTxqVM7wyeQR6AcOpemqUWgU8pa61VfSpBWtQeOMN'),(2,'user2','*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9','user2@qq.com','2025-03-17 14:44:12','user','./avatars/avatar_4.jpg','New Member','hhhX5KnDgeBNIi3ZHXpT1uv'),(3,'admin','*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9','admin@qq.com','2025-03-17 14:46:04','Admin','./avatars/avatar_53.jpg','Admin','Admin4yJR0xsAgpRDEvSKzJcO'),(59,'nNru2yGS','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','5073941286@qq.com','2025-05-14 21:55:35','user','default_avatar.png','New Member',''),(60,'Vmgd34Gf','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','3082194567@qq.com','2025-05-14 21:55:38','user','default_avatar.png','New Member',''),(61,'bX3OQpZC','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','8075421693@qq.com','2025-05-14 21:56:48','user','default_avatar.png','New Member',''),(62,'tMrTcSOd','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','6253870419@qq.com','2025-05-14 21:56:52','user','default_avatar.png','New Member',''),(57,'RGlcD8dH','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','7016528943@qq.com','2025-04-12 17:56:54','user','default_avatar.png','New Member',''),(58,'h9bDeW5n','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','5460273918@qq.com','2025-05-14 21:55:31','user','default_avatar.png','New Member',''),(53,'wY7zrUT6','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','5321680479@qq.com','2025-04-12 17:49:31','user','default_avatar.png','New Member',''),(54,'ATSvxRMi','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','1564829037@qq.com','2025-04-12 17:49:34','user','default_avatar.png','New Member',''),(55,'CFIbEJTq','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','1620497385@qq.com','2025-04-12 17:56:48','user','default_avatar.png','New Member',''),(56,'YtEf2a8z','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','2619053874@qq.com','2025-04-12 17:56:51','user','default_avatar.png','New Member',''),(52,'vrqwJnob','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','4957862310@qq.com','2025-04-12 17:49:27','user','default_avatar.png','New Member',''),(63,'lHJgQLhp','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','7236480591@qq.com','2025-05-14 21:56:55','user','default_avatar.png','New Member',''),(51,'7SxGWf8j','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','4R9rSJPp','2025-04-10 21:31:14','user','default_avatar.png','New Member',''),(50,'dtaYjzWm','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','TKLnrXsF','2025-04-10 21:31:11','user','default_avatar.png','New Member',''),(49,'ksgF0r6V','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','ZdVrc2Sg','2025-04-10 21:31:08','user','default_avatar.png','New Member',''),(64,'Bd0ix1xF','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','YZJBg0jh@qq.com','2026-03-27 16:14:27','user','default_avatar.png','New Member',''),(65,'E5uYSuXA','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','CS9OVpBD@qq.com','2026-03-27 16:14:28','user','default_avatar.png','New Member',''),(66,'eA0ypDk3','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','1TE4tf93@qq.com','2026-03-27 16:15:16','user','default_avatar.png','New Member',''),(67,'OqU2BeFX','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','5z6PUNJB@qq.com','2026-03-27 16:15:32','user','default_avatar.png','New Member',''),(68,'0L49srlx','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','x7EictR1@qq.com','2026-03-27 16:15:50','user','default_avatar.png','New Member',''),(69,'fsMg5czl','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','ihArY2Qu@qq.com','2026-03-27 16:15:51','user','default_avatar.png','New Member',''),(70,'0MAmBF0n','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','S7IrMrRn@qq.com','2026-03-27 16:15:53','user','default_avatar.png','New Member',''),(71,'tQi2eceu','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','GK5Igl1X@qq.com','2026-03-27 16:17:20','user','default_avatar.png','New Member',''),(72,'O2DrDjAx','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','GTY1MGpK@qq.com','2026-03-27 16:17:20','user','default_avatar.png','New Member',''),(73,'UZmriSIF','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','96t6lYCM@qq.com','2026-03-27 16:17:23','user','default_avatar.png','New Member',''),(74,'un8p2pOZ','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','HTDDaXJ2@qq.com','2026-03-27 16:20:18','user','default_avatar.png','New Member',''),(75,'h0bp0jgl','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','hsXkdnmf@qq.com','2026-03-27 16:20:32','user','default_avatar.png','New Member',''),(76,'nzOgA1Gj','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','8XFjkO4w@qq.com','2026-03-27 16:34:47','user','default_avatar.png','New Member',''),(77,'HqvMci7O','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','4ipaYVkS@qq.com','2026-03-27 16:34:48','user','default_avatar.png','New Member',''),(78,'u3D7IvbM','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','OJLaONxA@qq.com','2026-03-27 16:34:50','user','default_avatar.png','New Member',''),(79,'sEDek8WD','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','LHxBGlv7@qq.com','2026-03-27 16:35:15','user','default_avatar.png','New Member',''),(80,'JcG0N2uh','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','0taBvjtV@qq.com','2026-03-27 16:35:15','user','default_avatar.png','New Member',''),(81,'5IjwsYlz','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','kcAdoc4T@qq.com','2026-03-27 16:35:17','user','default_avatar.png','New Member',''),(82,'8actzW0M','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','cf0qLeV2@qq.com','2026-03-27 16:41:30','user','default_avatar.png','New Member',''),(83,'rZk4XH1W','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','tD0H3HxV@qq.com','2026-03-27 16:41:39','user','default_avatar.png','New Member',''),(84,'d7gGUoH7','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','UighCg8F@qq.com','2026-03-27 16:41:50','user','default_avatar.png','New Member',''),(85,'C81TsVBo','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','o3gGGRna@qq.com','2026-03-27 16:42:04','user','default_avatar.png','New Member',''),(86,'YCYWNPT2','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','cKzqJWZE@qq.com','2026-03-27 16:42:05','user','default_avatar.png','New Member',''),(87,'9tCXUiM7','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','vB1m08FE@qq.com','2026-03-27 16:42:07','user','default_avatar.png','New Member',''),(88,'Il4hXeYP','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','FbBhRKVD@qq.com','2026-03-27 16:45:25','user','default_avatar.png','New Member',''),(89,'CGcImZ5p','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','49s00jCU@qq.com','2026-03-27 16:45:25','user','default_avatar.png','New Member',''),(90,'jstNawp9','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','5YFG7cjf@qq.com','2026-03-27 16:45:27','user','default_avatar.png','New Member',''),(91,'mG3GPo2P','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','ArkT7X9F@qq.com','2026-03-27 16:56:14','user','default_avatar.png','New Member',''),(92,'BNukPkzU','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','D3OBbvsL@qq.com','2026-03-27 16:56:15','user','default_avatar.png','New Member',''),(93,'XJYDwb9x','*84AAC12F54AB666ECFC2A83C676908C8BBC381B1','H36J8lHU@qq.com','2026-03-27 16:56:17','user','default_avatar.png','New Member',''),(94,'ZAP','*DFB1B769F4A7C9A698214225F28C7A22093625C6','zaproxy@example.com','2026-03-27 17:37:12','user','default_avatar.png','New Member','');
/*!40000 ALTER TABLE `forum_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'forum'
--

--
-- Dumping routines for database 'forum'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-06 17:13:35
