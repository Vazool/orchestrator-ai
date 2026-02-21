-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: europ_assistance_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `actions`
--

DROP TABLE IF EXISTS `actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `actions` (
  `action_id` int NOT NULL AUTO_INCREMENT,
  `decision_id` int NOT NULL,
  `channel_type` varchar(50) DEFAULT NULL,
  `action_status` varchar(50) DEFAULT NULL,
  `message` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`action_id`),
  KEY `idx_actions_decision` (`decision_id`),
  CONSTRAINT `actions_ibfk_1` FOREIGN KEY (`decision_id`) REFERENCES `decisions` (`decision_id`),
  CONSTRAINT `actions_chk_1` CHECK ((`channel_type` in (_utf8mb4'sms',_utf8mb4'email',_utf8mb4'push',_utf8mb4'whatsapp',_utf8mb4'in_app'))),
  CONSTRAINT `actions_chk_2` CHECK ((`action_status` in (_utf8mb4'queued',_utf8mb4'sent',_utf8mb4'failed')))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `forename` varchar(100) NOT NULL,
  `surname` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `optin` tinyint(1) NOT NULL,
  `preferred_language` varchar(50) DEFAULT 'English',
  `country` varchar(50) DEFAULT NULL,
  `channel_type` varchar(50) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `travel_purpose` varchar(20) DEFAULT 'leisure',
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `decisions`
--

DROP TABLE IF EXISTS `decisions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `decisions` (
  `decision_id` int NOT NULL AUTO_INCREMENT,
  `event_id` int NOT NULL,
  `travel_id` int NOT NULL,
  `decision_type` varchar(50) DEFAULT NULL,
  `reason_code` varchar(50) DEFAULT NULL,
  `reason` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `risk_score` float DEFAULT NULL,
  PRIMARY KEY (`decision_id`),
  KEY `idx_decisions_event` (`event_id`),
  KEY `idx_decisions_reason` (`reason_code`),
  KEY `idx_decisions_travel` (`travel_id`),
  CONSTRAINT `decisions_ibfk_1` FOREIGN KEY (`travel_id`) REFERENCES `travel` (`travel_id`),
  CONSTRAINT `decisions_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`),
  CONSTRAINT `decisions_chk_1` CHECK ((`decision_type` in (_utf8mb4'no_action',_utf8mb4'notify',_utf8mb4'notify_safety_only'))),
  CONSTRAINT `decisions_chk_2` CHECK ((`reason_code` in (_utf8mb4'eligible',_utf8mb4'already_contacted',_utf8mb4'no_consent',_utf8mb4'goodwill_alert',_utf8mb4'ai_high_risk',_utf8mb4'ai_moderate_risk',_utf8mb4'ai_low_risk')))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `event_type` varchar(50) NOT NULL,
  `location_type` varchar(50) NOT NULL,
  `location_code` varchar(20) NOT NULL,
  `event_date` date NOT NULL,
  `severity_level` int NOT NULL,
  `source` varchar(100) NOT NULL,
  `external_source` varchar(100) DEFAULT NULL,
  `event_description` text,
  `json_payload` json DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`),
  CONSTRAINT `events_chk_1` CHECK ((`event_type` in (_utf8mb4'weather_warning',_utf8mb4'flight_disruption',_utf8mb4'gov_advice_change',_utf8mb4'major_event',_utf8mb4'weather-warning',_utf8mb4'flight-disruption'))),
  CONSTRAINT `events_chk_2` CHECK ((`location_type` in (_utf8mb4'Country',_utf8mb4'Region',_utf8mb4'Admin_area',_utf8mb4'City',_utf8mb4'Airport',_utf8mb4'Flight'))),
  CONSTRAINT `events_chk_3` CHECK ((`severity_level` between 1 and 5)),
  CONSTRAINT `events_chk_4` CHECK ((`source` in (_utf8mb4'Simulator',_utf8mb4'Live API',_utf8mb4'Manual',_utf8mb4'Government')))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locations` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `location_type` varchar(50) NOT NULL,
  `code` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `parent_location_id` int DEFAULT NULL,
  PRIMARY KEY (`location_id`),
  KEY `fk_locations_parent` (`parent_location_id`),
  CONSTRAINT `fk_locations_parent` FOREIGN KEY (`parent_location_id`) REFERENCES `locations` (`location_id`),
  CONSTRAINT `locations_chk_1` CHECK ((`location_type` in (_utf8mb4'Country',_utf8mb4'Region',_utf8mb4'Admin_area',_utf8mb4'City',_utf8mb4'Airport')))
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `policies`
--

DROP TABLE IF EXISTS `policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policies` (
  `policy_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `policy_type` varchar(100) DEFAULT NULL,
  `active_status` tinyint DEFAULT '1',
  `policy_coverage` text,
  `policy_coverage_json` json NOT NULL DEFAULT (json_object(_utf8mb4'weather_warning',false,_utf8mb4'flight_disruption',false,_utf8mb4'gov_advice_change',false,_utf8mb4'major_event',false,_utf8mb4'safety_only',false)),
  PRIMARY KEY (`policy_id`),
  UNIQUE KEY `customer_id` (`customer_id`),
  KEY `idx_policies_customer_active` (`customer_id`,`active_status`),
  CONSTRAINT `policies_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `chk_policy_coverage_json` CHECK (json_schema_valid(_utf8mb4'{\n            "type": "object",\n            "additionalProperties": false,\n            "properties": {\n              "weather_warning":   { "type": "boolean" },\n              "flight_disruption":{ "type": "boolean" },\n              "gov_advice_change":{ "type": "boolean" },\n              "major_event":      { "type": "boolean" },\n              "safety_only":      { "type": "boolean" }\n            },\n            "required": [\n              "weather_warning",\n              "flight_disruption",\n              "gov_advice_change",\n              "major_event",\n              "safety_only"\n            ]\n          }',`policy_coverage_json`))
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `policycoverage`
--

DROP TABLE IF EXISTS `policycoverage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `policycoverage` (
  `policy_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `policy_type` varchar(50) NOT NULL,
  PRIMARY KEY (`policy_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `policycoverage_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `travel`
--

DROP TABLE IF EXISTS `travel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `travel` (
  `travel_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `arrival_airport` varchar(10) NOT NULL,
  `destination_region` varchar(50) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `final_destination` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`travel_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `travel_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-21 23:11:14
