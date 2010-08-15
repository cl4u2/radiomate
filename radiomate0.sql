-- phpMyAdmin SQL Dump
-- version 3.3.4
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Aug 15, 2010 at 04:47 PM
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

--
-- Dumping data for table `compilation`
--

-- --------------------------------------------------------

--
-- Table structure for table `mediafiles`
--

CREATE TABLE IF NOT EXISTS `mediafiles` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user` varchar(60) DEFAULT NULL,
  `path` mediumtext NOT NULL,
  `type` enum('audio','video','other') NOT NULL DEFAULT 'audio',
  `title` varchar(1000) DEFAULT NULL,
  `author` varchar(1000) DEFAULT NULL,
  `album` varchar(1000) DEFAULT NULL,
  `genre` varchar(1000) DEFAULT NULL,
  `year` varchar(250) DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `comment` mediumtext,
  `license` varchar(1000) DEFAULT NULL,
  `tags` mediumtext,
  PRIMARY KEY (`id`),
  KEY `user` (`user`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

--
-- Dumping data for table `mediafiles`
--


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

--
-- Dumping data for table `playlistowners`
--


-- --------------------------------------------------------

--
-- Table structure for table `playlists`
--

CREATE TABLE IF NOT EXISTS `playlists` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `creator` varchar(60) DEFAULT NULL,
  `title` varchar(1000) DEFAULT NULL,
  `description` mediumtext,
  `comment` mediumtext,
  `tags` mediumtext,
  `private` tinyint(1) NOT NULL DEFAULT '0',
  `random` tinyint(1) NOT NULL DEFAULT '0',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `id` (`id`),
  KEY `creator` (`creator`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

--
-- Dumping data for table `playlists`
--


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

--
-- Dumping data for table `playlistviewers`
--


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
  `canManageTimetable` tinyint(1) NOT NULL,
  `fixedSlotTimes` tinyint(1) NOT NULL,
  `changeTimeBeforeTransmission` int(11) NOT NULL,
  `canCreateTestSlot` tinyint(1) NOT NULL,
  `fixedSlotTimesList` mediumtext,
  PRIMARY KEY (`rolename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`rolename`, `canManageRoles`, `canManageUsers`, `canManageAllPlaylists`, `canRegisterFiles`, `canManageRegisteredFiles`, `canManageTimetable`, `fixedSlotTimes`, `changeTimeBeforeTransmission`, `canCreateTestSlot`, `fixedSlotTimesList`) VALUES
('admin', 1, 1, 1, 1, 1, 1, 1, -1, 1, '60,120');

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
  `fallbackplaylist` bigint(20) unsigned DEFAULT NULL,
  `canceled` tinyint(1) NOT NULL DEFAULT '0',
  `archived` bigint(20) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `creator` (`creator`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

--
-- Dumping data for table `timeslots`
--


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
-- Dumping data for table `users`
--

INSERT INTO `users` (`name`, `password`, `role`, `displayname`) VALUES
('foobar', 'e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4', 'admin', 'Foo Bar');

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
