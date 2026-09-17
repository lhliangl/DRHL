-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: phpoll
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
-- Current Database: `phpoll`
--

/*!40000 DROP DATABASE IF EXISTS `phpoll`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `phpoll` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `phpoll`;

--
-- Table structure for table `phpoll_test_band`
--

DROP TABLE IF EXISTS `phpoll_test_band`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpoll_test_band` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `nome_band` text NOT NULL,
  `voti` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=67 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpoll_test_band`
--

LOCK TABLES `phpoll_test_band` WRITE;
/*!40000 ALTER TABLE `phpoll_test_band` DISABLE KEYS */;
/*!40000 ALTER TABLE `phpoll_test_band` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpoll_test_configurazione`
--

DROP TABLE IF EXISTS `phpoll_test_configurazione`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpoll_test_configurazione` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `max_voti` int(10) unsigned NOT NULL,
  `titolo_posizione` varchar(100) NOT NULL,
  `titolo_tipologia` varchar(100) NOT NULL,
  `titolo_punteggio` varchar(100) NOT NULL,
  `login` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `risultati_pixel` int(10) unsigned NOT NULL,
  `intervallo_tempo` int(10) unsigned NOT NULL,
  `barra1r` int(10) unsigned NOT NULL,
  `barra1g` int(10) unsigned NOT NULL,
  `barra1b` int(10) unsigned NOT NULL,
  `barra2r` int(10) unsigned NOT NULL,
  `barra2g` int(10) unsigned NOT NULL,
  `barra2b` int(10) unsigned NOT NULL,
  `barra3r` int(10) unsigned NOT NULL,
  `barra3g` int(10) unsigned NOT NULL,
  `barra3b` int(10) unsigned NOT NULL,
  `barra4r` int(10) unsigned NOT NULL,
  `barra4g` int(10) unsigned NOT NULL,
  `barra4b` int(10) unsigned NOT NULL,
  `percorso_link` varchar(100) NOT NULL,
  `domini` text NOT NULL,
  `messaggio_domini` text NOT NULL,
  `messaggio_giavotato` text NOT NULL,
  `messaggio_sgamo` text NOT NULL,
  `messaggio_ip` text NOT NULL,
  `oggetto_email` text NOT NULL,
  `messaggio_conferma_mail` text NOT NULL,
  `testo_email` text NOT NULL,
  `valid_email` text NOT NULL,
  `testo_submit` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpoll_test_configurazione`
--

LOCK TABLES `phpoll_test_configurazione` WRITE;
/*!40000 ALTER TABLE `phpoll_test_configurazione` DISABLE KEYS */;
INSERT INTO `phpoll_test_configurazione` VALUES (1,0,'khVdupYw','PcPlI7Kk','Q226OhVz','admin3','123456',1,0,0,10,26,14,252,12,4,12,0,85,1,14,'W2LyZv8a','m9MhKNOx','s2AJYwcN','EZUSbRM1','Cx293jNv','azcnQuju','eAtkck4c','esnaFXi2','jdwauiqddgIV7hFsEKJgwXqHeJ3qYrn1abFykI','Rjfuo6ik','eeN5lMQV');
/*!40000 ALTER TABLE `phpoll_test_configurazione` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpoll_test_voti`
--

DROP TABLE IF EXISTS `phpoll_test_voti`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpoll_test_voti` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) NOT NULL DEFAULT '',
  `band_votate` text NOT NULL,
  `timestamp` int(11) NOT NULL DEFAULT '0',
  `votato` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `browser` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpoll_test_voti`
--

LOCK TABLES `phpoll_test_voti` WRITE;
/*!40000 ALTER TABLE `phpoll_test_voti` DISABLE KEYS */;
/*!40000 ALTER TABLE `phpoll_test_voti` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'phpoll'
--

--
-- Dumping routines for database 'phpoll'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-29 20:26:56
