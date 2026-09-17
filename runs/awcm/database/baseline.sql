-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: awcm
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
-- Current Database: `awcm`
--

/*!40000 DROP DATABASE IF EXISTS `awcm`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `awcm` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `awcm`;

--
-- Table structure for table `awcm_blocks`
--

DROP TABLE IF EXISTS `awcm_blocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_blocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `file` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `position` int(11) NOT NULL,
  `tarteeb` int(11) NOT NULL,
  `page` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_blocks`
--

LOCK TABLES `awcm_blocks` WRITE;
/*!40000 ALTER TABLE `awcm_blocks` DISABLE KEYS */;
INSERT INTO `awcm_blocks` VALUES (1,'latest topics','','ltst_topics_1_colum_center.php',3,0,'index'),(2,'latest videos','','ltst_videos_filmstrip.php',3,5,'index'),(3,'Aljazeera News','','aljazeera_marquee.php',5,3,'news'),(4,'latest images','','latest_images_fade.php',1,0,'index'),(5,'online','','online.php',1,0,'index'),(6,'latest images','','latest_images_fade.php',2,1,'album'),(7,'latest images','','ltst_imgs_ajax_slider.php',3,0,'album'),(8,'search','','center_search.php',3,9,'index'),(9,'latest programs','','latest_pro_side.php',1,0,'index'),(10,'latest lessons','','latest_lessons_side.php',2,1,'all'),(11,'members area','','login.php',2,9,'all'),(12,'fast statics','','stats.php',2,1,'all'),(13,'fast search','','small_search.php',2,1,'all'),(14,'place','','place.php',3,10,'all'),(15,'site categories','\n<a href=index.php>index</a><br />\n<a href=topics.php>topics</a><br />\n<a href=lessons.php>lessons</a><br />\n<a href=programs.php>programs</a><br />\n<a href=sounds.php>sounds</a><br />\n<a href=video_lib.php>videos</a><br />\n<a href=album.php>images</a><br />\n<a href=flash_lib.php>flashs</a><br />\n<a href=news.php>news</a><br />\n<a href=weblinks.php>weblinks</a><br />\n<a href=contactus.php>contactus</a><br />\n<a href=search.php>search</a>\n','no',2,99,'all');
/*!40000 ALTER TABLE `awcm_blocks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_categories`
--

DROP TABLE IF EXISTS `awcm_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_categories` (
  `topics` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `lessons` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `programs` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `sounds` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `videos` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `images` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `flash` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `weblinks` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `news` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_categories`
--

LOCK TABLES `awcm_categories` WRITE;
/*!40000 ALTER TABLE `awcm_categories` DISABLE KEYS */;
INSERT INTO `awcm_categories` VALUES ('yes','yes','yes','yes','yes','yes','yes','yes','yes');
/*!40000 ALTER TABLE `awcm_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_control`
--

DROP TABLE IF EXISTS `awcm_control`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_control` (
  `notes` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_control`
--

LOCK TABLES `awcm_control` WRITE;
/*!40000 ALTER TABLE `awcm_control` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_control` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_flashs_cat`
--

DROP TABLE IF EXISTS `awcm_flashs_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_flashs_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `icon` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_flashs_cat`
--

LOCK TABLES `awcm_flashs_cat` WRITE;
/*!40000 ALTER TABLE `awcm_flashs_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_flashs_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_flashs_flashs`
--

DROP TABLE IF EXISTS `awcm_flashs_flashs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_flashs_flashs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `views` int(11) NOT NULL,
  `rate` int(11) NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_flashs_flashs`
--

LOCK TABLES `awcm_flashs_flashs` WRITE;
/*!40000 ALTER TABLE `awcm_flashs_flashs` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_flashs_flashs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_flashs_settings`
--

DROP TABLE IF EXISTS `awcm_flashs_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_flashs_settings` (
  `flshs_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `send_flash` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_flashs_settings`
--

LOCK TABLES `awcm_flashs_settings` WRITE;
/*!40000 ALTER TABLE `awcm_flashs_settings` DISABLE KEYS */;
INSERT INTO `awcm_flashs_settings` VALUES ('20','yes');
/*!40000 ALTER TABLE `awcm_flashs_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_images_cat`
--

DROP TABLE IF EXISTS `awcm_images_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_images_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_images_cat`
--

LOCK TABLES `awcm_images_cat` WRITE;
/*!40000 ALTER TABLE `awcm_images_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_images_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_images_images`
--

DROP TABLE IF EXISTS `awcm_images_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_images_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` int(11) NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `views` int(11) NOT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `thumb` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `rate` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_images_images`
--

LOCK TABLES `awcm_images_images` WRITE;
/*!40000 ALTER TABLE `awcm_images_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_images_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_images_settings`
--

DROP TABLE IF EXISTS `awcm_images_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_images_settings` (
  `imgs_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `send_image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `ltst_imgs` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_images_settings`
--

LOCK TABLES `awcm_images_settings` WRITE;
/*!40000 ALTER TABLE `awcm_images_settings` DISABLE KEYS */;
INSERT INTO `awcm_images_settings` VALUES ('25','yes','yes');
/*!40000 ALTER TABLE `awcm_images_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_languages`
--

DROP TABLE IF EXISTS `awcm_languages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_languages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `file` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_languages`
--

LOCK TABLES `awcm_languages` WRITE;
/*!40000 ALTER TABLE `awcm_languages` DISABLE KEYS */;
INSERT INTO `awcm_languages` VALUES (1,'English','en.php'),(2,'Ø¹Ø±Ø¨ÙŠ','ar.php');
/*!40000 ALTER TABLE `awcm_languages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_lessons_cat`
--

DROP TABLE IF EXISTS `awcm_lessons_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_lessons_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `details` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `icon` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_lessons_cat`
--

LOCK TABLES `awcm_lessons_cat` WRITE;
/*!40000 ALTER TABLE `awcm_lessons_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_lessons_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_lessons_coments`
--

DROP TABLE IF EXISTS `awcm_lessons_coments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_lessons_coments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lesson` int(11) NOT NULL,
  `author` int(11) NOT NULL,
  `coment` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_lessons_coments`
--

LOCK TABLES `awcm_lessons_coments` WRITE;
/*!40000 ALTER TABLE `awcm_lessons_coments` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_lessons_coments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_lessons_lessons`
--

DROP TABLE IF EXISTS `awcm_lessons_lessons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_lessons_lessons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` int(11) NOT NULL,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `short_desc` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `views` int(11) DEFAULT NULL,
  `rate` int(11) DEFAULT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `allow_coments` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_lessons_lessons`
--

LOCK TABLES `awcm_lessons_lessons` WRITE;
/*!40000 ALTER TABLE `awcm_lessons_lessons` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_lessons_lessons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_lessons_settings`
--

DROP TABLE IF EXISTS `awcm_lessons_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_lessons_settings` (
  `fast_stats` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `send_lesson` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `lessons_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `show_sig` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `block_les_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_lessons_settings`
--

LOCK TABLES `awcm_lessons_settings` WRITE;
/*!40000 ALTER TABLE `awcm_lessons_settings` DISABLE KEYS */;
INSERT INTO `awcm_lessons_settings` VALUES ('yes','yes','15','yes','yes');
/*!40000 ALTER TABLE `awcm_lessons_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_maininfo`
--

DROP TABLE IF EXISTS `awcm_maininfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_maininfo` (
  `sitename` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `address` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `defult_theme` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `defult_language` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `copyrights` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `keywords` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `rules` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `ajax` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `members_on` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `coments_guests` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `admin_email` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `favicon` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `close_yn` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `close_msg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `closergstr_yn` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `closergstr_msg` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date_type` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `version` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `site_create_date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_maininfo`
--

LOCK TABLES `awcm_maininfo` WRITE;
/*!40000 ALTER TABLE `awcm_maininfo` DISABLE KEYS */;
INSERT INTO `awcm_maininfo` VALUES ('awcm','http://localhost/awcm//','awcm_darkblue','en.php',NULL,'',NULL,'on','on','yes','admin@qq.com','','no','','no','','hijri','2.1','');
/*!40000 ALTER TABLE `awcm_maininfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_member_pms`
--

DROP TABLE IF EXISTS `awcm_member_pms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_member_pms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `reciever` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `subject` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `msg` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `hash` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_member_pms`
--

LOCK TABLES `awcm_member_pms` WRITE;
/*!40000 ALTER TABLE `awcm_member_pms` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_member_pms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_members`
--

DROP TABLE IF EXISTS `awcm_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_members` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `password` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `email` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `sex` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `country` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `avatar` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `signature` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `level` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `autoactivate` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `notes` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_members`
--

LOCK TABLES `awcm_members` WRITE;
/*!40000 ALTER TABLE `awcm_members` DISABLE KEYS */;
INSERT INTO `awcm_members` VALUES (1,'admin','e10adc3949ba59abbe56e057f20f883e','admin@qq.com','','','','','admin','<span style=background:red;border:black solid 1px;>Administrator</span>','yes',''),(2,'user1','e10adc3949ba59abbe56e057f20f883e','user1@qq.com','male','qwe','','','member','','no',''),(3,'user2','e10adc3949ba59abbe56e057f20f883e','user2@qq.com','male','qwe','','','member','','no','');
/*!40000 ALTER TABLE `awcm_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_msgs`
--

DROP TABLE IF EXISTS `awcm_msgs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_msgs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_msgs`
--

LOCK TABLES `awcm_msgs` WRITE;
/*!40000 ALTER TABLE `awcm_msgs` DISABLE KEYS */;
INSERT INTO `awcm_msgs` VALUES (25,'Congratulations','<center><h2>AWCM v2.1 has been installed succesfully','15/07/2009');
/*!40000 ALTER TABLE `awcm_msgs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_news_cat`
--

DROP TABLE IF EXISTS `awcm_news_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_news_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `details` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_news_cat`
--

LOCK TABLES `awcm_news_cat` WRITE;
/*!40000 ALTER TABLE `awcm_news_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_news_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_news_coments`
--

DROP TABLE IF EXISTS `awcm_news_coments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_news_coments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `news` int(11) NOT NULL,
  `author` int(11) NOT NULL,
  `coment` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_news_coments`
--

LOCK TABLES `awcm_news_coments` WRITE;
/*!40000 ALTER TABLE `awcm_news_coments` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_news_coments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_news_news`
--

DROP TABLE IF EXISTS `awcm_news_news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_news_news` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` int(11) NOT NULL,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `views` int(11) DEFAULT NULL,
  `rate` int(11) DEFAULT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `allow_coments` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_news_news`
--

LOCK TABLES `awcm_news_news` WRITE;
/*!40000 ALTER TABLE `awcm_news_news` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_news_news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_news_settings`
--

DROP TABLE IF EXISTS `awcm_news_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_news_settings` (
  `send_news` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `news_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `show_sig` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `catpg_clms` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `mpg_clms` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_news_settings`
--

LOCK TABLES `awcm_news_settings` WRITE;
/*!40000 ALTER TABLE `awcm_news_settings` DISABLE KEYS */;
INSERT INTO `awcm_news_settings` VALUES ('yes','20','no','2','2');
/*!40000 ALTER TABLE `awcm_news_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_online`
--

DROP TABLE IF EXISTS `awcm_online`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_online` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `memid` text NOT NULL,
  `time` text NOT NULL,
  `ip` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_online`
--

LOCK TABLES `awcm_online` WRITE;
/*!40000 ALTER TABLE `awcm_online` DISABLE KEYS */;
INSERT INTO `awcm_online` VALUES (15,'no','1782634942','::1'),(16,'1','1782634958','::1');
/*!40000 ALTER TABLE `awcm_online` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_pages`
--

DROP TABLE IF EXISTS `awcm_pages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_pages`
--

LOCK TABLES `awcm_pages` WRITE;
/*!40000 ALTER TABLE `awcm_pages` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_pages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_pro_cat`
--

DROP TABLE IF EXISTS `awcm_pro_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_pro_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `icon` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_pro_cat`
--

LOCK TABLES `awcm_pro_cat` WRITE;
/*!40000 ALTER TABLE `awcm_pro_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_pro_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_pro_pro`
--

DROP TABLE IF EXISTS `awcm_pro_pro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_pro_pro` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` int(11) NOT NULL,
  `name` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `screanshot_yn` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `screanshot_url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `size` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `company` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `license` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `rate` int(11) NOT NULL,
  `downloads` int(11) NOT NULL,
  `author` int(11) NOT NULL,
  `capability` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_pro_pro`
--

LOCK TABLES `awcm_pro_pro` WRITE;
/*!40000 ALTER TABLE `awcm_pro_pro` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_pro_pro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_pro_settings`
--

DROP TABLE IF EXISTS `awcm_pro_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_pro_settings` (
  `send_pro` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `pros_per_page` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `fast_stats` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `rand_pros` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_pro_settings`
--

LOCK TABLES `awcm_pro_settings` WRITE;
/*!40000 ALTER TABLE `awcm_pro_settings` DISABLE KEYS */;
INSERT INTO `awcm_pro_settings` VALUES ('yes','20','yes','yes');
/*!40000 ALTER TABLE `awcm_pro_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_sounds_cat`
--

DROP TABLE IF EXISTS `awcm_sounds_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_sounds_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `sub` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_sounds_cat`
--

LOCK TABLES `awcm_sounds_cat` WRITE;
/*!40000 ALTER TABLE `awcm_sounds_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_sounds_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_sounds_settings`
--

DROP TABLE IF EXISTS `awcm_sounds_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_sounds_settings` (
  `sounds_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `send_sound` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_sounds_settings`
--

LOCK TABLES `awcm_sounds_settings` WRITE;
/*!40000 ALTER TABLE `awcm_sounds_settings` DISABLE KEYS */;
INSERT INTO `awcm_sounds_settings` VALUES ('14','yes');
/*!40000 ALTER TABLE `awcm_sounds_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_sounds_sounds`
--

DROP TABLE IF EXISTS `awcm_sounds_sounds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_sounds_sounds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `cat` int(11) NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `hits` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_sounds_sounds`
--

LOCK TABLES `awcm_sounds_sounds` WRITE;
/*!40000 ALTER TABLE `awcm_sounds_sounds` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_sounds_sounds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_themes`
--

DROP TABLE IF EXISTS `awcm_themes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_themes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `file` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_themes`
--

LOCK TABLES `awcm_themes` WRITE;
/*!40000 ALTER TABLE `awcm_themes` DISABLE KEYS */;
INSERT INTO `awcm_themes` VALUES (14,'nice_motorcycle','nice_motorcycle'),(11,'awcm_darkblue','awcm_darkblue'),(13,'nice_blue','nice_blue'),(12,'silver','silver');
/*!40000 ALTER TABLE `awcm_themes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_topics_cat`
--

DROP TABLE IF EXISTS `awcm_topics_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_topics_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `details` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `sub` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_topics_cat`
--

LOCK TABLES `awcm_topics_cat` WRITE;
/*!40000 ALTER TABLE `awcm_topics_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_topics_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_topics_coments`
--

DROP TABLE IF EXISTS `awcm_topics_coments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_topics_coments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `topic` int(11) NOT NULL,
  `author` int(11) NOT NULL,
  `coment` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_topics_coments`
--

LOCK TABLES `awcm_topics_coments` WRITE;
/*!40000 ALTER TABLE `awcm_topics_coments` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_topics_coments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_topics_settings`
--

DROP TABLE IF EXISTS `awcm_topics_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_topics_settings` (
  `fast_stats` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `send_topic` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `topics_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `show_sig` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `catpg_clms` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_topics_settings`
--

LOCK TABLES `awcm_topics_settings` WRITE;
/*!40000 ALTER TABLE `awcm_topics_settings` DISABLE KEYS */;
INSERT INTO `awcm_topics_settings` VALUES ('yes','no','20','yes','2');
/*!40000 ALTER TABLE `awcm_topics_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_topics_topics`
--

DROP TABLE IF EXISTS `awcm_topics_topics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_topics_topics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` int(11) NOT NULL,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `views` int(11) DEFAULT NULL,
  `rate` int(11) DEFAULT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `allow_coments` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `image` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_topics_topics`
--

LOCK TABLES `awcm_topics_topics` WRITE;
/*!40000 ALTER TABLE `awcm_topics_topics` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_topics_topics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_videos_cat`
--

DROP TABLE IF EXISTS `awcm_videos_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_videos_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `icon` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_videos_cat`
--

LOCK TABLES `awcm_videos_cat` WRITE;
/*!40000 ALTER TABLE `awcm_videos_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_videos_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_videos_coments`
--

DROP TABLE IF EXISTS `awcm_videos_coments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_videos_coments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `video` int(11) NOT NULL,
  `author` int(11) NOT NULL,
  `coment` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_videos_coments`
--

LOCK TABLES `awcm_videos_coments` WRITE;
/*!40000 ALTER TABLE `awcm_videos_coments` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_videos_coments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_videos_settings`
--

DROP TABLE IF EXISTS `awcm_videos_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_videos_settings` (
  `vid_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `logo` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `send_video` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_videos_settings`
--

LOCK TABLES `awcm_videos_settings` WRITE;
/*!40000 ALTER TABLE `awcm_videos_settings` DISABLE KEYS */;
INSERT INTO `awcm_videos_settings` VALUES ('25','../images/vid_logo.png','yes');
/*!40000 ALTER TABLE `awcm_videos_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_videos_videos`
--

DROP TABLE IF EXISTS `awcm_videos_videos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_videos_videos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` int(11) NOT NULL,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `image` mediumblob NOT NULL,
  `rate` int(11) NOT NULL,
  `views` int(11) NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `time` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `allow_coments` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_videos_videos`
--

LOCK TABLES `awcm_videos_videos` WRITE;
/*!40000 ALTER TABLE `awcm_videos_videos` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_videos_videos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_weblinks_cat`
--

DROP TABLE IF EXISTS `awcm_weblinks_cat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_weblinks_cat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_weblinks_cat`
--

LOCK TABLES `awcm_weblinks_cat` WRITE;
/*!40000 ALTER TABLE `awcm_weblinks_cat` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_weblinks_cat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_weblinks_settings`
--

DROP TABLE IF EXISTS `awcm_weblinks_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_weblinks_settings` (
  `webs_per_pg` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_weblinks_settings`
--

LOCK TABLES `awcm_weblinks_settings` WRITE;
/*!40000 ALTER TABLE `awcm_weblinks_settings` DISABLE KEYS */;
INSERT INTO `awcm_weblinks_settings` VALUES ('20');
/*!40000 ALTER TABLE `awcm_weblinks_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awcm_weblinks_sites`
--

DROP TABLE IF EXISTS `awcm_weblinks_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awcm_weblinks_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `name` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `descr` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `author` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `visits` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `rate` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `active` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `date` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `email` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awcm_weblinks_sites`
--

LOCK TABLES `awcm_weblinks_sites` WRITE;
/*!40000 ALTER TABLE `awcm_weblinks_sites` DISABLE KEYS */;
/*!40000 ALTER TABLE `awcm_weblinks_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'awcm'
--

--
-- Dumping routines for database 'awcm'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-29 10:19:22
