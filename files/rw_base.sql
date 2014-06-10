# ************************************************************
# Sequel Pro SQL dump
# Version 4096
#
# http://www.sequelpro.com/
# http://code.google.com/p/sequel-pro/
#
# Host: 192.168.30.12 (MySQL 5.5.35-0ubuntu0.12.04.2)
# Database: roundware
# Generation Time: 2014-06-03 19:06:13 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table rw_asset
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_asset`;

CREATE TABLE `rw_asset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `filename` varchar(256) DEFAULT NULL,
  `volume` double DEFAULT NULL,
  `submitted` tinyint(1) NOT NULL,
  `project_id` int(11) DEFAULT NULL,
  `created` datetime NOT NULL,
  `audiolength` bigint(20) DEFAULT NULL,
  `language_id` int(11) DEFAULT NULL,
  `file` varchar(100) NOT NULL DEFAULT '/var/www/rwmedia/rw_test_audio1.wav',
  `weight` int(11) NOT NULL,
  `mediatype` varchar(16) NOT NULL,
  `description` longtext NOT NULL,
  `initialenvelope_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_asset_6b4dc4c3` (`session_id`),
  KEY `rw_asset_499df97c` (`project_id`),
  KEY `rw_asset_7ab48146` (`language_id`),
  CONSTRAINT `language_id_refs_id_56fa8d6c` FOREIGN KEY (`language_id`) REFERENCES `rw_language` (`id`),
  CONSTRAINT `project_id_refs_id_74b331dc` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`),
  CONSTRAINT `session_id_refs_id_5ac0ae9` FOREIGN KEY (`session_id`) REFERENCES `rw_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_asset` WRITE;
/*!40000 ALTER TABLE `rw_asset` DISABLE KEYS */;

INSERT INTO `rw_asset` (`id`, `session_id`, `latitude`, `longitude`, `filename`, `volume`, `submitted`, `project_id`, `created`, `audiolength`, `language_id`, `file`, `weight`, `mediatype`, `description`, `initialenvelope_id`)
VALUES
	(1,2891,28.2562653919411,-58.94140825,'rw_test_audio1.wav',1,1,1,'2012-07-24 18:06:40',30000000000,1,'',50,'audio','',NULL);

/*!40000 ALTER TABLE `rw_asset` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_asset_loc_description
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_asset_loc_description`;

CREATE TABLE `rw_asset_loc_description` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `asset_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rw_asset_loc_description_asset_id_30aea39a_uniq` (`asset_id`,`localizedstring_id`),
  KEY `rw_asset_loc_description_a64c0c36` (`asset_id`),
  KEY `rw_asset_loc_description_f2fd4c16` (`localizedstring_id`),
  CONSTRAINT `asset_id_refs_id_27a2eee3` FOREIGN KEY (`asset_id`) REFERENCES `rw_asset` (`id`),
  CONSTRAINT `localizedstring_id_refs_id_1dfa14d` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table rw_asset_tags
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_asset_tags`;

CREATE TABLE `rw_asset_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `asset_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_id` (`asset_id`,`tag_id`),
  KEY `rw_asset_tags_7696bc7d` (`asset_id`),
  KEY `rw_asset_tags_3747b463` (`tag_id`),
  CONSTRAINT `asset_id_refs_id_569bfdc6` FOREIGN KEY (`asset_id`) REFERENCES `rw_asset` (`id`),
  CONSTRAINT `tag_id_refs_id_25993850` FOREIGN KEY (`tag_id`) REFERENCES `rw_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_asset_tags` WRITE;
/*!40000 ALTER TABLE `rw_asset_tags` DISABLE KEYS */;

INSERT INTO `rw_asset_tags` (`id`, `asset_id`, `tag_id`)
VALUES
	(2,1,3),
	(3,1,5),
	(1,1,8);

/*!40000 ALTER TABLE `rw_asset_tags` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_audiotrack
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_audiotrack`;

CREATE TABLE `rw_audiotrack` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `minvolume` double NOT NULL,
  `maxvolume` double NOT NULL,
  `minduration` double NOT NULL,
  `maxduration` double NOT NULL,
  `mindeadair` double NOT NULL,
  `maxdeadair` double NOT NULL,
  `minfadeintime` double NOT NULL,
  `maxfadeintime` double NOT NULL,
  `minfadeouttime` double NOT NULL,
  `maxfadeouttime` double NOT NULL,
  `minpanpos` double NOT NULL,
  `maxpanpos` double NOT NULL,
  `minpanduration` double NOT NULL,
  `maxpanduration` double NOT NULL,
  `repeatrecordings` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_audiotrack_499df97c` (`project_id`),
  CONSTRAINT `project_id_refs_id_3c3c55a6` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_audiotrack` WRITE;
/*!40000 ALTER TABLE `rw_audiotrack` DISABLE KEYS */;

INSERT INTO `rw_audiotrack` (`id`, `project_id`, `minvolume`, `maxvolume`, `minduration`, `maxduration`, `mindeadair`, `maxdeadair`, `minfadeintime`, `maxfadeintime`, `minfadeouttime`, `maxfadeouttime`, `minpanpos`, `maxpanpos`, `minpanduration`, `maxpanduration`, `repeatrecordings`)
VALUES
	(1,1,1,1,5000000000,10000000000,1000000000,3000000000,100000000,500000000,100000000,2000000000,0,0,5000000000,10000000000,0);

/*!40000 ALTER TABLE `rw_audiotrack` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_envelope
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_envelope`;

CREATE TABLE `rw_envelope` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_envelope_6b4dc4c3` (`session_id`),
  CONSTRAINT `session_id_refs_id_4a38374a` FOREIGN KEY (`session_id`) REFERENCES `rw_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_envelope` WRITE;
/*!40000 ALTER TABLE `rw_envelope` DISABLE KEYS */;

INSERT INTO `rw_envelope` (`id`, `session_id`, `created`)
VALUES
	(302,2891,'2013-01-21 10:36:44');

/*!40000 ALTER TABLE `rw_envelope` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_envelope_assets
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_envelope_assets`;

CREATE TABLE `rw_envelope_assets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `envelope_id` int(11) NOT NULL,
  `asset_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `envelope_id` (`envelope_id`,`asset_id`),
  KEY `rw_envelope_assets_169cd330` (`envelope_id`),
  KEY `rw_envelope_assets_7696bc7d` (`asset_id`),
  CONSTRAINT `asset_id_refs_id_2fed96b3` FOREIGN KEY (`asset_id`) REFERENCES `rw_asset` (`id`),
  CONSTRAINT `envelope_id_refs_id_1a4d3e14` FOREIGN KEY (`envelope_id`) REFERENCES `rw_envelope` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_envelope_assets` WRITE;
/*!40000 ALTER TABLE `rw_envelope_assets` DISABLE KEYS */;

INSERT INTO `rw_envelope_assets` (`id`, `envelope_id`, `asset_id`)
VALUES
	(1,302,1);

/*!40000 ALTER TABLE `rw_envelope_assets` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_event
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_event`;

CREATE TABLE `rw_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_time` datetime NOT NULL,
  `client_time` varchar(50) DEFAULT NULL,
  `session_id` int(11) NOT NULL,
  `event_type` varchar(50) NOT NULL,
  `data` longtext,
  `latitude` varchar(50) DEFAULT NULL,
  `longitude` varchar(50) DEFAULT NULL,
  `tags` longtext,
  `operationid` int(11) DEFAULT NULL,
  `udid` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_event_6b4dc4c3` (`session_id`),
  CONSTRAINT `session_id_refs_id_2aa2ee27` FOREIGN KEY (`session_id`) REFERENCES `rw_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_event` WRITE;
/*!40000 ALTER TABLE `rw_event` DISABLE KEYS */;

INSERT INTO `rw_event` (`id`, `server_time`, `client_time`, `session_id`, `event_type`, `data`, `latitude`, `longitude`, `tags`, `operationid`, `udid`)
VALUES
	(10,'2013-12-24 22:29:44',NULL,2891,'request_stream',NULL,NULL,NULL,NULL,NULL,NULL);

/*!40000 ALTER TABLE `rw_event` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_eventtype
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_eventtype`;

CREATE TABLE `rw_eventtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table rw_language
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_language`;

CREATE TABLE `rw_language` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `language_code` varchar(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_language` WRITE;
/*!40000 ALTER TABLE `rw_language` DISABLE KEYS */;

INSERT INTO `rw_language` (`id`, `language_code`)
VALUES
	(1,'en'),
	(2,'es');

/*!40000 ALTER TABLE `rw_language` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_listeninghistoryitem
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_listeninghistoryitem`;

CREATE TABLE `rw_listeninghistoryitem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) NOT NULL,
  `asset_id` int(11) NOT NULL,
  `starttime` datetime NOT NULL,
  `duration` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_listeninghistoryitem_6b4dc4c3` (`session_id`),
  KEY `rw_listeninghistoryitem_7696bc7d` (`asset_id`),
  CONSTRAINT `asset_id_refs_id_549ea184` FOREIGN KEY (`asset_id`) REFERENCES `rw_asset` (`id`),
  CONSTRAINT `session_id_refs_id_7131cf26` FOREIGN KEY (`session_id`) REFERENCES `rw_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



# Dump of table rw_localizedstring
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_localizedstring`;

CREATE TABLE `rw_localizedstring` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `localized_string` longtext NOT NULL,
  `language_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_localizedstring_7ab48146` (`language_id`),
  CONSTRAINT `language_id_refs_id_155857ee` FOREIGN KEY (`language_id`) REFERENCES `rw_language` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_localizedstring` WRITE;
/*!40000 ALTER TABLE `rw_localizedstring` DISABLE KEYS */;

INSERT INTO `rw_localizedstring` (`id`, `localized_string`, `language_id`)
VALUES
	(5,'male',1),
	(6,'hombre',2),
	(7,'female',1),
	(8,'mujer',2),
	(9,'Why are you using Roundware?',1),
	(10,'¿Por qué utiliza Roundware?',2),
	(15,'Artist',1),
	(16,'Artista',2),
	(17,'Visitor',1),
	(18,'Visitante',2),
	(41,'Leave feedback',1),
	(42,'Dejar comentario',2),
	(43,'Respond to something you\'ve heard.',1),
	(44,'Responde sobre algo que has escuchado.',2),
	(47,'You are out of range of this Roundware project.  Please go somewhere within range and try again.  Thank you.',1),
	(48,'Está fuera del alcance de este proyecto Roundware. Por favor, vaya en alguna parte dentro del rango y vuelve a intentarlo. Gracias.',2),
	(49,'Check out this awesome recording I made using Roundware!',1),
	(50,'Echa un vistazo a este impresionante grabación que hice usando Roundware!',2),
	(53,'Herein should be the brief legal agreement that participants need to agree to in order to make and submit a recording to a Roundware project.',1),
	(54,'En esto debería ser el acuerdo escrito legal que los participantes deben ponerse de acuerdo a fin de realizar y presentar una grabación a un proyecto Roundware.',2),
	(55,'What genders do you want to listen to?',1),
	(56,'¿Qué géneros Qué quieres escuchar?',2),
	(57,'Curator',1),
	(58,'recent recordings',1),
	(59,'nearby recordings',1),
	(60,'Who do you want to hear?',1),
	(61,'Who are you?',1),
	(62,'What do you want to talk about?',1),
	(63,'What do you want to listen to?',1),
	(64,'What gender are you?',1);

/*!40000 ALTER TABLE `rw_localizedstring` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_masterui
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_masterui`;

CREATE TABLE `rw_masterui` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `ui_mode_id` int(11) NOT NULL,
  `tag_category_id` int(11) NOT NULL,
  `select_id` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `index` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_masterui_419d03c9` (`ui_mode_id`),
  KEY `rw_masterui_1f0789df` (`tag_category_id`),
  KEY `rw_masterui_19d006d2` (`select_id`),
  KEY `rw_masterui_499df97c` (`project_id`),
  CONSTRAINT `project_id_refs_id_25de30ff` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`),
  CONSTRAINT `select_id_refs_id_4ebcadbb` FOREIGN KEY (`select_id`) REFERENCES `rw_selectionmethod` (`id`),
  CONSTRAINT `tag_category_id_refs_id_1bd43db2` FOREIGN KEY (`tag_category_id`) REFERENCES `rw_tagcategory` (`id`),
  CONSTRAINT `ui_mode_id_refs_id_1d04d87e` FOREIGN KEY (`ui_mode_id`) REFERENCES `rw_uimode` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_masterui` WRITE;
/*!40000 ALTER TABLE `rw_masterui` DISABLE KEYS */;

INSERT INTO `rw_masterui` (`id`, `name`, `ui_mode_id`, `tag_category_id`, `select_id`, `active`, `index`, `project_id`)
VALUES
	(1,'What genders do you want to listen to?',1,3,3,1,1,1),
	(3,'What do you want to listen to?',1,2,3,1,3,1),
	(4,'What gender are you?',2,3,1,1,1,1),
	(6,'What do you want to talk about?',2,2,1,1,3,1),
	(7,'Who do you want to hear?',1,4,3,1,2,1),
	(8,'Who are you?',2,4,1,1,2,1);

/*!40000 ALTER TABLE `rw_masterui` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_masterui_header_text_loc
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_masterui_header_text_loc`;

CREATE TABLE `rw_masterui_header_text_loc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `masterui_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rw_masterui_header_text_loc_masterui_id_6f0abb51_uniq` (`masterui_id`,`localizedstring_id`),
  KEY `rw_masterui_header_text_loc_65df905c` (`masterui_id`),
  KEY `rw_masterui_header_text_loc_566c66f7` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_3e5f99fb` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `masterui_id_refs_id_5a739c30` FOREIGN KEY (`masterui_id`) REFERENCES `rw_masterui` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_masterui_header_text_loc` WRITE;
/*!40000 ALTER TABLE `rw_masterui_header_text_loc` DISABLE KEYS */;

INSERT INTO `rw_masterui_header_text_loc` (`id`, `masterui_id`, `localizedstring_id`)
VALUES
	(3,1,55),
	(2,1,56),
	(7,3,63),
	(8,4,64),
	(6,6,62),
	(4,7,60),
	(5,8,61);

/*!40000 ALTER TABLE `rw_masterui_header_text_loc` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_project
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_project`;

CREATE TABLE `rw_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `pub_date` datetime NOT NULL,
  `audio_format` varchar(50) NOT NULL,
  `auto_submit` tinyint(1) NOT NULL,
  `max_recording_length` int(11) NOT NULL,
  `listen_questions_dynamic` tinyint(1) NOT NULL,
  `speak_questions_dynamic` tinyint(1) NOT NULL,
  `sharing_url` varchar(512) NOT NULL,
  `out_of_range_url` varchar(512) NOT NULL,
  `recording_radius` int(11) DEFAULT NULL,
  `listen_enabled` tinyint(1) NOT NULL,
  `geo_listen_enabled` tinyint(1) NOT NULL,
  `speak_enabled` tinyint(1) NOT NULL,
  `geo_speak_enabled` tinyint(1) NOT NULL,
  `reset_tag_defaults_on_startup` tinyint(1) NOT NULL,
  `repeat_mode_id` int(11) DEFAULT NULL,
  `audio_stream_bitrate` varchar(3) NOT NULL,
  `files_version` varchar(16) NOT NULL,
  `files_url` varchar(512) NOT NULL,
  `ordering` varchar(16) NOT NULL,
  `demo_stream_enabled` tinyint(1) NOT NULL,
  `demo_stream_url` varchar(512) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_project_349728aa` (`repeat_mode_id`),
  CONSTRAINT `repeat_mode_id_refs_id_2c41aefb` FOREIGN KEY (`repeat_mode_id`) REFERENCES `rw_repeatmode` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_project` WRITE;
/*!40000 ALTER TABLE `rw_project` DISABLE KEYS */;

INSERT INTO `rw_project` (`id`, `name`, `latitude`, `longitude`, `pub_date`, `audio_format`, `auto_submit`, `max_recording_length`, `listen_questions_dynamic`, `speak_questions_dynamic`, `sharing_url`, `out_of_range_url`, `recording_radius`, `listen_enabled`, `geo_listen_enabled`, `speak_enabled`, `geo_speak_enabled`, `reset_tag_defaults_on_startup`, `repeat_mode_id`, `audio_stream_bitrate`, `files_version`, `files_url`, `ordering`, `demo_stream_enabled`, `demo_stream_url`)
VALUES
	(1,'Test Project',45,-59,'2011-12-06 16:06:32','mp3',1,30,0,0,'http://roundware.org/r/eid=[id]','http://scapesaudio.dyndns.org:8000/mg_outofrange.mp3',20,1,0,1,1,1,1,'128','1','http://roundware.org/webview/rw.zip','random',1,'http://scapesaudio.dyndns.org:8000/scapes1.mp3');

/*!40000 ALTER TABLE `rw_project` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_project_demo_stream_message_loc
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_project_demo_stream_message_loc`;

CREATE TABLE `rw_project_demo_stream_message_loc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rw_project_demo_stream_message_loc_project_id_2ee38bf6_uniq` (`project_id`,`localizedstring_id`),
  KEY `rw_project_demo_stream_message_loc_499df97c` (`project_id`),
  KEY `rw_project_demo_stream_message_loc_566c66f7` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_44d0ccee` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `project_id_refs_id_531a85b3` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_project_demo_stream_message_loc` WRITE;
/*!40000 ALTER TABLE `rw_project_demo_stream_message_loc` DISABLE KEYS */;

INSERT INTO `rw_project_demo_stream_message_loc` (`id`, `project_id`, `localizedstring_id`)
VALUES
	(44,1,47),
	(43,1,48);

/*!40000 ALTER TABLE `rw_project_demo_stream_message_loc` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_project_legal_agreement_loc
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_project_legal_agreement_loc`;

CREATE TABLE `rw_project_legal_agreement_loc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`,`localizedstring_id`),
  KEY `rw_project_legal_agreement_loc_499df97c` (`project_id`),
  KEY `rw_project_legal_agreement_loc_566c66f7` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_439ab8bc` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `project_id_refs_id_64920ca3` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_project_legal_agreement_loc` WRITE;
/*!40000 ALTER TABLE `rw_project_legal_agreement_loc` DISABLE KEYS */;

INSERT INTO `rw_project_legal_agreement_loc` (`id`, `project_id`, `localizedstring_id`)
VALUES
	(108,1,53),
	(109,1,54);

/*!40000 ALTER TABLE `rw_project_legal_agreement_loc` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_project_out_of_range_message_loc
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_project_out_of_range_message_loc`;

CREATE TABLE `rw_project_out_of_range_message_loc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`,`localizedstring_id`),
  KEY `rw_project_out_of_range_message_loc_499df97c` (`project_id`),
  KEY `rw_project_out_of_range_message_loc_566c66f7` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_5806fa4f` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `project_id_refs_id_5b6323d0` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_project_out_of_range_message_loc` WRITE;
/*!40000 ALTER TABLE `rw_project_out_of_range_message_loc` DISABLE KEYS */;

INSERT INTO `rw_project_out_of_range_message_loc` (`id`, `project_id`, `localizedstring_id`)
VALUES
	(111,1,47),
	(110,1,48);

/*!40000 ALTER TABLE `rw_project_out_of_range_message_loc` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_project_sharing_message_loc
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_project_sharing_message_loc`;

CREATE TABLE `rw_project_sharing_message_loc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`,`localizedstring_id`),
  KEY `rw_project_sharing_message_loc_499df97c` (`project_id`),
  KEY `rw_project_sharing_message_loc_566c66f7` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_671f4b1a` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `project_id_refs_id_16bb9cd5` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_project_sharing_message_loc` WRITE;
/*!40000 ALTER TABLE `rw_project_sharing_message_loc` DISABLE KEYS */;

INSERT INTO `rw_project_sharing_message_loc` (`id`, `project_id`, `localizedstring_id`)
VALUES
	(108,1,49),
	(109,1,50);

/*!40000 ALTER TABLE `rw_project_sharing_message_loc` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_repeatmode
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_repeatmode`;

CREATE TABLE `rw_repeatmode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mode` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_repeatmode` WRITE;
/*!40000 ALTER TABLE `rw_repeatmode` DISABLE KEYS */;

INSERT INTO `rw_repeatmode` (`id`, `mode`)
VALUES
	(1,'stop'),
	(2,'continuous');

/*!40000 ALTER TABLE `rw_repeatmode` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_selectionmethod
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_selectionmethod`;

CREATE TABLE `rw_selectionmethod` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `data` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_selectionmethod` WRITE;
/*!40000 ALTER TABLE `rw_selectionmethod` DISABLE KEYS */;

INSERT INTO `rw_selectionmethod` (`id`, `name`, `data`)
VALUES
	(1,'single',''),
	(2,'multi',''),
	(3,'multi_at_least_one','');

/*!40000 ALTER TABLE `rw_selectionmethod` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_session
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_session`;

CREATE TABLE `rw_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` varchar(36) DEFAULT NULL,
  `starttime` datetime NOT NULL,
  `stoptime` datetime DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  `language_id` int(11) DEFAULT NULL,
  `client_type` varchar(128) DEFAULT NULL,
  `client_system` varchar(128) DEFAULT NULL,
  `demo_stream_enabled` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_session_499df97c` (`project_id`),
  KEY `rw_session_7ab48146` (`language_id`),
  CONSTRAINT `language_id_refs_id_50dae3ca` FOREIGN KEY (`language_id`) REFERENCES `rw_language` (`id`),
  CONSTRAINT `project_id_refs_id_52c90e52` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_session` WRITE;
/*!40000 ALTER TABLE `rw_session` DISABLE KEYS */;

INSERT INTO `rw_session` (`id`, `device_id`, `starttime`, `stoptime`, `project_id`, `language_id`, `client_type`, `client_system`, `demo_stream_enabled`)
VALUES
	(-10,'session-for-admin-uploads','2014-01-25 13:44:49',NULL,1,1,NULL,NULL,0),
	(2891,'e87e8199-01c9-4151-ae96-d704b61323e7','2012-08-27 00:11:48','2012-08-27 00:15:52',1,1,NULL,NULL,0);

/*!40000 ALTER TABLE `rw_session` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_speaker
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_speaker`;

CREATE TABLE `rw_speaker` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `activeyn` tinyint(1) NOT NULL,
  `code` varchar(10) NOT NULL,
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `maxdistance` int(11) NOT NULL,
  `mindistance` int(11) NOT NULL,
  `maxvolume` double NOT NULL,
  `minvolume` double NOT NULL,
  `uri` varchar(200) NOT NULL,
  `backupuri` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_speaker_499df97c` (`project_id`),
  CONSTRAINT `project_id_refs_id_4055f3f7` FOREIGN KEY (`project_id`) REFERENCES `rw_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_speaker` WRITE;
/*!40000 ALTER TABLE `rw_speaker` DISABLE KEYS */;

INSERT INTO `rw_speaker` (`id`, `project_id`, `activeyn`, `code`, `latitude`, `longitude`, `maxdistance`, `mindistance`, `maxvolume`, `minvolume`, `uri`, `backupuri`)
VALUES
	(1,1,1,'1',42.132059,-99.103302,20000,10000,0.5,0.5,'http://scapesaudio.dyndns.org:8000/scapes1.mp3','http://scapesaudio.dyndns.org:8000/scapes1.mp3');

/*!40000 ALTER TABLE `rw_speaker` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_tag
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_tag`;

CREATE TABLE `rw_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_category_id` int(11) NOT NULL,
  `value` longtext NOT NULL,
  `description` longtext NOT NULL,
  `data` longtext,
  `filter` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_tag_1f0789df` (`tag_category_id`),
  CONSTRAINT `tag_category_id_refs_id_194541f7` FOREIGN KEY (`tag_category_id`) REFERENCES `rw_tagcategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_tag` WRITE;
/*!40000 ALTER TABLE `rw_tag` DISABLE KEYS */;

INSERT INTO `rw_tag` (`id`, `tag_category_id`, `value`, `description`, `data`, `filter`)
VALUES
	(3,3,'male','male','','--'),
	(4,3,'female','female','','--'),
	(5,2,'Why RW?','Why are you using Roundware?\r\n','','--'),
	(8,4,'Artist','Artist','','--'),
	(9,4,'Visitor','Visitor','','--'),
	(21,6,'feedback','Leave feedback','','--'),
	(22,2,'respond','Respond to something you\'ve heard.','','--'),
	(23,4,'curator','curator','class=tag-one','--'),
	(24,7,'recent','recent','','_ten_most_recent_days'),
	(25,7,'nearby','nearby','','_within_10km');

/*!40000 ALTER TABLE `rw_tag` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_tag_loc_description
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_tag_loc_description`;

CREATE TABLE `rw_tag_loc_description` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rw_tag_loc_description_tag_id_b1f7076_uniq` (`tag_id`,`localizedstring_id`),
  KEY `rw_tag_loc_description_5659cca2` (`tag_id`),
  KEY `rw_tag_loc_description_f2fd4c16` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_20d1f27d` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `tag_id_refs_id_f0c4aaf` FOREIGN KEY (`tag_id`) REFERENCES `rw_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_tag_loc_description` WRITE;
/*!40000 ALTER TABLE `rw_tag_loc_description` DISABLE KEYS */;

INSERT INTO `rw_tag_loc_description` (`id`, `tag_id`, `localizedstring_id`)
VALUES
	(5,24,58),
	(4,25,59);

/*!40000 ALTER TABLE `rw_tag_loc_description` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_tag_loc_msg
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_tag_loc_msg`;

CREATE TABLE `rw_tag_loc_msg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_id` int(11) NOT NULL,
  `localizedstring_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_id` (`tag_id`,`localizedstring_id`),
  KEY `rw_tag_loc_msg_3747b463` (`tag_id`),
  KEY `rw_tag_loc_msg_566c66f7` (`localizedstring_id`),
  CONSTRAINT `localizedstring_id_refs_id_2eea3d62` FOREIGN KEY (`localizedstring_id`) REFERENCES `rw_localizedstring` (`id`),
  CONSTRAINT `tag_id_refs_id_1e5d0d1e` FOREIGN KEY (`tag_id`) REFERENCES `rw_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_tag_loc_msg` WRITE;
/*!40000 ALTER TABLE `rw_tag_loc_msg` DISABLE KEYS */;

INSERT INTO `rw_tag_loc_msg` (`id`, `tag_id`, `localizedstring_id`)
VALUES
	(62,3,5),
	(63,3,6),
	(65,4,7),
	(64,4,8),
	(66,5,9),
	(67,5,10),
	(69,8,15),
	(68,8,16),
	(70,9,17),
	(71,9,18),
	(72,21,41),
	(73,21,42),
	(74,22,43),
	(75,22,44),
	(76,23,57),
	(77,24,58),
	(61,25,59);

/*!40000 ALTER TABLE `rw_tag_loc_msg` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_tag_relationships
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_tag_relationships`;

CREATE TABLE `rw_tag_relationships` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_tag_id` int(11) NOT NULL,
  `to_tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rw_tag_relationships_from_tag_id_12e376df_uniq` (`from_tag_id`,`to_tag_id`),
  KEY `rw_tag_relationships_335d9ea3` (`from_tag_id`),
  KEY `rw_tag_relationships_27bf15b0` (`to_tag_id`),
  CONSTRAINT `from_tag_id_refs_id_5da427d` FOREIGN KEY (`from_tag_id`) REFERENCES `rw_tag` (`id`),
  CONSTRAINT `to_tag_id_refs_id_5da427d` FOREIGN KEY (`to_tag_id`) REFERENCES `rw_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_tag_relationships` WRITE;
/*!40000 ALTER TABLE `rw_tag_relationships` DISABLE KEYS */;

INSERT INTO `rw_tag_relationships` (`id`, `from_tag_id`, `to_tag_id`)
VALUES
	(90,3,3),
	(106,3,4),
	(108,3,5),
	(110,3,8),
	(112,3,9),
	(114,3,21),
	(116,3,22),
	(118,3,23),
	(105,4,3),
	(107,5,3),
	(109,8,3),
	(111,9,3),
	(113,21,3),
	(115,22,3),
	(117,23,3);

/*!40000 ALTER TABLE `rw_tag_relationships` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_tagcategory
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_tagcategory`;

CREATE TABLE `rw_tagcategory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `data` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_tagcategory` WRITE;
/*!40000 ALTER TABLE `rw_tagcategory` DISABLE KEYS */;

INSERT INTO `rw_tagcategory` (`id`, `name`, `data`)
VALUES
	(2,'question',''),
	(3,'gender',''),
	(4,'usertype',''),
	(6,'admin',''),
	(7,'channel','');

/*!40000 ALTER TABLE `rw_tagcategory` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_uimapping
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_uimapping`;

CREATE TABLE `rw_uimapping` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `master_ui_id` int(11) NOT NULL,
  `index` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  `default` tinyint(1) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rw_uimapping_4e9ac10e` (`master_ui_id`),
  KEY `rw_uimapping_3747b463` (`tag_id`),
  CONSTRAINT `master_ui_id_refs_id_1a9c98a6` FOREIGN KEY (`master_ui_id`) REFERENCES `rw_masterui` (`id`),
  CONSTRAINT `tag_id_refs_id_38b3d21` FOREIGN KEY (`tag_id`) REFERENCES `rw_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_uimapping` WRITE;
/*!40000 ALTER TABLE `rw_uimapping` DISABLE KEYS */;

INSERT INTO `rw_uimapping` (`id`, `master_ui_id`, `index`, `tag_id`, `default`, `active`)
VALUES
	(1,1,2,3,1,1),
	(2,1,1,4,1,1),
	(5,3,1,5,1,1),
	(8,4,2,3,1,1),
	(9,4,1,4,0,1),
	(12,6,1,5,1,1),
	(15,7,1,8,1,1),
	(16,7,2,9,1,1),
	(17,8,2,9,0,1),
	(53,8,2,8,1,1),
	(54,3,2,22,1,1),
	(55,6,2,22,0,1);

/*!40000 ALTER TABLE `rw_uimapping` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_uimode
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_uimode`;

CREATE TABLE `rw_uimode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `data` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOCK TABLES `rw_uimode` WRITE;
/*!40000 ALTER TABLE `rw_uimode` DISABLE KEYS */;

INSERT INTO `rw_uimode` (`id`, `name`, `data`)
VALUES
	(1,'listen',''),
	(2,'speak','');

/*!40000 ALTER TABLE `rw_uimode` ENABLE KEYS */;
UNLOCK TABLES;


# Dump of table rw_vote
# ------------------------------------------------------------

DROP TABLE IF EXISTS `rw_vote`;

CREATE TABLE `rw_vote` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` int(11) DEFAULT NULL,
  `session_id` int(11) NOT NULL,
  `asset_id` int(11) NOT NULL,
  `type` varchar(16) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `rw_vote_6b4dc4c3` (`session_id`),
  KEY `rw_vote_7696bc7d` (`asset_id`),
  CONSTRAINT `asset_id_refs_id_624fda90` FOREIGN KEY (`asset_id`) REFERENCES `rw_asset` (`id`),
  CONSTRAINT `session_id_refs_id_4fb62cee` FOREIGN KEY (`session_id`) REFERENCES `rw_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
