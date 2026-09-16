-- MySQL dump 10.13  Distrib 5.5.53, for Win32 (AMD64)
--
-- Host: 127.0.0.1    Database: phpns
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
-- Current Database: `phpns`
--

/*!40000 DROP DATABASE IF EXISTS `phpns`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `phpns` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `phpns`;

--
-- Table structure for table `phpns_articles`
--

DROP TABLE IF EXISTS `phpns_articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_articles` (
  `id` int(25) NOT NULL AUTO_INCREMENT,
  `article_title` varchar(100) NOT NULL,
  `article_subtitle` varchar(100) NOT NULL,
  `article_author` varchar(100) NOT NULL,
  `article_cat` varchar(15) NOT NULL,
  `article_text` varchar(20000) NOT NULL,
  `article_exptext` varchar(20000) NOT NULL,
  `article_imgid` varchar(100) NOT NULL,
  `allow_comments` varchar(1) NOT NULL,
  `start_date` varchar(15) NOT NULL,
  `end_date` varchar(15) NOT NULL,
  `active` varchar(1) NOT NULL,
  `approved` varchar(1) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `ip` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `article_title` (`article_title`,`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_articles`
--

LOCK TABLES `phpns_articles` WRITE;
/*!40000 ALTER TABLE `phpns_articles` DISABLE KEYS */;
INSERT INTO `phpns_articles` VALUES (1,'Welcome to phpns!','','admin','all','&lt;p&gt;If you see are viewing this message, the phpns installation was a success! This article is filed under &amp;quot;Site Wide News&amp;quot;, which is the default category that is created during installation.&lt;/p&gt;&lt;p&gt;&lt;font color=&quot;#993300&quot;&gt;You are free to modify this message, or delete it all together&lt;/font&gt;. Why should you use phpns?&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&lt;strong&gt;It&#039;s free&lt;/strong&gt;. Phpns is released under the GPL license, which gives you the ability to change it, redistribute it, and use it personally or professionally.&lt;/li&gt;&lt;li&gt;&lt;strong&gt;It&#039;s clean&lt;/strong&gt;. It&#039;s a breath or fresh air, following web standards and semantics. The (open-source) code is neatly organized, logically indented, and well-commented to make changes easier.&lt;/li&gt;&lt;li&gt;I&lt;strong&gt;t&#039;s easy to integrate&lt;/strong&gt;. Only one line of code is necessary on your website, and you have a dynamic, fully functional news system. &lt;/li&gt;&lt;li&gt;&lt;strong&gt;It&#039;s easy to install&lt;/strong&gt;. The guided installation will have you up and running in minutes, asking you just a few questions about your database setup.&lt;/li&gt;&lt;/ul&gt;Some more information is available in the &amp;quot;Full Article&amp;quot; section...','What does &amp;quot;free&amp;quot; mean? &lt;blockquote&gt;To the phpns developers, the word &amp;quot;free&amp;quot; means more than just the cost of the product. The word free means that &lt;strong&gt;you are free&lt;/strong&gt; to modify anything you want about phpns, without any license restrictions.&lt;/blockquote&gt;&lt;p&gt;Why is phpns free in both price and modification?&lt;/p&gt;&lt;blockquote&gt;&lt;p&gt;Because we believe in the open-source message. Closed source applications restrict the user from customizing the way the system works, and prevents the communitiy from contributing to the package. Plus, we love seeing our software being put to good use, and we love modifications.&lt;/p&gt;&lt;/blockquote&gt;&lt;p&gt;Why don&#039;t you require a &amp;quot;Powered by phpns&amp;quot; message at the bottom of each page, like other news systems?&lt;/p&gt;&lt;blockquote&gt;&lt;p&gt;Because we hated that when using other products... and the fact that you had to pay to have it removed. However, if you don&#039;t mind a message like that, it can be enabled in the preferences system. It&#039;s disabled by default.&lt;/p&gt;&lt;/blockquote&gt;&lt;p&gt;What can I do to help the project?&lt;/p&gt;&lt;blockquote&gt;&lt;p&gt;If you would like to be a part of the project, we always appreciate help. What you can do:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Spread the word. Recommend our system to your friends and co-workers!&lt;/li&gt;&lt;li&gt;Report bugs you&#039;ve encountered at the &lt;a href=&quot;http://launchpad.net/phpns&quot;&gt;phpns launchpad website&lt;/a&gt;. &lt;/li&gt;&lt;li&gt;Submit reviews to software review websites around the internet. As long as they are honest, this is a great way to help us.&lt;/li&gt;&lt;li&gt;Donate. This helps with hosting/domain costs, and you&#039;ll get your name on the website along with a message and URL of your blog/website.&lt;/li&gt;&lt;li&gt;Become a sponsor. If you&#039;re a hosting service, business, or organization, we&#039;re always looking for funding and bandwith.&lt;/li&gt;&lt;li&gt;Develop. Contact us on the website if you think we could use your services.&lt;/li&gt;&lt;/ul&gt;That&#039;s it. Enjoy phpns!&lt;br /&gt;&lt;/blockquote&gt;','imgid','0','','','1','1','1782738974','::1'),(2,'DRHL PHPNS Seed Article 01 - admin','admin owned seed','admin','32','DRHL phpns admin article main text 01','DRHL phpns admin article extended text 01','','1','1782653675','1783604075','1','1','1782732075','127.0.0.1'),(3,'DRHL PHPNS Seed Article 02 - admin','admin owned seed','admin','32','DRHL phpns admin article main text 02','DRHL phpns admin article extended text 02','','1','1782653675','1783604075','1','1','1782732175','127.0.0.1'),(4,'DRHL PHPNS Seed Article 03 - user1','user1 owned seed','user1','32','DRHL phpns user1 article main text 03','DRHL phpns user1 article extended text 03','','1','1782653675','1783604075','1','1','1782732275','127.0.0.1'),(5,'DRHL PHPNS Seed Article 04 - user1','user1 owned seed','user1','32','DRHL phpns user1 article main text 04','DRHL phpns user1 article extended text 04','','1','1782653675','1783604075','1','1','1782732375','127.0.0.1'),(6,'DRHL PHPNS Seed Article 05 - user2','user2 owned seed','user2','32','DRHL phpns user2 article main text 05','DRHL phpns user2 article extended text 05','','1','1782653675','1783604075','1','1','1782732475','127.0.0.1'),(7,'DRHL PHPNS Seed Article 06 - user2','user2 owned seed','user2','32','DRHL phpns user2 article main text 06','DRHL phpns user2 article extended text 06','','1','1782653675','1783604075','1','1','1782732575','127.0.0.1'),(8,'DRHL PHPNS Seed Article 07 - user1','user1 owned seed','user1','32','DRHL phpns user1 article main text 07','DRHL phpns user1 article extended text 07','','1','1782653675','1783604075','1','1','1782732675','127.0.0.1'),(9,'DRHL PHPNS Seed Article 08 - user2','user2 owned seed','user2','32','DRHL phpns user2 article main text 08','DRHL phpns user2 article extended text 08','','1','1782653675','1783604075','1','1','1782732775','127.0.0.1');
/*!40000 ALTER TABLE `phpns_articles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_banlist`
--

DROP TABLE IF EXISTS `phpns_banlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_banlist` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `ip` varchar(15) NOT NULL,
  `banned_by` varchar(20) NOT NULL,
  `reason` varchar(5000) NOT NULL,
  `timestamp` varchar(12) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_banlist`
--

LOCK TABLES `phpns_banlist` WRITE;
/*!40000 ALTER TABLE `phpns_banlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `phpns_banlist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_categories`
--

DROP TABLE IF EXISTS `phpns_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_categories` (
  `id` int(15) NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(100) NOT NULL,
  `cat_parent` varchar(10000) NOT NULL,
  `cat_author` varchar(100) NOT NULL,
  `cat_desc` varchar(1000) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `ip` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_categories`
--

LOCK TABLES `phpns_categories` WRITE;
/*!40000 ALTER TABLE `phpns_categories` DISABLE KEYS */;
INSERT INTO `phpns_categories` VALUES (32,'Site news','','admin','This is for general news on your website.','1782738974','::1');
/*!40000 ALTER TABLE `phpns_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_comments`
--

DROP TABLE IF EXISTS `phpns_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_comments` (
  `id` int(25) NOT NULL AUTO_INCREMENT,
  `article_id` varchar(25) NOT NULL,
  `comment_text` varchar(1000) NOT NULL,
  `website` varchar(100) NOT NULL,
  `comment_author` varchar(20) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `approved` varchar(1) NOT NULL,
  `ip` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_comments`
--

LOCK TABLES `phpns_comments` WRITE;
/*!40000 ALTER TABLE `phpns_comments` DISABLE KEYS */;
INSERT INTO `phpns_comments` VALUES (1,'2','DRHL phpns seed comment A for article 2','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(2,'3','DRHL phpns seed comment A for article 3','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(3,'4','DRHL phpns seed comment A for article 4','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(4,'5','DRHL phpns seed comment A for article 5','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(5,'6','DRHL phpns seed comment A for article 6','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(6,'7','DRHL phpns seed comment A for article 7','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(7,'8','DRHL phpns seed comment A for article 8','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(8,'9','DRHL phpns seed comment A for article 9','http://localhost/phpns/','user1','1782737075','1','127.0.0.1'),(16,'2','DRHL phpns seed comment B for article 2','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(17,'3','DRHL phpns seed comment B for article 3','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(18,'4','DRHL phpns seed comment B for article 4','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(19,'5','DRHL phpns seed comment B for article 5','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(20,'6','DRHL phpns seed comment B for article 6','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(21,'7','DRHL phpns seed comment B for article 7','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(22,'8','DRHL phpns seed comment B for article 8','http://localhost/phpns/','user2','1782737175','1','127.0.0.1'),(23,'9','DRHL phpns seed comment B for article 9','http://localhost/phpns/','user2','1782737175','1','127.0.0.1');
/*!40000 ALTER TABLE `phpns_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_cookielog`
--

DROP TABLE IF EXISTS `phpns_cookielog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_cookielog` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(15) NOT NULL,
  `rank_id` varchar(15) NOT NULL,
  `cookie_id` varchar(32) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `ip` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_cookielog`
--

LOCK TABLES `phpns_cookielog` WRITE;
/*!40000 ALTER TABLE `phpns_cookielog` DISABLE KEYS */;
INSERT INTO `phpns_cookielog` VALUES (1,'10','3','a3324635c7a970823573b62740104680','1788667360','::1'),(2,'9','2','7103b06fe5839678fa379c7a780bf41a','1788667360','::1');
/*!40000 ALTER TABLE `phpns_cookielog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_gconfig`
--

DROP TABLE IF EXISTS `phpns_gconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_gconfig` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `v1` varchar(17) NOT NULL,
  `v2` varchar(10) NOT NULL,
  `v3` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_gconfig`
--

LOCK TABLES `phpns_gconfig` WRITE;
/*!40000 ALTER TABLE `phpns_gconfig` DISABLE KEYS */;
INSERT INTO `phpns_gconfig` VALUES (15,'siteonline','0','0','0'),(16,'def_rsslimit','','','3'),(17,'def_rssorder','desc','',''),(18,'def_items_per_page','10','',''),(19,'def_rsstitle','','','phpns rss feed'),(20,'def_rssdesc','','','An RSS feed from phpns articles.'),(21,'def_rssenabled','1','',''),(22,'def_limit','10','',''),(23,'def_order','desc','',''),(24,'def_offset','0','',''),(25,'timestamp_format','','','l F d, Y  g:i a'),(26,'def_comlimit','','','100000'),(27,'def_comenabled','1','',''),(28,'def_comorder','asc','',''),(29,'global_message','','','Welcome to the phpns admin panel! Click \'change message\' to modify/delete this message.'),(30,'siteonline','0','0','0'),(31,'wysiwyg','yes','',''),(32,'sys_time_format','l F d, Y  g:i a','',''),(33,'line','yes','','');
/*!40000 ALTER TABLE `phpns_gconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_images`
--

DROP TABLE IF EXISTS `phpns_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_images` (
  `id` int(15) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(15) NOT NULL,
  `image_filepath` varchar(500) NOT NULL,
  `alt_description` varchar(100) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `ip` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_images`
--

LOCK TABLES `phpns_images` WRITE;
/*!40000 ALTER TABLE `phpns_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `phpns_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_ranks`
--

DROP TABLE IF EXISTS `phpns_ranks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_ranks` (
  `id` int(15) NOT NULL AUTO_INCREMENT,
  `rank_title` varchar(100) NOT NULL,
  `rank_desc` varchar(1000) NOT NULL,
  `rank_author` varchar(100) NOT NULL,
  `permissions` varchar(100) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_ranks`
--

LOCK TABLES `phpns_ranks` WRITE;
/*!40000 ALTER TABLE `phpns_ranks` DISABLE KEYS */;
INSERT INTO `phpns_ranks` VALUES (1,'Administrators','Any user assigned to this rank will have full access.','admin','1,1,1,1,1,1,1,1,1,1,1,1','1782738974'),(2,'register','Only some functions can be used','admin','0,0,0,0,1,0,0,0,0,0,0,0','1782739299'),(3,'users','Only some functions can be used','admin','0,0,0,0,1,1,1,1,1,0,1,1','1782739479');
/*!40000 ALTER TABLE `phpns_ranks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_syslog`
--

DROP TABLE IF EXISTS `phpns_syslog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_syslog` (
  `id` int(24) NOT NULL AUTO_INCREMENT,
  `task` varchar(20) NOT NULL,
  `description` varchar(200) NOT NULL,
  `user` int(5) NOT NULL,
  `page` varchar(120) NOT NULL,
  `timestamp` varchar(12) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_syslog`
--

LOCK TABLES `phpns_syslog` WRITE;
/*!40000 ALTER TABLE `phpns_syslog` DISABLE KEYS */;
INSERT INTO `phpns_syslog` VALUES (12,'INSTALL','User &lt;i&gt;admin&lt;/i&gt; has installed phpns!',0,'/phpns/install/','1782738974'),(13,'new_user','User &lt;i&gt;admin&lt;/i&gt; has &lt;strong&gt;created&lt;/strong&gt; a new user account named &lt;i&gt;register&lt;/i&gt; (lhl) with the rank of 2',14,'/phpns/user.php?do=newp','1782739504'),(14,'new_user','User &lt;i&gt;admin&lt;/i&gt; has &lt;strong&gt;created&lt;/strong&gt; a new user account named &lt;i&gt;user1&lt;/i&gt; (lhl) with the rank of 3',14,'/phpns/user.php?do=newp','1782739518'),(15,'new_user','User &lt;i&gt;admin&lt;/i&gt; has &lt;strong&gt;created&lt;/strong&gt; a new user account named &lt;i&gt;user2&lt;/i&gt; (lhl) with the rank of 3',14,'/phpns/user.php?do=newp','1782739531'),(16,'login','User &lt;i&gt;user1&lt;/i&gt; has &lt;strong&gt;logged in&lt;/strong&gt;',10,'/phpns/login.php?do=p','1788667360'),(17,'login','User &lt;i&gt;register&lt;/i&gt; has &lt;strong&gt;logged in&lt;/strong&gt;',9,'/phpns/login.php?do=p','1788667360');
/*!40000 ALTER TABLE `phpns_syslog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_templates`
--

DROP TABLE IF EXISTS `phpns_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_templates` (
  `id` int(15) NOT NULL AUTO_INCREMENT,
  `template_name` varchar(100) NOT NULL,
  `template_desc` varchar(1000) NOT NULL,
  `template_author` varchar(100) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `html_article` varchar(5000) NOT NULL,
  `html_comment` varchar(5000) NOT NULL,
  `html_form` varchar(5000) NOT NULL,
  `html_pagination` varchar(5000) NOT NULL,
  `template_selected` varchar(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_templates`
--

LOCK TABLES `phpns_templates` WRITE;
/*!40000 ALTER TABLE `phpns_templates` DISABLE KEYS */;
INSERT INTO `phpns_templates` VALUES (9,'Default','This is the default phpns template.','Phpns-team','1194252704','&lt;div style=&quot;margin-bottom: 30px; min-height: 130px;&quot;&gt;\r\n &lt;h2 style=&quot;margin-bottom: 0pt&quot;&gt;&lt;a href=&quot;{article_href}&quot; style=&quot;text-decoration: none;&quot;&gt;{title}&lt;/a&gt;&lt;/h2&gt;\r\n  &lt;h4 style=&quot;margin: 0 0 0 3em; font-weight: normal;&quot;&gt;&lt;em&gt;Posted by &lt;a href=&quot;#&quot;&gt;{author}&lt;/a&gt;&lt;/em&gt;&lt;/h4&gt;\r\n &lt;div style=&quot;float:right; padding: 0 0 10px 10px&quot;&gt;{reddit} {digg}&lt;/div&gt;\r\n {main_article}\r\n &lt;div&gt;\r\n  {full_story}\r\n\r\n  &lt;div id=&quot;comments&quot; style=&quot;text-align: right;&quot;&gt;\r\n  &lt;strong&gt;&lt;a href=&quot;{article_href}#comments&quot;&gt;{comment_count} comments&lt;/a&gt;&lt;/strong&gt;\r\n  &lt;/div&gt;\r\n &lt;/div&gt;\r\n&lt;/div&gt;','&lt;div style=&quot;background: #eee; font: caption; margin: 20px 0 0 5%; padding: 5px;&quot;&gt;\r\n &lt;div style=&quot;border: 1px solid #ccc; padding: 3px; background: #ccc; margin-bottom: 5px;&quot;&gt; \r\n  &lt;div style=&quot;text-align: right; float: right&quot;&gt; {timestamp}&lt;/div&gt;  \r\n &lt;strong&gt;Posted by  &lt;a href=&quot;{website}&quot;&gt;{author}&lt;/a&gt;&lt;/strong&gt; as {ip}\r\n &lt;/div&gt;\r\n {comment}\r\n&lt;/div&gt;','&lt;div style=&quot;font: caption; margin-left: 5%;&quot;&gt;\r\n&lt;form style=&quot;margin-top: 50px;&quot; action=&quot;{action}&quot; method=&quot;post&quot;&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;name&quot; id=&quot;name&quot; /&gt; &lt;label for=&quot;name&quot;&gt;Name (required)&lt;/label&gt;&lt;br /&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;email&quot; id=&quot;email&quot; /&gt; &lt;label for=&quot;email&quot;&gt;Email (not published) (required)&lt;/label&gt;&lt;br /&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;website&quot; id=&quot;website&quot; /&gt; &lt;label for=&quot;website&quot;&gt;Website&lt;/label&gt;&lt;br /&gt;\r\n&lt;textarea name=&quot;comment&quot; style=&quot;width:100%; height: 150px&quot;&gt;&lt;/textarea&gt;&lt;br /&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;captcha&quot; style=&quot;width: 100px&quot; /&gt; &lt;label for=&quot;captcha&quot;&gt;&lt;strong&gt;What is {captcha_question}?&lt;/strong&gt;&lt;/label&gt;&lt;br /&gt;\r\n{hidden_data}\r\n{captcha_answer}\r\n&lt;input type=&quot;submit&quot; value=&quot;Submit comment&quot; id=&quot;submit&quot; /&gt;\r\n&lt;/form&gt;\r\n&lt;/div&gt;','&lt;a style=&quot;padding: 3px; margin: 10px; border: 1px solid #888;&quot; href=&quot;{previous_page}&quot;&gt;Previous Page&lt;/a&gt; {middle_pages} &lt;a  style=&quot;padding: 3px; margin: 10px; border: 1px solid #888;&quot; href=&quot;{next_page}&quot;&gt;Next Page&lt;/a&gt;','1');
/*!40000 ALTER TABLE `phpns_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_themes`
--

DROP TABLE IF EXISTS `phpns_themes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_themes` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `theme_name` varchar(100) NOT NULL,
  `theme_author` varchar(100) NOT NULL,
  `theme_dir` varchar(200) NOT NULL,
  `base_dir` varchar(50) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `theme_selected` varchar(1) NOT NULL,
  `permissions` varchar(10000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_themes`
--

LOCK TABLES `phpns_themes` WRITE;
/*!40000 ALTER TABLE `phpns_themes` DISABLE KEYS */;
INSERT INTO `phpns_themes` VALUES (9,'default','phpns team','themes/default/','default','1782738974','1','');
/*!40000 ALTER TABLE `phpns_themes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_userlogin`
--

DROP TABLE IF EXISTS `phpns_userlogin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_userlogin` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(15) NOT NULL,
  `rank_id` varchar(15) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `ip` varchar(15) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_userlogin`
--

LOCK TABLES `phpns_userlogin` WRITE;
/*!40000 ALTER TABLE `phpns_userlogin` DISABLE KEYS */;
INSERT INTO `phpns_userlogin` VALUES (1,'user1','3','1788667360','::1'),(2,'register','2','1788667360','::1');
/*!40000 ALTER TABLE `phpns_userlogin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phpns_users`
--

DROP TABLE IF EXISTS `phpns_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phpns_users` (
  `id` int(15) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(100) NOT NULL,
  `full_name` varchar(150) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(40) NOT NULL,
  `timestamp` varchar(15) NOT NULL,
  `ip` varchar(15) NOT NULL,
  `msn` varchar(100) NOT NULL,
  `aim` varchar(100) NOT NULL,
  `yahoo` varchar(100) NOT NULL,
  `skype` varchar(100) NOT NULL,
  `display_picture` varchar(150) NOT NULL,
  `rank_id` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phpns_users`
--

LOCK TABLES `phpns_users` WRITE;
/*!40000 ALTER TABLE `phpns_users` DISABLE KEYS */;
INSERT INTO `phpns_users` VALUES (8,'admin','admin','','7c4a8d09ca3762af61e59520943dc26494f8941b','1782738974','127.0.0.1','','','','','','1'),(9,'register','lhl','','7c4a8d09ca3762af61e59520943dc26494f8941b','1782739504','::1','','','','',' ','2'),(10,'user1','lhl','','7c4a8d09ca3762af61e59520943dc26494f8941b','1782739518','::1','','','','',' ','3'),(11,'user2','lhl','','7c4a8d09ca3762af61e59520943dc26494f8941b','1782739531','::1','','','','',' ','3');
/*!40000 ALTER TABLE `phpns_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'phpns'
--

--
-- Dumping routines for database 'phpns'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-06 12:57:42
