USE workspace_reservation;

-- Clear existing data
DELETE FROM reservations;
DELETE FROM seats;
DELETE FROM resources;
DELETE FROM floors;
DELETE FROM offices;
DELETE FROM users;

-- Reset AUTO_INCREMENT
ALTER TABLE reservations AUTO_INCREMENT = 1;
ALTER TABLE seats AUTO_INCREMENT = 1;
ALTER TABLE resources AUTO_INCREMENT = 1;
ALTER TABLE floors AUTO_INCREMENT = 1;
ALTER TABLE offices AUTO_INCREMENT = 1;
ALTER TABLE users AUTO_INCREMENT = 1;

-- Offices
INSERT INTO offices (name, location) VALUES
('Guindy', 'Chennai'),
('Thoraipakkam', 'Chennai'),
('OMR', 'Chennai');

-- Floors
INSERT INTO floors (office_id, floor_number, floor_type) VALUES
((SELECT office_id FROM offices WHERE name='Guindy'), 1, 'Cafeteria'),
((SELECT office_id FROM offices WHERE name='Guindy'), 2, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 3, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 4, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 5, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 6, 'Cafeteria'),
((SELECT office_id FROM offices WHERE name='Guindy'), 7, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 8, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 9, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 10, 'Normal'),
((SELECT office_id FROM offices WHERE name='Guindy'), 11, 'Normal'),

((SELECT office_id FROM offices WHERE name='Thoraipakkam'), 1, 'Normal'),
((SELECT office_id FROM offices WHERE name='Thoraipakkam'), 2, 'Normal'),
((SELECT office_id FROM offices WHERE name='Thoraipakkam'), 3, 'Normal'),

((SELECT office_id FROM offices WHERE name='OMR'), 1, 'Normal');

-- Resources
INSERT INTO resources (floor_id, name, resource_type, capacity) VALUES
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Guindy') AND floor_number=2), 'ProjectA Workspace', 'Workspace', 10),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Guindy') AND floor_number=2), 'Guindy Meeting Room 1', 'MeetingRoom', 20),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Guindy') AND floor_number=2), 'Guindy Conference Hall', 'ConferenceHall', 50),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Guindy') AND floor_number=2), 'Guindy Training Room', 'TrainingRoom', 30),

((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Thoraipakkam') AND floor_number=1), 'ProjectB Workspace', 'Workspace', 10),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Thoraipakkam') AND floor_number=1), 'Thoraipakkam Meeting Room 1', 'MeetingRoom', 15),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Thoraipakkam') AND floor_number=1), 'Thoraipakkam Conference Hall', 'ConferenceHall', 40),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='Thoraipakkam') AND floor_number=1), 'Thoraipakkam Training Room', 'TrainingRoom', 25),

((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='OMR') AND floor_number=1), 'ProjectC Workspace', 'Workspace', 10),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='OMR') AND floor_number=1), 'OMR Meeting Room 1', 'MeetingRoom', 10),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='OMR') AND floor_number=1), 'OMR Conference Hall', 'ConferenceHall', 30),
((SELECT floor_id FROM floors WHERE office_id=(SELECT office_id FROM offices WHERE name='OMR') AND floor_number=1), 'OMR Training Room', 'TrainingRoom', 20);

-- Seats (Project A)
INSERT INTO seats (resource_id, seat_number)
SELECT resource_id, 'A1' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A2' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A3' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A4' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A5' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A6' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A7' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A8' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A9' FROM resources WHERE name='ProjectA Workspace'
UNION ALL SELECT resource_id, 'A10' FROM resources WHERE name='ProjectA Workspace';

-- Seats (Project B)
INSERT INTO seats (resource_id, seat_number)
SELECT resource_id, 'B1' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B2' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B3' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B4' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B5' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B6' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B7' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B8' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B9' FROM resources WHERE name='ProjectB Workspace'
UNION ALL SELECT resource_id, 'B10' FROM resources WHERE name='ProjectB Workspace';

-- Seats (Project C)
INSERT INTO seats (resource_id, seat_number)
SELECT resource_id, 'C1' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C2' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C3' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C4' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C5' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C6' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C7' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C8' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C9' FROM resources WHERE name='ProjectC Workspace'
UNION ALL SELECT resource_id, 'C10' FROM resources WHERE name='ProjectC Workspace';

-- Users
INSERT INTO users (employee_id, username, email, password, role, project_name) VALUES
(10001, 'Alice', 'alice@prodapt.com', 'alice123', 'Employee', 'LUMEN'),
(10002, 'Bob', 'bob@prodapt.com', 'bob123', 'Employee', 'LUMEN'),
(10003, 'Charlie', 'charlie@prodapt.com', 'charlie123', 'Employee', 'SYNAPT'),
(20001, 'David', 'david@prodapt.com', 'david123', 'Manager', 'SYNAPT'),
(20002, 'Eve', 'eve@prodapt.com', 'eve123', 'Manager', 'SYNAPT'),

(30002, 'Sophia', 'sophia@prodapt.com', 'sophia123', 'Management', NULL),
(28945, 'Arun', 'arun.sr@prodapt.com', 'arun123', 'Employee', 'SYNAPT'),
(30000, 'HR', 'hr@prodapt.com', 'HR', 'Management', NULL);

-- Insert a Meeting Room resource (floor_id=1 is just example, use a valid floor_id from your floors table)
INSERT INTO resources (name, resource_type, floor_id)
VALUES ('Conference Room 1', 'MeetingRoom', 1);

INSERT INTO training_reservations (user_id, resource_id, start_date, end_date, batch)
VALUES
-- Arun reserves Guindy Training Room
(6, 4, '2025-09-10', '2025-09-14', 'Java1'),

-- Sophia reserves Thoraipakkam Training Room
(7, 8, '2025-09-15', '2025-09-20', 'Python');

INSERT INTO reservations (user_id, resource_id, seat_id, reservation_date, time_slot)
VALUES
-- Alice reserves two seats
(1, 1, 1, '2025-09-01', 'Morning'),
(1, 1, 2, '2025-09-02', 'Morning'),

-- Bob reserves the same seat on consecutive days (good training data for "reserved_again")
(2, 1, 3, '2025-09-03', 'Afternoon'),
(2, 1, 3, '2025-09-04', 'Afternoon'),

-- Charlie reserves another seat once
(3, 1, 4, '2025-09-05', 'Morning'),

-- David (Manager) reserves a seat — good to have manager data too
(4, 1, 5, '2025-09-05', 'Afternoon'),

-- Eve (Manager) reserves another seat
(5, 1, 6, '2025-09-06', 'Morning'),

-- Sophia (Management) reserves once — helps training model for management users
(6, 1, 7, '2025-09-07', 'Morning'),

-- Arun (You) reserves multiple times to have pattern for recommendations
(7, 1, 8, '2025-09-08', 'Morning'),
(7, 1, 8, '2025-09-09', 'Morning'),
(7, 1, 8, '2025-09-10', 'Morning'),

-- HR reserves once
(8, 1, 9, '2025-09-08', 'Afternoon');
