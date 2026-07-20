-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jul 19, 2026 at 05:00 PM
-- Server version: 8.3.0
-- PHP Version: 8.2.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `app_mikrotik`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_group`
--

INSERT INTO `auth_group` (`id`, `name`) VALUES
(1, 'asistente_administrativo'),
(2, 'soporte');

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_group_id_b120cbf9` (`group_id`),
  KEY `auth_group_permissions_permission_id_84c5c92e` (`permission_id`)
) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_group_permissions`
--

INSERT INTO `auth_group_permissions` (`id`, `group_id`, `permission_id`) VALUES
(1, 1, 25),
(2, 1, 26),
(3, 1, 27),
(4, 1, 28),
(5, 1, 29),
(6, 1, 30),
(7, 1, 31),
(8, 1, 32),
(9, 1, 33),
(10, 1, 34),
(11, 1, 35),
(12, 1, 36),
(13, 1, 37),
(14, 1, 38),
(15, 1, 39),
(16, 1, 40),
(17, 1, 41),
(18, 1, 42),
(19, 1, 43),
(20, 1, 44),
(21, 2, 25),
(22, 2, 26),
(23, 2, 27),
(24, 2, 28);

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id_2f476e4b` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 3, 'add_permission'),
(6, 'Can change permission', 3, 'change_permission'),
(7, 'Can delete permission', 3, 'delete_permission'),
(8, 'Can view permission', 3, 'view_permission'),
(9, 'Can add group', 2, 'add_group'),
(10, 'Can change group', 2, 'change_group'),
(11, 'Can delete group', 2, 'delete_group'),
(12, 'Can view group', 2, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add logs', 9, 'add_logs'),
(26, 'Can change logs', 9, 'change_logs'),
(27, 'Can delete logs', 9, 'delete_logs'),
(28, 'Can view logs', 9, 'view_logs'),
(29, 'Can add factura', 8, 'add_factura'),
(30, 'Can change factura', 8, 'change_factura'),
(31, 'Can delete factura', 8, 'delete_factura'),
(32, 'Can view factura', 8, 'view_factura'),
(33, 'Can add plan', 11, 'add_plan'),
(34, 'Can change plan', 11, 'change_plan'),
(35, 'Can delete plan', 11, 'delete_plan'),
(36, 'Can view plan', 11, 'view_plan'),
(37, 'Can add pago', 10, 'add_pago'),
(38, 'Can change pago', 10, 'change_pago'),
(39, 'Can delete pago', 10, 'delete_pago'),
(40, 'Can view pago', 10, 'view_pago'),
(41, 'Can add cliente', 7, 'add_cliente'),
(42, 'Can change cliente', 7, 'change_cliente'),
(43, 'Can delete cliente', 7, 'delete_cliente'),
(44, 'Can view cliente', 7, 'view_cliente'),
(45, 'Can add configuracion morosidad', 12, 'add_configuracionmorosidad'),
(46, 'Can change configuracion morosidad', 12, 'change_configuracionmorosidad'),
(47, 'Can delete configuracion morosidad', 12, 'delete_configuracionmorosidad'),
(48, 'Can view configuracion morosidad', 12, 'view_configuracionmorosidad'),
(49, 'Can add seguimiento morosidad', 13, 'add_seguimientomorosidad'),
(50, 'Can change seguimiento morosidad', 13, 'change_seguimientomorosidad'),
(51, 'Can delete seguimiento morosidad', 13, 'delete_seguimientomorosidad'),
(52, 'Can view seguimiento morosidad', 13, 'view_seguimientomorosidad');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$1200000$mlvYeiAdd9jkhmOcIzvzUi$8TCA9d3h7BtV4v+vvvID4cs3eLEdbT4HRyVSJbBbavA=', '2026-07-19 12:37:02.791124', 1, 'admin', '', '', '', 1, 1, '2026-05-25 21:26:02.958922'),
(2, 'pbkdf2_sha256$1200000$dB7kjlgpZvvb7YS7Gvloya$69BJ5I7iNF0bgfaS2gpZEV2fSzLRWtHfSXJOUBD3bDI=', '2026-06-17 14:52:27.106474', 0, 'cajero', 'Sr. Cajero', 'Cajin', 'cajero@gmail.com', 0, 1, '2026-06-02 00:21:58.000000'),
(3, 'pbkdf2_sha256$1200000$x8fDmCj7wsanWSXysTL1I5$Kx+NuVPs3nWvs8MOb3/RpwBoJIvTRFnJOcPgWhYcNFE=', '2026-06-17 14:52:48.305331', 0, 'soporte', 'Sr. Soporte', 'Soportin', 'soporte@gmail.com', 0, 1, '2026-06-02 00:23:19.000000'),
(4, '!F6tXB6FKHqJJ6vLSYrhQYLiI23Qs5bo8Rm7RIHAD', NULL, 0, 'Sistema', '', '', '', 1, 1, '2026-06-14 14:02:31.000000');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_user_id_6a12ed8b` (`user_id`),
  KEY `auth_user_groups_group_id_97559544` (`group_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `auth_user_groups`
--

INSERT INTO `auth_user_groups` (`id`, `user_id`, `group_id`) VALUES
(1, 2, 1),
(2, 3, 2),
(3, 4, 1),
(4, 4, 2);

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_user_id_a95ead1b` (`user_id`),
  KEY `auth_user_user_permissions_permission_id_1fbb5f2c` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `control_morosidad_configuracionmorosidad`
--

DROP TABLE IF EXISTS `control_morosidad_configuracionmorosidad`;
CREATE TABLE IF NOT EXISTS `control_morosidad_configuracionmorosidad` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `diasGracia` smallint UNSIGNED NOT NULL,
  `diaCobroMensual` smallint UNSIGNED NOT NULL,
  PRIMARY KEY (`id`)
) ;

--
-- Dumping data for table `control_morosidad_configuracionmorosidad`
--

INSERT INTO `control_morosidad_configuracionmorosidad` (`id`, `diasGracia`, `diaCobroMensual`) VALUES
(1, 3, 1);

-- --------------------------------------------------------

--
-- Table structure for table `core_cliente`
--

DROP TABLE IF EXISTS `core_cliente`;
CREATE TABLE IF NOT EXISTS `core_cliente` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `cedula` varchar(9) NOT NULL,
  `celular` varchar(12) NOT NULL,
  `direccion` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `direccionIP` char(39) NOT NULL,
  `saldo` decimal(10,2) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `borrado` tinyint(1) NOT NULL,
  `idPlan_id` bigint NOT NULL,
  `fechaRegistro` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_cliente_idPlan_id_6eca7a1d` (`idPlan_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3159 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `core_factura`
--

DROP TABLE IF EXISTS `core_factura`;
CREATE TABLE IF NOT EXISTS `core_factura` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `montoUSD` decimal(10,2) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `idCliente_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_factura_idCliente_id_64b764a2` (`idCliente_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `core_logs`
--

DROP TABLE IF EXISTS `core_logs`;
CREATE TABLE IF NOT EXISTS `core_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `modulo` varchar(30) NOT NULL,
  `mensaje` longtext NOT NULL,
  `error` tinyint(1) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `idPersonal_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_logs_idPersonal_id_50adcf8a` (`idPersonal_id`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `core_pago`
--

DROP TABLE IF EXISTS `core_pago`;
CREATE TABLE IF NOT EXISTS `core_pago` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `montoUSD` decimal(10,2) NOT NULL,
  `tasa` decimal(10,2) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `comprobante` varchar(100) DEFAULT NULL,
  `idCliente_id` bigint NOT NULL,
  `idPersonal_id` int NOT NULL,
  `metodo` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_pago_idCliente_id_848ebb17` (`idCliente_id`),
  KEY `core_pago_idPersonal_id_aed299e1` (`idPersonal_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `core_plan`
--

DROP TABLE IF EXISTS `core_plan`;
CREATE TABLE IF NOT EXISTS `core_plan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `plan` varchar(20) NOT NULL,
  `precioUSD` decimal(10,2) NOT NULL,
  `velocidad_subida` decimal(10,2) NOT NULL,
  `velocidad_bajada` decimal(10,2) NOT NULL,
  `borrado` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `core_plan`
--

INSERT INTO `core_plan` (`id`, `plan`, `precioUSD`, `velocidad_subida`, `velocidad_bajada`, `borrado`) VALUES
(1, 'Basico', 25.00, 5.00, 5.00, 0);

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'group'),
(3, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(6, 'sessions', 'session'),
(7, 'core', 'cliente'),
(8, 'core', 'factura'),
(9, 'core', 'logs'),
(10, 'core', 'pago'),
(11, 'core', 'plan'),
(12, 'control_morosidad', 'configuracionmorosidad'),
(13, 'control_morosidad', 'seguimientomorosidad');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-05-20 04:55:12.409324'),
(2, 'auth', '0001_initial', '2026-05-20 04:55:12.965385'),
(3, 'admin', '0001_initial', '2026-05-20 04:55:13.184227'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-05-20 04:55:13.191785'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-05-20 04:55:13.208642'),
(6, 'contenttypes', '0002_remove_content_type_name', '2026-05-20 04:55:13.293540'),
(7, 'auth', '0002_alter_permission_name_max_length', '2026-05-20 04:55:13.360907'),
(8, 'auth', '0003_alter_user_email_max_length', '2026-05-20 04:55:13.408220'),
(9, 'auth', '0004_alter_user_username_opts', '2026-05-20 04:55:13.419334'),
(10, 'auth', '0005_alter_user_last_login_null', '2026-05-20 04:55:13.467490'),
(11, 'auth', '0006_require_contenttypes_0002', '2026-05-20 04:55:13.468495'),
(12, 'auth', '0007_alter_validators_add_error_messages', '2026-05-20 04:55:13.478037'),
(13, 'auth', '0008_alter_user_username_max_length', '2026-05-20 04:55:13.534756'),
(14, 'auth', '0009_alter_user_last_name_max_length', '2026-05-20 04:55:13.575149'),
(15, 'auth', '0010_alter_group_name_max_length', '2026-05-20 04:55:13.611981'),
(16, 'auth', '0011_update_proxy_permissions', '2026-05-20 04:55:13.624743'),
(17, 'auth', '0012_alter_user_first_name_max_length', '2026-05-20 04:55:13.678782'),
(18, 'sessions', '0001_initial', '2026-05-20 04:55:13.724703'),
(19, 'core', '0001_initial', '2026-05-20 05:23:15.746635'),
(20, 'core', '0002_alter_pago_fecha', '2026-05-26 03:32:56.280430'),
(21, 'core', '0003_remove_pago_pagousd_pago_metodo_alter_cliente_estado', '2026-05-26 04:22:34.775183'),
(22, 'core', '0004_alter_pago_tasa', '2026-05-26 04:35:10.748494'),
(23, 'core', '0005_alter_pago_comprobante', '2026-05-27 15:42:51.070511'),
(24, 'core', '0006_alter_pago_comprobante', '2026-05-29 01:47:59.809708'),
(25, 'core', '0007_alter_cliente_cedula_alter_cliente_direccionip_and_more', '2026-06-01 14:59:34.702295'),
(26, 'core', '0008_alter_cliente_estado', '2026-06-01 14:59:34.708871'),
(27, 'core', '0009_alter_pago_comprobante', '2026-06-01 14:59:34.760175'),
(28, 'core', '0010_cliente_fecharegistro', '2026-06-04 02:56:27.953811'),
(29, 'control_morosidad', '0001_initial', '2026-06-23 00:06:37.272513');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('l36zq4b1webt735vmu21juntyuv8utz5', '.eJxVjMsOwiAQAP9lz4awLFTo0Xu_oVnYIlUDSR8n47-bJj3odWYybxh538q4r9MyzgI9IFx-WeT0nOoh5MH13lRqdVvmqI5EnXZVQ5PpdTvbv0HhtUAPXpLNOknqcrQGQ0ZmCihIxpEmrQ11rnMm-uDsVQuSZx9yNtlpQknw-QLSizb_:1wlUVi:cclfYAkm5FqHP2QcdF4tygHoVVm342mBx9lMGAIYTkA', '2026-08-02 12:37:02.792594');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
