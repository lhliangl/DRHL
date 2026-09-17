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
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_forums`
--

LOCK TABLES `forum_forums` WRITE;
/*!40000 ALTER TABLE `forum_forums` DISABLE KEYS */;
INSERT INTO `forum_forums` VALUES (1,0,'General Discussion','Stable baseline forum for normal browsing and DRHL access-control tests.'),(2,1,'Testing Area','Secondary forum used to keep navigation and multi-forum behavior available.');
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
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_message`
--

LOCK TABLES `forum_message` WRITE;
/*!40000 ALTER TABLE `forum_message` DISABLE KEYS */;
INSERT INTO `forum_message` VALUES (1,0,0,0,'DRHL_JSFORUM_ADMIN_TOPIC_BASELINE','admin','2026-09-10 10:00:00'),(2,0,0,1,'DRHL_JSFORUM_USER1_REPLY_P1','user1','2026-09-10 10:01:00'),(3,0,0,2,'DRHL_JSFORUM_USER2_REPLY_P2','user2','2026-09-10 10:02:00'),(4,0,0,3,'DRHL_JSFORUM_ADMIN_REPLY_P3','admin','2026-09-10 10:03:00'),(5,0,1,0,'DRHL_JSFORUM_USER1_SECOND_TOPIC','user1','2026-09-10 10:04:00'),(6,0,1,1,'DRHL_JSFORUM_USER2_SECOND_REPLY','user2','2026-09-10 10:05:00'),(7,1,2,0,'DRHL_JSFORUM_USER2_FEATURE_TOPIC','user2','2026-09-10 10:06:00'),(8,1,2,1,'DRHL_JSFORUM_USER1_FEATURE_REPLY','user1','2026-09-10 10:07:00');
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
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_settings`
--

LOCK TABLES `forum_settings` WRITE;
/*!40000 ALTER TABLE `forum_settings` DISABLE KEYS */;
INSERT INTO `forum_settings` VALUES (1,'forum','root','root','../forum/','My Forum','10');
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
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_threads`
--

LOCK TABLES `forum_threads` WRITE;
/*!40000 ALTER TABLE `forum_threads` DISABLE KEYS */;
INSERT INTO `forum_threads` VALUES (1,0,0,'Welcome to JsForum',0),(2,0,1,'Access Control Test Thread',2),(3,1,2,'Feature Discussion',0);
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
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_users`
--

LOCK TABLES `forum_users` WRITE;
/*!40000 ALTER TABLE `forum_users` DISABLE KEYS */;
INSERT INTO `forum_users` VALUES (1,'user1','*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9','user1@qq.com','2025-03-17 10:23:57','user','./avatars/avatar_34.jpg','New Member','hahaTxqVM7wyeQR6AcOpemqUWgU8pa61VfSpBWtQeOMN'),(2,'user2','*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9','user2@qq.com','2025-03-17 14:44:12','user','./avatars/avatar_4.jpg','New Member','hhhX5KnDgeBNIi3ZHXpT1uv'),(3,'admin','*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9','admin@qq.com','2025-03-17 14:46:04','Admin','./avatars/avatar_53.jpg','Admin','Admin4yJR0xsAgpRDEvSKzJcO');
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

-- Dump completed on 2026-09-10 10:53:17
