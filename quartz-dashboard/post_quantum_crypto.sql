-- MySQL dump 10.13  Distrib 8.0.31, for Linux (x86_64)
--
-- Host: localhost    Database: post_quantum_crypto
-- ------------------------------------------------------
-- Server version	8.0.31-0ubuntu0.20.04.2

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
-- Table structure for table `aource_crypto_algo`
--

DROP TABLE IF EXISTS `source_crypto_algo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `source_crypto_algo` (
  `algo_name` varchar(255) NOT NULL,
  `pqc_safe` tinyint(1) DEFAULT NULL,
  `risk_factor` decimal(2,1) DEFAULT NULL,
  `remediation` varchar(255) DEFAULT NULL,
  `key_size` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `aource_crypto_algo`
--

LOCK TABLES `source_crypto_algo` WRITE;
INSERT INTO `source_crypto_algo` VALUES ('AES-CBC',1,0,'AES-CBC is PQC secure for key size greater than 256 bits.','256'), ('aes',1,0,'AES is PQC secure for key size greater than 256 bits.','256'),('3DES',0,1.0,'3DES is not PQC safe','0'),('des3_ede',0,1.0,'DES3_EDE is not PQC safe','0'),('AES-XTS',1,0,'AES-XTS is PQC secure for key size greater than 256 bits.', '256');
UNLOCK TABLES;

--
-- Table structure for table `api_scan`
--

DROP TABLE IF EXISTS `api_scan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `api_scan` (
  `scan_id` int NOT NULL AUTO_INCREMENT,
  `host` varchar(255) NOT NULL,
  `port` int DEFAULT NULL,
  `protocol` varchar(255) DEFAULT NULL,
  `status` varchar(255) NOT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`scan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `api_scan`
--

LOCK TABLES `api_scan` WRITE;
/*!40000 ALTER TABLE `api_scan` DISABLE KEYS */;
INSERT INTO `api_scan` VALUES (1,'https://google.com',443,'https','Delete',NULL),(2,'127.0.0.1',3306,'mysql','Delete',NULL),(3,'127.0.0.1',3306,'mysql','Delete',NULL),(4,'127.0.0.1',3306,'mysql','Delete',NULL),(5,'127.0.0.1',3306,'mysql','Delete',NULL),(6,'127.0.0.1',3306,'mysql','Delete',NULL),(7,'127.0.0.1',3306,'mysql','Complete','127.0.0.1_20230202-0951.json'),(8,'127.0.0.1',3306,'mysql','Delete',NULL),(9,'127.0.0.1',3306,'mysql','Delete',NULL),(10,'127.0.0.1',3306,'mysql','Delete',NULL),(11,'127.0.0.1',3306,'mysql','Delete',NULL),(12,'127.0.0.1',3306,'mysql','Initiated',NULL),(13,'127.0.0.1',3306,'mysql','Initiated',NULL),(14,'127.0.0.1',3306,'mysql','Initiated',NULL),(15,'127.0.0.1',3306,'mysql','Initiated',NULL),(16,'127.0.0.1',3306,'mysql','Initiated','127.0.0.1_20230301-0733.json'),(17,'127.0.0.1',3306,'mysql','Complete','127.0.0.1_20230301-0740.json'),(18,'127.0.0.1',3306,'mysql','Complete','127.0.0.1_20230301-0750.json'),(19,'127.0.0.1',3306,'mysql','Complete','127.0.0.1_20230301-0754.json');
/*!40000 ALTER TABLE `api_scan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `encryption_risk_factor`
--

DROP TABLE IF EXISTS `encryption_risk_factor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `encryption_risk_factor` (
  `algo_name` varchar(255) DEFAULT NULL,
  `pqc_safe` varchar(3) DEFAULT NULL,
  `risk_factor` decimal(2,1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `encryption_risk_factor`
--

LOCK TABLES `encryption_risk_factor` WRITE;
/*!40000 ALTER TABLE `encryption_risk_factor` DISABLE KEYS */;
INSERT INTO `encryption_risk_factor` VALUES ('RSA','No',1.0),('AES256','Yes',0.0),('AES128','Yes',0.5),('3DES','No',1.0);
/*!40000 ALTER TABLE `encryption_risk_factor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hashing_risk_factor`
--

DROP TABLE IF EXISTS `hashing_risk_factor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hashing_risk_factor` (
  `algo_name` varchar(255) DEFAULT NULL,
  `pqc_safe` varchar(3) DEFAULT NULL,
  `risk_factor` decimal(2,1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hashing_risk_factor`
--

LOCK TABLES `hashing_risk_factor` WRITE;
/*!40000 ALTER TABLE `hashing_risk_factor` DISABLE KEYS */;
INSERT INTO `hashing_risk_factor` VALUES ('MD5','No',1.0),('SHA256','Yes',0.0),('SHA384','Yes',0.0),('SHA','Yes',0.5);
/*!40000 ALTER TABLE `hashing_risk_factor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kx_risk_factor`
--

DROP TABLE IF EXISTS `kx_risk_factor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kx_risk_factor` (
  `algo_name` varchar(255) DEFAULT NULL,
  `pqc_safe` varchar(3) DEFAULT NULL,
  `risk_factor` decimal(2,1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kx_risk_factor`
--

LOCK TABLES `kx_risk_factor` WRITE;
/*!40000 ALTER TABLE `kx_risk_factor` DISABLE KEYS */;
INSERT INTO `kx_risk_factor` VALUES ('ECDHE_RSA','No',1.0),('CRYSTALS-KYBER','Yes',0.0),('Sike','Yes',0.5),('RSA','No',1.0);
/*!40000 ALTER TABLE `kx_risk_factor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tls_crypto_algo`
--

DROP TABLE IF EXISTS `tls_crypto_algo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tls_crypto_algo` (
  `algo_name` varchar(255) NOT NULL,
  `pqc_safe` tinyint(1) DEFAULT NULL,
  `risk_factor` decimal(2,1) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `key_exchange` varchar(255) DEFAULT NULL,
  `encryption` varchar(255) DEFAULT NULL,
  `hash` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`algo_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tls_crypto_algo`
--

LOCK TABLES `tls_crypto_algo` WRITE;
/*!40000 ALTER TABLE `tls_crypto_algo` DISABLE KEYS */;
INSERT INTO `tls_crypto_algo` VALUES ('AES128-SHA',1,0.5,'Improve PQC compliance by upgrading to AES256.','','AES128','SHA'),('ECDHE-RSA-AES256-SHA384',0,1.0,'ECDHE-RSA is not PQC safe','ECDHE-RSA','AES256','SHA384'),('TLS_AES_128_GCM_SHA256',1,0.5,'Upgrade AES128 to AES256','','AES128','SHA256'),('TLS_CHACHA20_POLY1305_SHA256',0,1.0,'Not PQC secure','','CHACHA20_POLY1305','SHA256'),('TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA',0,1.0,'Use AES 256 and SHAE 256 or higher','','',''),('TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA',1,0.0,'PQC secure','ECDHE-RSA','AES256','SHA'),('TLS_RSA_WITH_3DES_EDE_CBC_SHA',0,1.0,'RSA and 3DES are not PQC secure','RSA','3DES','SHA'),('TLS_RSA_WITH_AES_128_CBC_SHA256',0,1.0,'RSA is not PQC secure','RSA','AES128','SHA256');
/*!40000 ALTER TABLE `tls_crypto_algo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-06  7:41:56
