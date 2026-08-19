-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: hotel_db
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.24.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `CLIENTE`
--

DROP TABLE IF EXISTS `CLIENTE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CLIENTE` (
  `id_cliente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `documento_identidad` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pais_origen` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `documento_identidad` (`documento_identidad`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `EMPLEADO`
--

DROP TABLE IF EXISTS `EMPLEADO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EMPLEADO` (
  `id_empleado` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `puesto` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_contratacion` date NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_empleado`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HABITACION`
--

DROP TABLE IF EXISTS `HABITACION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HABITACION` (
  `id_habitacion` int unsigned NOT NULL AUTO_INCREMENT,
  `codigo_sede` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `region` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `numero_habitacion` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `piso` tinyint unsigned NOT NULL,
  `tipo_habitacion` enum('INDIVIDUAL','DOBLE','TRIPLE','SUITE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `capacidad` tinyint unsigned NOT NULL,
  `precio_noche` decimal(10,2) NOT NULL,
  `estado_actual` enum('DISPONIBLE','RESERVADA','OCUPADA','LIMPIEZA','MANTENIMIENTO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'DISPONIBLE',
  `activa` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_habitacion`),
  UNIQUE KEY `uq_habitacion_sede_numero` (`codigo_sede`,`numero_habitacion`),
  CONSTRAINT `chk_habitacion_capacidad` CHECK ((`capacidad` > 0)),
  CONSTRAINT `chk_habitacion_piso` CHECK ((`piso` > 0)),
  CONSTRAINT `chk_habitacion_precio` CHECK ((`precio_noche` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LOG_HABITACION`
--

DROP TABLE IF EXISTS `LOG_HABITACION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LOG_HABITACION` (
  `id_log` int unsigned NOT NULL AUTO_INCREMENT,
  `id_habitacion` int unsigned NOT NULL,
  `id_empleado` int unsigned NOT NULL,
  `estado_anterior` enum('DISPONIBLE','RESERVADA','OCUPADA','LIMPIEZA','MANTENIMIENTO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado_nuevo` enum('DISPONIBLE','RESERVADA','OCUPADA','LIMPIEZA','MANTENIMIENTO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_cambio` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `motivo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_log`),
  KEY `fk_log_habitacion` (`id_habitacion`),
  KEY `fk_log_empleado` (`id_empleado`),
  CONSTRAINT `fk_log_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_log_habitacion` FOREIGN KEY (`id_habitacion`) REFERENCES `HABITACION` (`id_habitacion`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_log_estado` CHECK ((`estado_anterior` <> `estado_nuevo`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PAGO`
--

DROP TABLE IF EXISTS `PAGO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PAGO` (
  `id_pago` int unsigned NOT NULL AUTO_INCREMENT,
  `id_reserva` int unsigned NOT NULL,
  `id_empleado` int unsigned NOT NULL,
  `fecha_pago` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `monto` decimal(10,2) NOT NULL,
  `metodo_pago` enum('EFECTIVO','TARJETA','TRANSFERENCIA') COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` enum('PENDIENTE','APROBADO','RECHAZADO','ANULADO') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDIENTE',
  `referencia` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_pago`),
  UNIQUE KEY `referencia` (`referencia`),
  KEY `fk_pago_reserva` (`id_reserva`),
  KEY `fk_pago_empleado` (`id_empleado`),
  CONSTRAINT `fk_pago_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_pago_reserva` FOREIGN KEY (`id_reserva`) REFERENCES `RESERVA` (`id_reserva`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_pago_monto` CHECK ((`monto` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `RESERVA`
--

DROP TABLE IF EXISTS `RESERVA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RESERVA` (
  `id_reserva` int unsigned NOT NULL AUTO_INCREMENT,
  `id_cliente` int unsigned NOT NULL,
  `id_habitacion` int unsigned NOT NULL,
  `id_empleado` int unsigned NOT NULL,
  `fecha_reserva` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_entrada` date NOT NULL,
  `fecha_salida` date NOT NULL,
  `numero_huespedes` tinyint unsigned NOT NULL,
  `canal_reserva` enum('WEB','TELEFONO','PRESENCIAL','AGENCIA') COLLATE utf8mb4_unicode_ci NOT NULL,
  `estado` enum('PENDIENTE','CONFIRMADA','CHECK_IN','CHECK_OUT','CANCELADA') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDIENTE',
  `monto_total` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_reserva`),
  KEY `fk_reserva_cliente` (`id_cliente`),
  KEY `fk_reserva_habitacion` (`id_habitacion`),
  KEY `fk_reserva_empleado` (`id_empleado`),
  CONSTRAINT `fk_reserva_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `CLIENTE` (`id_cliente`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_reserva_empleado` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_reserva_habitacion` FOREIGN KEY (`id_habitacion`) REFERENCES `HABITACION` (`id_habitacion`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_reserva_fechas` CHECK ((`fecha_salida` > `fecha_entrada`)),
  CONSTRAINT `chk_reserva_huespedes` CHECK ((`numero_huespedes` > 0)),
  CONSTRAINT `chk_reserva_monto` CHECK ((`monto_total` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'hotel_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-18 23:45:25
