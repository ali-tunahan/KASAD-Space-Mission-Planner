USE DASAK;

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

CREATE TABLE IF NOT EXISTS Bidder (
    id CHAR(36) PRIMARY KEY,
    specialization VARCHAR(255),
    FOREIGN KEY (id) REFERENCES User(id)
);

CREATE TABLE IF NOT EXISTS Bid (
    bid_id CHAR(36) PRIMARY KEY,
    bidder_id CHAR(36),
    amount DECIMAL(19, 4),
    bid_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (bidder_id) REFERENCES Bidder(id)
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

CREATE TABLE IF NOT EXISTS Employer (
    id CHAR(36) PRIMARY KEY,
    industry VARCHAR(100),
    FOREIGN KEY (id) REFERENCES User(id)
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
    