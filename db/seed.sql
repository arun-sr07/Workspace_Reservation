USE workspace_reservation;

-- 1. Clear existing data in dependency order
DELETE FROM reservations;
DELETE FROM seats;
DELETE FROM workspaces;
DELETE FROM users;

-- 2. Reset auto-increment counters
ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE workspaces AUTO_INCREMENT = 1;
ALTER TABLE seats AUTO_INCREMENT = 1;
ALTER TABLE reservations AUTO_INCREMENT = 1;

-- 3. Insert users
INSERT INTO users (name, email) VALUES 
('Arun Srinivasan', 'arunsrinivasan003@gmail.com');

-- 4. Insert workspaces
INSERT INTO workspaces (name) VALUES 
('Workspace A'),
('Workspace B');

-- 5. Insert seats (workspace IDs 1 and 2 now guaranteed to exist)
INSERT INTO seats (workspace_id, seat_number) VALUES
(1, 'A1'),
(1, 'A2'),
(1, 'A3'),
(2, 'B1'),
(2, 'B2'),
(2, 'B3');
