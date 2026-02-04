-- create the tables
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    forename VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL CHECK (email LIKE '%@%'),
    preferred_language VARCHAR(50) NOT NULL,
    optin BOOLEAN NOT NULL,
    country VARCHAR(50) NOT NULL,
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN ('SMS', 'Email', 'Phone'))
);

CREATE TABLE Policies (
    policy_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL UNIQUE,
    policy_type VARCHAR(50) NOT NULL CHECK (policy_type IN ('Travel', 'Home')),
    active_status BOOLEAN NOT NULL,
    policy_coverage TEXT,

    policy_coverage_json JSON NOT NULL
      DEFAULT (JSON_OBJECT(
        'weather_warning', false,
        'flight_disruption', false,
        'gov_advice_change', false,
        'major_event', false,
        'safety_only', false
      )),

    CONSTRAINT chk_policy_coverage_json
      CHECK (
        JSON_SCHEMA_VALID(
          '{
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "weather_warning":   { "type": "boolean" },
              "flight_disruption":{ "type": "boolean" },
              "gov_advice_change":{ "type": "boolean" },
              "major_event":      { "type": "boolean" },
              "safety_only":      { "type": "boolean" }
            },
            "required": [
              "weather_warning",
              "flight_disruption",
              "gov_advice_change",
              "major_event",
              "safety_only"
            ]
          }',
          policy_coverage_json
        )
      ),

    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    INDEX idx_policies_customer_active (customer_id, active_status)
);


CREATE TABLE Travel (
    travel_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    flight_number VARCHAR(20),
    departure_airport VARCHAR(3),
    arrival_airport VARCHAR(3),
    trip_status VARCHAR(50) NOT NULL CHECK (trip_status IN ('Planned', 'Ongoing', 'Delayed', 'Cancelled', 'Arrived')),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE Events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('weather-warning', 'flight-disruption', 'gov_advice_change', 'major_event')),
    location_type VARCHAR(50) NOT NULL CHECK (location_type IN ('Country', 'Region', 'Admin_area', 'City', 'Airport', 'Flight')),
    location_code VARCHAR(20) NOT NULL,
    event_date DATE NOT NULL,
    severity_level INT NOT NULL CHECK (severity_level BETWEEN 1 AND 5),
    source VARCHAR(100) NOT NULL CHECK (source IN ('Simulator', 'Live API', 'Manual', 'Government')),
    external_source VARCHAR(100),
    event_description TEXT,
    json_payload JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Decisions (
    decision_id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    travel_id INT NOT NULL,
    decision_type VARCHAR(50) NOT NULL CHECK (decision_type IN ('no_action', 'notify', 'notify_safety_only')),
    reason_code VARCHAR(100) NOT NULL CHECK (reason_code IN ('not_travelling', 'no_consent', 'no_coverage', 'eligible', 'goodwill_alert')),
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (travel_id) REFERENCES Travel(travel_id),
    FOREIGN KEY (event_id) REFERENCES Events(event_id),

    INDEX idx_decisions_event (event_id),
    INDEX idx_decisions_reason (reason_code),
    INDEX idx_decisions_travel (travel_id)
);

CREATE TABLE Locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    location_type VARCHAR(50) NOT NULL
        CHECK (location_type IN ('Country', 'Region', 'Admin_area', 'City', 'Airport')),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_location_id INT NULL,
    CONSTRAINT fk_locations_parent
        FOREIGN KEY (parent_location_id) REFERENCES Locations(location_id)
);

CREATE TABLE Actions (
    action_id INT PRIMARY KEY AUTO_INCREMENT,
    decision_id INT NOT NULL,
    channel_type VARCHAR(20) NOT NULL CHECK (channel_type IN ('sms','email','push','whatsapp','in_app')),
    action_status VARCHAR(20) NOT NULL CHECK (action_status IN ('queued','sent','failed')),
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (decision_id) REFERENCES Decisions(decision_id),
    
    INDEX idx_actions_decision (decision_id)
);

INSERT INTO Locations (location_id, location_type, code, name, parent_location_id) VALUES
-- Country
(1,  'Country',   'FR',      'France',                 NULL),

-- Regions
(10, 'Region',    'FR-GES',  'Grand Est',              1),
(11, 'Region',    'FR-IDF',  'Île-de-France',          1),
(12, 'Region',    'FR-NAQ',  'Nouvelle-Aquitaine',     1),

-- Admin areas (departments)
(20, 'Admin_area','FR-67',   'Bas-Rhin',               10),
(21, 'Admin_area','FR-75',   'Paris',                  11),
(22, 'Admin_area','FR-33',   'Gironde',                12),
(23, 'Admin_area','FR-87',   'Haute-Vienne',           12),

-- Cities
(30, 'City',      'STR',     'Strasbourg',             20),
(31, 'City',      'PAR',     'Paris',                  21),
(32, 'City',      'BOD',     'Bordeaux',               22),
(33, 'City',      'LIM',     'Limoges',                23),

-- Airports
(40, 'Airport',   'SXB',     'Strasbourg Airport',     30),
(41, 'Airport',   'CDG',     'Paris Charles de Gaulle',31),
(42, 'Airport',   'ORY',     'Paris Orly',             31),
(43, 'Airport',   'BOD',     'Bordeaux-Mérignac',      32);