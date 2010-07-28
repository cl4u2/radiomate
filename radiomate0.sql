-- phpMyAdmin SQL Dump
-- version 3.3.3
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 03, 2010 at 03:06 PM
-- Server version: 5.1.47
-- PHP Version: 5.3.2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `radiomate0`
--

-- --------------------------------------------------------

--
-- Table structure for table `compilation`
--

CREATE TABLE IF NOT EXISTS `compilation` (
  `playlist` bigint(20) unsigned NOT NULL,
  `mediafile` bigint(20) unsigned NOT NULL,
  `position` int(10) unsigned NOT NULL,
  PRIMARY KEY (`playlist`,`mediafile`,`position`),
  KEY `mediafile` (`mediafile`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `mediafiles`
--

CREATE TABLE IF NOT EXISTS `mediafiles` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` varchar(60) NOT NULL,
  `path` mediumtext NOT NULL,
  `type` enum('audio','video','other') NOT NULL DEFAULT 'audio',
  `title` varchar(1000) DEFAULT NULL,
  `author` varchar(1000) DEFAULT NULL,
  `album` varchar(1000) DEFAULT NULL,
  `genre` varchar(1000) DEFAULT NULL,
  `year` varchar(250) DEFAULT NULL,
  `comment` mediumtext,
  `license` varchar(1000) DEFAULT NULL,
  `tags` mediumtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `playlistowners`
--

CREATE TABLE IF NOT EXISTS `playlistowners` (
  `playlist` bigint(20) unsigned NOT NULL,
  `user` varchar(60) NOT NULL,
  PRIMARY KEY (`playlist`,`user`),
  KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `playlists`
--

CREATE TABLE IF NOT EXISTS `playlists` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `creator` varchar(60) NOT NULL,
  `fallback` tinyint(1) NOT NULL DEFAULT '0',
  `title` varchar(1000) DEFAULT NULL,
  `description` mediumtext,
  `comment` mediumtext,
  `tags` mediumtext,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `id` (`id`),
  KEY `creator` (`creator`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `playlistviewers`
--

CREATE TABLE IF NOT EXISTS `playlistviewers` (
  `playlist` bigint(20) unsigned NOT NULL,
  `user` varchar(60) NOT NULL,
  PRIMARY KEY (`playlist`,`user`),
  KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE IF NOT EXISTS `roles` (
  `rolename` varchar(60) NOT NULL,
  `canManageRoles` tinyint(1) NOT NULL,
  `canManageUsers` tinyint(1) NOT NULL,
  `canManageAllPlaylists` tinyint(1) NOT NULL,
  `canRegisterFiles` tinyint(1) NOT NULL,
  `canManageRegisteredFiles` tinyint(1) NOT NULL,
  `canSearchRegisteredFiles` tinyint(1) NOT NULL,
  `canManageTimetable` tinyint(1) NOT NULL,
  `fixedSlotTime` tinyint(1) NOT NULL,
  `changeTimeBeforeTransmission` int(11) NOT NULL,
  `canCreateTestMountpoint` tinyint(1) NOT NULL,
  `canListNetcasts` tinyint(1) NOT NULL,
  `fixedSlotTimesList` mediumtext,
  PRIMARY KEY (`rolename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `timeslots`
--

CREATE TABLE IF NOT EXISTS `timeslots` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `creator` varchar(60) NOT NULL,
  `slottype` varchar(60) NOT NULL,
  `beginningtime` datetime NOT NULL,
  `endingtime` datetime NOT NULL,
  `title` varchar(1000) DEFAULT NULL,
  `description` mediumtext,
  `comment` mediumtext,
  `tags` mediumtext,
  `slotparameters` mediumtext,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `creator` (`creator`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `name` varchar(60) NOT NULL,
  `password` varchar(60) NOT NULL,
  `role` varchar(60) NOT NULL,
  `displayname` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `compilation`
--
ALTER TABLE `compilation`
  ADD CONSTRAINT `compilation_ibfk_1` FOREIGN KEY (`playlist`) REFERENCES `playlists` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `compilation_ibfk_2` FOREIGN KEY (`mediafile`) REFERENCES `mediafiles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `mediafiles`
--
ALTER TABLE `mediafiles`
  ADD CONSTRAINT `mediafiles_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`name`) ON DELETE NO ACTION ON UPDATE CASCADE;

--
-- Constraints for table `playlistowners`
--
ALTER TABLE `playlistowners`
  ADD CONSTRAINT `playlistowners_ibfk_1` FOREIGN KEY (`playlist`) REFERENCES `playlists` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `playlistowners_ibfk_2` FOREIGN KEY (`user`) REFERENCES `users` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `playlists`
--
ALTER TABLE `playlists`
  ADD CONSTRAINT `playlists_ibfk_1` FOREIGN KEY (`creator`) REFERENCES `users` (`name`) ON DELETE NO ACTION ON UPDATE CASCADE;

--
-- Constraints for table `playlistviewers`
--
ALTER TABLE `playlistviewers`
  ADD CONSTRAINT `playlistviewers_ibfk_1` FOREIGN KEY (`user`) REFERENCES `users` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `playlistviewers_ibfk_2` FOREIGN KEY (`playlist`) REFERENCES `playlists` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `timeslots`
--
ALTER TABLE `timeslots`
  ADD CONSTRAINT `timeslots_ibfk_1` FOREIGN KEY (`creator`) REFERENCES `users` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role`) REFERENCES `roles` (`rolename`) ON DELETE NO ACTION ON UPDATE CASCADE;
