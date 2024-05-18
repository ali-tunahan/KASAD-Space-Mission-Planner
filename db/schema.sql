USE DASAK;

CREATE TABLE IF NOT EXISTS Worksa(idd CHAR(36) PRIMARY KEY);

CREATE TABLE IF NOT EXISTS User (
    id CHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Person (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(50),
    first_name VARCHAR(255),
    middle_name VARCHAR(255),
    last_name VARCHAR(255),
    FOREIGN KEY (id) REFERENCES User(id)
);

CREATE TABLE IF NOT EXISTS Admin (
    id CHAR(36) PRIMARY KEY,
    assigned_region VARCHAR(255),
    FOREIGN KEY (id) REFERENCES User(id)
);


CREATE TABLE IF NOT EXISTS Company (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    street VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    founding_date DATE,
    balance DECIMAL(19, 4),
    area_code VARCHAR(4),
    phone_number VARCHAR(50),
    FOREIGN KEY (id) REFERENCES User(id)
);

CREATE TABLE IF NOT EXISTS Astronaut (
    id CHAR(36) PRIMARY KEY,
    company_id CHAR(36),
    date_of_birth DATE,
    nationality VARCHAR(50),
    rank VARCHAR(50),
    years_of_experience INT,
    FOREIGN KEY (id) REFERENCES User(id),
    FOREIGN KEY (company_id) REFERENCES Company(id)
);


CREATE TABLE IF NOT EXISTS Bidder (
    id CHAR(36) PRIMARY KEY,
    specialization VARCHAR(255),
    FOREIGN KEY (id) REFERENCES Company(id)
);

CREATE TABLE IF NOT EXISTS Bid (
    bid_id CHAR(36) PRIMARY KEY,
    bidder_id CHAR(36),
    amount DECIMAL(19, 4),
    bid_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (bidder_id) REFERENCES Bidder(id)
);

CREATE TABLE IF NOT EXISTS Employer (
    id CHAR(36) PRIMARY KEY,
    industry VARCHAR(100),
    FOREIGN KEY (id) REFERENCES Company(id)
);

CREATE TABLE IF NOT EXISTS Transaction (
    transaction_id CHAR(36) PRIMARY KEY,
    bidder_id CHAR(36),
    employer_id CHAR(36),
    date DATE,
    amount DECIMAL(19, 4),
    status VARCHAR(50),
    FOREIGN KEY (bidder_id) REFERENCES Bidder(id),
    FOREIGN KEY (employer_id) REFERENCES Employer(id)
);

CREATE TABLE IF NOT EXISTS SystemReport (
    report_id CHAR(36) PRIMARY KEY,
    id CHAR(36),
    title VARCHAR(100),
    content VARCHAR(5000),
    FOREIGN KEY (id) REFERENCES Admin(id)
);


CREATE TABLE IF NOT EXISTS Mission (
    mission_id CHAR(36) PRIMARY KEY,
    employer_id CHAR(36),
    title VARCHAR(100),
    description VARCHAR(5000),
    objectives VARCHAR(100),
    launch_date DATE,
    duration INT,
    num_of_astronauts INT,
    payload_volume INT,
    payload_weight INT,
    FOREIGN KEY (employer_id) REFERENCES Employer(id)
);

CREATE TABLE IF NOT EXISTS Training (
    training_id CHAR(36) PRIMARY KEY,
    name VARCHAR(100),
    code VARCHAR(20),
    description VARCHAR(5000),
    duration INT
);

CREATE TABLE IF NOT EXISTS Bid_Has_Astronaut (
    bid_id CHAR(36),
    id CHAR(36),
    PRIMARY KEY (bid_id, id),
    FOREIGN KEY (bid_id) REFERENCES Bid(bid_id),
    FOREIGN KEY (id) REFERENCES Astronaut(id)
);

CREATE TABLE IF NOT EXISTS Mission_Accepted_Bid (
    mission_id CHAR(36),
    bid_id CHAR(36),
    PRIMARY KEY (mission_id, bid_id),
    FOREIGN KEY (mission_id) REFERENCES Mission(mission_id),
    FOREIGN KEY (bid_id) REFERENCES Bid(bid_id)
);

CREATE TABLE IF NOT EXISTS Mission_Requires_Training (
    mission_id CHAR(36),
    training_id CHAR(36),
    PRIMARY KEY (mission_id, training_id),
    FOREIGN KEY (mission_id) REFERENCES Mission(mission_id),
    FOREIGN KEY (training_id) REFERENCES Training(training_id)
);

CREATE TABLE IF NOT EXISTS Astronaut_Completes_Training (
    astronaut_id CHAR(36),
    training_id CHAR(36),
    status INT,
    PRIMARY KEY (astronaut_id, training_id),
    FOREIGN KEY (astronaut_id) REFERENCES Astronaut(id),
    FOREIGN KEY (training_id) REFERENCES Training(training_id)
);


CREATE TABLE IF NOT EXISTS Training_Prerequisite_Training (
    prereq_id CHAR(36),
    train_id CHAR(36),
    PRIMARY KEY (prereq_id, train_id),
    FOREIGN KEY (prereq_id) REFERENCES Training(training_id),
    FOREIGN KEY (train_id) REFERENCES Training(training_id)
);

CREATE VIEW Astronaut_Age AS
SELECT 
    id, 
    TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
FROM 
    Astronaut;

CREATE VIEW Bidder_Missions AS
SELECT 
    M.mission_id,
    M.employer_id,
    M.title,
    M.description,
    M.objectives,
    M.launch_date,
    M.duration,
    M.num_of_astronauts,
    M.payload_volume,
    M.payload_weight
FROM 
    Mission M
JOIN 
    Mission_Accepted_Bid MAB ON M.mission_id = MAB.mission_id
JOIN 
    Bid BD ON MAB.bid_id = BD.bid_id
JOIN 
    Bidder B ON BD.bidder_id = B.id;

CREATE VIEW Astronaut_Accepted_Missions AS
SELECT 
    A.id AS astronaut_id,
    M.mission_id,
    M.employer_id,
    M.title,
    M.description,
    M.objectives,
    M.launch_date,
    M.duration,
    M.num_of_astronauts,
    M.payload_volume,
    M.payload_weight
FROM 
    Astronaut A
JOIN 
    Bid_Has_Astronaut BHA ON A.id = BHA.id
JOIN 
    Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
JOIN 
    Mission M ON MAB.mission_id = M.mission_id;


CREATE VIEW Astronaut_Stats AS
SELECT 
    A.id AS astronaut_id,
    COUNT(MAB.mission_id) AS experience,
    SUM(M.duration) / A.years_of_experience AS performance
FROM 
    Astronaut A
JOIN 
    Bid_Has_Astronaut BHA ON A.id = BHA.id
JOIN 
    Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
JOIN 
    Mission M ON MAB.mission_id = M.mission_id
WHERE 
    DATE_ADD(M.launch_date, INTERVAL M.duration DAY) >= CURDATE()
GROUP BY 
    A.id;


SET GLOBAL event_scheduler = ON;
CREATE EVENT IF NOT EXISTS UpdateBidStatusEvent
ON SCHEDULE EVERY 1 DAY
STARTS (TIMESTAMP(CURRENT_DATE) + INTERVAL 1 DAY)
DO
  UPDATE Bid
  SET status = 'DeadlinePassed'
  WHERE bid_date < CURRENT_DATE AND status != 'DeadlinePassed' AND status != 'Rejected';


DELIMITER //

CREATE TRIGGER CheckPersonCompanyIdBeforeInsert
BEFORE INSERT ON Person
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Company WHERE id = NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The same id exists in Company table.';
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER CheckCompanyPersonIdBeforeInsert
BEFORE INSERT ON Company
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Person WHERE id = NEW.id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The same id exists in Person table.';
    END IF;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AfterBidderDeleted
AFTER DELETE ON Bidder
FOR EACH ROW
BEGIN
    DELETE FROM Bid WHERE bidder_id = OLD.id;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AfterEmployerDeleted
AFTER DELETE ON Employer
FOR EACH ROW
BEGIN
    DELETE FROM Mission WHERE employer_id = OLD.id;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER AfterTransactionInserted
AFTER INSERT ON Transaction
FOR EACH ROW
BEGIN
    UPDATE Company SET balance = balance + NEW.amount WHERE id = NEW.bidder_id;
    UPDATE Company SET balance = balance - NEW.amount WHERE id = NEW.employer_id;
END //

DELIMITER ;



INSERT INTO User (id, email, password) VALUES
('11111111-1111-1111-1111-111111111111', 'user1@example.com', 'password1'),
('22222222-2222-2222-2222-222222222222', 'user2@example.com', 'password2'),
('33333333-3333-3333-3333-333333333333', 'user3@example.com', 'password3'),
('44444444-4444-4444-4444-444444444444', 'user4@example.com', 'password4'),
('55555555-5555-5555-5555-555555555555', 'user5@example.com', 'password5'),
('66666666-6666-6666-6666-666666666666', 'user6@example.com', 'password6'),
('77777777-7777-7777-7777-777777777777', 'user7@example.com', 'password7'),
('88888888-8888-8888-8888-888888888888', 'user8@example.com', 'password8'),
('99999999-9999-9999-9999-999999999999', 'user9@example.com', 'password9');

INSERT INTO Person (id, title, first_name, middle_name, last_name) VALUES
('11111111-1111-1111-1111-111111111111', 'Mr.', 'John', 'Q.', 'Doe'),
('22222222-2222-2222-2222-222222222222', 'Ms.', 'Jane', 'R.', 'Smith'),
('33333333-3333-3333-3333-333333333333', 'Dr.', 'Jim', 'B.', 'Beam'),

('77777777-7777-7777-7777-777777777777', 'Mr.', 'Gnour', 'The', 'Devourer'),
('88888888-8888-8888-8888-888888888888', 'Dr.', 'Ati', 'Tunahan', 'Zilla'),
('99999999-9999-9999-9999-999999999999', 'Av.', 'Serhan', 'Bayri', 'Domuzu');


INSERT INTO Admin (id, assigned_region) VALUES
('11111111-1111-1111-1111-111111111111', 'North America'),
('22222222-2222-2222-2222-222222222222', 'Europe'),
('33333333-3333-3333-3333-333333333333', 'Asia');

INSERT INTO Company (id, name, street, city, state, postal_code, founding_date, balance, area_code, phone_number) VALUES
('44444444-4444-4444-4444-444444444444', 'SpaceX', '1 Rocket Road', 'Hawthorne', 'CA', '90250', '2002-03-14', 1000000.00, '310', '123-4567'),
('55555555-5555-5555-5555-555555555555', 'Blue Origin', '2121 4th Ave', 'Seattle', 'WA', '98121', '2000-09-08', 2000000.00, '206', '765-4321'),
('66666666-6666-6666-6666-666666666666', 'Virgin Galactic', 'Virgin Way', 'Las Cruces', 'NM', '88001', '2004-01-01', 3000000.00, '575', '321-6547');

INSERT INTO Astronaut (id, company_id, date_of_birth, nationality, rank, years_of_experience) VALUES
('77777777-7777-7777-7777-777777777777', '44444444-4444-4444-4444-444444444444', '1980-07-24', 'American', 'Commander', 15),
('88888888-8888-8888-8888-888888888888', '55555555-5555-5555-5555-555555555555', '1975-05-15', 'Canadian', 'Pilot', 20),
('99999999-9999-9999-9999-999999999999', '66666666-6666-6666-6666-666666666666', '1990-12-01', 'British', 'Engineer', 10);

INSERT INTO Bidder (id, specialization) VALUES
('44444444-4444-4444-4444-444444444444', 'Rocket Engineering'),
('55555555-5555-5555-5555-555555555555', 'Propulsion Systems'),
('66666666-6666-6666-6666-666666666666', 'Spacecraft Design');

INSERT INTO Bid (bid_id, bidder_id, amount, bid_date, status) VALUES
('a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1', '44444444-4444-4444-4444-444444444444', 500000.00, '2023-04-01', 'Open'),
('b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2', '55555555-5555-5555-5555-555555555555', 750000.00, '2023-04-01', 'Open'),
('c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3', '66666666-6666-6666-6666-666666666666', 600000.00, '2023-04-01', 'Open');

INSERT INTO Employer (id, industry) VALUES
('44444444-4444-4444-4444-444444444444', 'Aerospace'),
('55555555-5555-5555-5555-555555555555', 'Engineering'),
('66666666-6666-6666-6666-666666666666', 'Technology');

INSERT INTO Mission (mission_id, employer_id, title, description, objectives, launch_date, duration, num_of_astronauts, payload_volume, payload_weight) VALUES
('d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4', '44444444-4444-4444-4444-444444444444', 'Mars Colony', 'Establish a self-sustaining colony on Mars.', 'Colonization', '2025-12-25', 540, 6, 5000, 20000),
('e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5', '55555555-5555-5555-5555-555555555555', 'Lunar Research', 'Conduct advanced research on the moon.', 'Research', '2024-07-20', 90, 4, 2000, 10000),
('f6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6', '66666666-6666-6666-6666-666666666666', 'Asteroid Mining', 'Mine valuable resources from NEA.', 'Mining', '2024-11-05', 120, 5, 3000, 15000);

INSERT INTO Transaction (transaction_id, bidder_id, employer_id, date, amount, status) VALUES
('g7g7g7g7-g7g7-g7g7-g7g7-g7g7g7g7g7g7', '44444444-4444-4444-4444-444444444444', '55555555-5555-5555-5555-555555555555', '2023-05-01', 200000.00, 'FINISHED'),
('h8h8h8h8-h8h8-h8h8-h8h8-h8h8h8h8h8h8', '55555555-5555-5555-5555-555555555555', '66666666-6666-6666-6666-666666666666', '2023-06-01', 300000.00, 'FINISHED'),
('i9i9i9i9-i9i9-i9i9-i9i9-i9i9i9i9i9i9', '66666666-6666-6666-6666-666666666666', '44444444-4444-4444-4444-444444444444', '2023-07-01', 250000.00, 'FINISHED');

INSERT INTO SystemReport (report_id, id, title, content) VALUES
('j0j0j0j0-j0j0-j0j0-j0j0-j0j0j0j0j0j0', '11111111-1111-1111-1111-111111111111', 'Server Maintenance', 'Routine server maintenance completed without issues.'),
('k1k1k1k1-k1k1-k1k1-k1k1-k1k1k1k1k1k1', '22222222-2222-2222-2222-222222222222', 'Data Backup', 'Full data backup was performed successfully.'),
('l2l2l2l2-l2l2-l2l2-l2l2-l2l2l2l2l2l2', '33333333-3333-3333-3333-333333333333', 'Security Update', 'Latest security patches have been applied.');

INSERT INTO Training (training_id, name, code, description, duration) VALUES
('m3m3m3m3-m3m3-m3m3-m3m3-m3m3m3m3m3m3', 'Basic Space Survival', 'BSS101', 'Training for basic survival skills in space.', 30),
('n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4', 'Advanced Navigation', 'ADV202', 'Advanced navigation training for space travel.', 45),
('o5o5o5o5-o5o5-o5o5-o5o5-o5o5o5o5o5o5', 'Zero-G Operations', 'ZGO303', 'Operational training in zero gravity environments.', 60);

INSERT INTO Bid_Has_Astronaut (bid_id, id) VALUES
('a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1', '77777777-7777-7777-7777-777777777777'),
('b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2', '88888888-8888-8888-8888-888888888888'),
('c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3', '99999999-9999-9999-9999-999999999999');

INSERT INTO Mission_Accepted_Bid (mission_id, bid_id) VALUES
('d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4', 'a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1'),
('e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5', 'b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2'),
('f6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6', 'c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3');

INSERT INTO Mission_Requires_Training (mission_id, training_id) VALUES
('d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4', 'm3m3m3m3-m3m3-m3m3-m3m3-m3m3m3m3m3m3'),
('e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5', 'n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4'),
('f6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6', 'o5o5o5o5-o5o5-o5o5-o5o5-o5o5o5o5o5o5');


INSERT INTO Training_Prerequisite_Training (prereq_id, train_id) VALUES
('m3m3m3m3-m3m3-m3m3-m3m3-m3m3m3m3m3m3', 'n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4'),
('n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4', 'o5o5o5o5-o5o5-o5o5-o5o5-o5o5o5o5o5o5');


INSERT INTO Astronaut_Completes_Training (astronaut_id, training_id, status) VALUES
-- Basic Space Survival Training
('77777777-7777-7777-7777-777777777777', 'm3m3m3m3-m3m3-m3m3-m3m3-m3m3m3m3m3m3', 100),
('88888888-8888-8888-8888-888888888888', 'm3m3m3m3-m3m3-m3m3-m3m3-m3m3m3m3m3m3', 100),
('99999999-9999-9999-9999-999999999999', 'm3m3m3m3-m3m3-m3m3-m3m3-m3m3m3m3m3m3', 100),
-- Advanced Navigation (requires Basic Space Survival)
('77777777-7777-7777-7777-777777777777', 'n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4', 100),
('88888888-8888-8888-8888-888888888888', 'n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4', 100),
('99999999-9999-9999-9999-999999999999', 'n4n4n4n4-n4n4-n4n4-n4n4-n4n4n4n4n4n4', 100),
-- Zero-G Operations (requires Advanced Navigation)
('77777777-7777-7777-7777-777777777777', 'o5o5o5o5-o5o5-o5o5-o5o5-o5o5o5o5o5o5', 100),
('88888888-8888-8888-8888-888888888888', 'o5o5o5o5-o5o5-o5o5-o5o5-o5o5o5o5o5o5', 100),
('99999999-9999-9999-9999-999999999999', 'o5o5o5o5-o5o5-o5o5-o5o5-o5o5o5o5o5o5', 100);
