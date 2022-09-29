-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 29, 2022 at 09:15 AM
-- Server version: 10.4.19-MariaDB
-- PHP Version: 8.0.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tera`
--

-- --------------------------------------------------------

--
-- Table structure for table `abnorms`
--

CREATE TABLE `abnorms` (
  `id` int(20) NOT NULL,
  `name` varchar(127) NOT NULL,
  `tooltip` varchar(1000) NOT NULL,
  `icon` varchar(127) NOT NULL,
  `type` varchar(127) NOT NULL,
  `mobSize` varchar(10) NOT NULL,
  `kind` int(5) NOT NULL,
  `level` int(4) NOT NULL,
  `property` int(10) NOT NULL,
  `category` int(15) NOT NULL,
  `skillCategory` int(15) NOT NULL,
  `time` int(127) NOT NULL,
  `priority` int(1) NOT NULL,
  `infinity` int(1) NOT NULL,
  `realtime` int(1) NOT NULL,
  `isBuff` int(1) NOT NULL,
  `isShow` int(1) NOT NULL,
  `isStance` int(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `abnorms`
--

--
-- Indexes for dumped tables
--

--
-- Indexes for table `abnorms`
--
ALTER TABLE `abnorms`
  ADD PRIMARY KEY (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
