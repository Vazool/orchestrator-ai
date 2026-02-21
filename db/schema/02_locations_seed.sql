USE europ_assistance_db;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE locations;

INSERT INTO locations (location_id, location_type, code, name, parent_location_id) VALUES
(1, 'Country', 'FR', 'France', NULL),
(2, 'Country', 'GB', 'United Kingdom', NULL),
(3, 'Country', 'ES', 'Spain', NULL),
(10, 'Region', 'FR-GES', 'Grand Est', 1),
(11, 'Region', 'FR-IDF', 'Île-de-France', 1),
(12, 'Region', 'FR-NAQ', 'Nouvelle-Aquitaine', 1),
(14, 'Region', 'UK-LON', 'London Area', 2),
(15, 'Region', 'ES-MAD', 'Madrid Region', 3),
(20, 'Admin_area', 'FR-67', 'Bas-Rhin', 10),
(21, 'Admin_area', 'FR-75', 'Paris', 11),
(22, 'Admin_area', 'FR-33', 'Gironde', 12),
(23, 'Admin_area', 'FR-87', 'Haute-Vienne', 12),
(24, 'Admin_area', 'FR-13', 'Bouches-du-Rhône', 1),
(25, 'Admin_area', 'FR-06', 'Alpes-Maritimes', 1),
(26, 'Admin_area', 'FR-69', 'Rhône', 1),
(30, 'City', 'STR', 'Strasbourg', 20),
(31, 'City', 'PAR', 'Paris', 21),
(32, 'City', 'BOD', 'Bordeaux', 22),
(33, 'City', 'LIM', 'Limoges', 23),
(34, 'City', 'MRS', 'Marseille', 24),
(35, 'City', 'NCE', 'Nice', 25),
(36, 'City', 'LYS', 'Lyon', 26),
(37, 'City', 'LON', 'London', 14),
(38, 'City', 'MAD', 'Madrid', 15),
(40, 'Airport', 'SXB', 'Strasbourg Airport', 30),
(41, 'Airport', 'CDG', 'Paris Charles de Gaulle', 31),
(42, 'Airport', 'ORY', 'Paris Orly', 31),
(43, 'Airport', 'BOD', 'Bordeaux-Mérignac', 32),
(44, 'Airport', 'MRS', 'Marseille Provence', 34),
(45, 'Airport', 'NCE', 'Nice Côte d’Azur', 35),
(46, 'Airport', 'LYS', 'Lyon–Saint Exupéry', 36),
(47, 'Airport', 'LHR', 'London Heathrow', 37),
(48, 'Airport', 'MAD', 'Adolfo Suárez Madrid–Barajas', 38);

SET FOREIGN_KEY_CHECKS = 1;