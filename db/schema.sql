-- ===============================
-- DROP OLD TABLES (for rebuilds)
-- ===============================
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS seats;
DROP TABLE IF EXISTS training_reservations;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS floors;
DROP TABLE IF EXISTS offices;
DROP TABLE IF EXISTS users;


-- ===============================
-- USERS
-- ===============================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT UNIQUE,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100),
    role ENUM('Employee','Manager','Admin','Management') DEFAULT 'Employee',
    project_name VARCHAR(100) NULL
);


-- ===============================
-- OFFICES
-- ===============================
CREATE TABLE offices (
    office_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

-- ===============================
-- FLOORS
-- ===============================
CREATE TABLE floors (
    floor_id INT AUTO_INCREMENT PRIMARY KEY,
    office_id INT NOT NULL,
    floor_number INT NOT NULL,
    floor_type ENUM('Normal','Cafeteria') DEFAULT 'Normal',
    FOREIGN KEY (office_id) REFERENCES offices(office_id)
);

-- ===============================
-- RESOURCES (workspace, meeting rooms, etc.)
-- ===============================
CREATE TABLE resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    floor_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    resource_type ENUM('Workspace','MeetingRoom','ConferenceHall','TrainingRoom') NOT NULL,
    capacity INT NOT NULL DEFAULT 30,
    project_name VARCHAR(100) DEFAULT 'LUMEN', -- only for workspace
    FOREIGN KEY (floor_id) REFERENCES floors(floor_id)
);

-- ===============================
-- SEATS (only for workspace resources)
-- ===============================
CREATE TABLE seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT NOT NULL,
    seat_number VARCHAR(20) NOT NULL,
    project_name VARCHAR(100), -- match seed.sql
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
);


CREATE TABLE reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    seat_id INT, 
    reservation_date DATE NOT NULL,
    
    start_time TIME NULL,
    end_time TIME NULL,
    time_slot ENUM('Morning','Afternoon','Evening') NULL, 
    batch ENUM('Java1','Java2','Python') NULL, 
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
);

CREATE TABLE training_reservations (
    training_reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resource_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    batch ENUM('Java1','Java2','Python') NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
);

