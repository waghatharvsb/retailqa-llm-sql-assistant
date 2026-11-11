-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: atliq_tshirts
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.22.04.4

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
-- Current Database: `atliq_tshirts`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `atliq_tshirts` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `atliq_tshirts`;

--
-- Table structure for table `discounts`
--

DROP TABLE IF EXISTS `discounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discounts` (
  `discount_id` int NOT NULL AUTO_INCREMENT,
  `t_shirt_id` int NOT NULL,
  `pct_discount` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`discount_id`),
  KEY `t_shirt_id` (`t_shirt_id`),
  CONSTRAINT `discounts_ibfk_1` FOREIGN KEY (`t_shirt_id`) REFERENCES `t_shirts` (`t_shirt_id`),
  CONSTRAINT `discounts_chk_1` CHECK ((`pct_discount` between 0 and 100))
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discounts`
--

LOCK TABLES `discounts` WRITE;
/*!40000 ALTER TABLE `discounts` DISABLE KEYS */;
INSERT INTO `discounts` VALUES (1,1,10.00),(2,2,15.00),(3,3,20.00),(4,4,5.00),(5,5,25.00),(6,6,10.00),(7,7,30.00),(8,8,35.00),(9,9,40.00),(10,10,45.00);
/*!40000 ALTER TABLE `discounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_shirts`
--

DROP TABLE IF EXISTS `t_shirts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_shirts` (
  `t_shirt_id` int NOT NULL AUTO_INCREMENT,
  `brand` enum('Van Huesen','Levi','Nike','Adidas') NOT NULL,
  `color` enum('Red','Blue','Black','White') NOT NULL,
  `size` enum('XS','S','M','L','XL') NOT NULL,
  `price` int DEFAULT NULL,
  `stock_quantity` int NOT NULL,
  PRIMARY KEY (`t_shirt_id`),
  UNIQUE KEY `brand_color_size` (`brand`,`color`,`size`),
  CONSTRAINT `t_shirts_chk_1` CHECK ((`price` between 10 and 50))
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_shirts`
--

LOCK TABLES `t_shirts` WRITE;
/*!40000 ALTER TABLE `t_shirts` DISABLE KEYS */;
INSERT INTO `t_shirts` VALUES (1,'Nike','Red','XL',18,28),(2,'Levi','Blue','S',32,87),(3,'Nike','Black','L',14,61),(4,'Nike','White','XS',30,41),(5,'Van Huesen','Red','L',33,61),(6,'Van Huesen','White','XS',47,26),(7,'Van Huesen','Blue','XS',36,89),(8,'Levi','Blue','XS',29,81),(9,'Nike','Blue','XL',43,35),(10,'Adidas','White','S',16,84),(12,'Adidas','Red','M',34,42),(14,'Adidas','Blue','L',36,25),(15,'Adidas','White','L',20,99),(16,'Van Huesen','Black','XL',45,47),(17,'Levi','Red','XS',19,83),(18,'Levi','Blue','XL',26,32),(22,'Adidas','Black','M',14,33),(23,'Adidas','Red','L',27,85),(24,'Adidas','Black','XS',21,21),(25,'Adidas','Black','L',49,53),(26,'Levi','Red','XL',46,100),(27,'Levi','Black','XL',27,75),(28,'Levi','Blue','M',48,98),(29,'Van Huesen','Black','M',27,91),(30,'Van Huesen','Blue','S',38,40),(31,'Nike','White','L',46,35),(32,'Adidas','White','M',42,46),(33,'Nike','Black','XL',33,95),(34,'Van Huesen','Blue','M',16,57),(36,'Nike','Black','S',32,11),(37,'Levi','Red','M',50,47),(39,'Adidas','Red','XL',29,61),(41,'Van Huesen','Black','S',11,60),(42,'Nike','Black','XS',32,54),(46,'Nike','Red','S',18,23),(49,'Nike','Red','XS',35,87),(52,'Levi','Red','L',50,82),(53,'Van Huesen','White','XL',15,91),(54,'Van Huesen','White','L',26,77),(55,'Levi','Red','S',25,82),(57,'Levi','White','XL',50,28),(60,'Adidas','Black','S',21,54),(63,'Van Huesen','Black','XS',21,91),(64,'Nike','Blue','XS',17,75),(67,'Van Huesen','White','S',27,13),(71,'Adidas','Red','XS',19,74),(75,'Adidas','Red','S',17,24),(78,'Van Huesen','Black','L',35,100),(83,'Adidas','Black','XL',15,77),(85,'Levi','White','XS',41,74),(88,'Adidas','White','XS',23,33),(92,'Nike','White','XL',38,74),(94,'Levi','White','S',24,15),(98,'Levi','Black','S',11,35),(99,'Levi','Blue','L',40,80),(101,'Levi','White','L',12,33),(103,'Nike','White','M',31,96),(104,'Van Huesen','Red','XS',37,36),(112,'Van Huesen','Red','M',31,81),(114,'Levi','Black','XS',28,10),(115,'Nike','Blue','M',47,90),(120,'Van Huesen','White','M',38,10),(123,'Nike','White','S',38,78),(124,'Nike','Red','M',15,33),(129,'Nike','Blue','L',49,85),(135,'Adidas','Blue','M',23,93),(136,'Nike','Blue','S',18,15),(140,'Levi','Black','M',25,57),(148,'Adidas','Blue','XL',15,95),(157,'Van Huesen','Blue','L',50,15),(163,'Van Huesen','Red','XL',43,66),(167,'Adidas','White','XL',12,43),(169,'Levi','Black','L',33,90),(176,'Adidas','Blue','S',24,12),(192,'Levi','White','M',47,86),(200,'Adidas','Blue','XS',19,88);
/*!40000 ALTER TABLE `t_shirts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-04 13:38:26
