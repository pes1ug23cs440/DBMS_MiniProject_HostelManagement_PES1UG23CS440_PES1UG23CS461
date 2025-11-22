-- HOSTEL MANAGEMENT SYSTEM DATABASE
-- Drop existing tables if they exist
CREATE DATABASE IF NOT EXISTS hostel_management;
USE hostel_management;
DROP TABLE IF EXISTS monitors;
DROP TABLE IF EXISTS gives_laundry;
DROP TABLE IF EXISTS books_mess;
DROP TABLE IF EXISTS student_room_fees;
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS local_guardian;
DROP TABLE IF EXISTS laundry;
DROP TABLE IF EXISTS mess;
DROP TABLE IF EXISTS fees;
DROP TABLE IF EXISTS room;
DROP TABLE IF EXISTS warden;
DROP TABLE IF EXISTS student;

-- Create Student Table
CREATE TABLE student (
    s_id VARCHAR(20) PRIMARY KEY,
    f_name VARCHAR(50) NOT NULL,
    m_name VARCHAR(50),
    l_name VARCHAR(50) NOT NULL,
    p_no VARCHAR(15) NOT NULL,
    leader_id VARCHAR(20),
    FOREIGN KEY (leader_id) REFERENCES student(s_id) ON DELETE SET NULL
);

-- Create Local Guardian Table (Weak Entity)
CREATE TABLE local_guardian (
    s_id VARCHAR(20),
    name VARCHAR(100) NOT NULL,
    p_no VARCHAR(15) PRIMARY KEY,
    FOREIGN KEY (s_id) REFERENCES student(s_id) ON DELETE CASCADE
);

-- Create Room Table
CREATE TABLE room (
    r_no VARCHAR(10) PRIMARY KEY,
    no_of_people INT NOT NULL DEFAULT 0,
    max_capacity INT NOT NULL DEFAULT 4
);

-- Create Fees Table
CREATE TABLE fees (
    p_id VARCHAR(30) PRIMARY KEY,
    p_date DATE NOT NULL,
    p_method VARCHAR(20) NOT NULL CHECK (p_method IN ('Cash', 'Card', 'UPI', 'Net Banking')),
    amount DECIMAL(10,2) NOT NULL
);

-- Create Laundry Table
CREATE TABLE laundry (
    l_no VARCHAR(20) PRIMARY KEY,
    days_of_laundry INT NOT NULL,
    rate_per_day DECIMAL(10,2) DEFAULT 50.00
);

-- Create Mess Table
CREATE TABLE mess (
    m_no VARCHAR(10) PRIMARY KEY,
    m_name VARCHAR(50) NOT NULL,
    monthly_fee DECIMAL(10,2) NOT NULL
);

-- Create Warden Table
CREATE TABLE warden (
    w_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    p_no VARCHAR(15) NOT NULL
);

-- Create Ternary Relationship: Student-Room-Fees
CREATE TABLE student_room_fees (
    s_id VARCHAR(20),
    r_no VARCHAR(10),
    p_id VARCHAR(30),
    allotment_date DATE NOT NULL,
    PRIMARY KEY (s_id),
    FOREIGN KEY (s_id) REFERENCES student(s_id) ON DELETE CASCADE,
    FOREIGN KEY (r_no) REFERENCES room(r_no) ON DELETE CASCADE,
    FOREIGN KEY (p_id) REFERENCES fees(p_id) ON DELETE CASCADE
);

-- Create Student-Mess Relationship
CREATE TABLE books_mess (
    s_id VARCHAR(20),
    m_no VARCHAR(10),
    booking_date DATE NOT NULL,
    PRIMARY KEY (s_id),
    FOREIGN KEY (s_id) REFERENCES student(s_id) ON DELETE CASCADE,
    FOREIGN KEY (m_no) REFERENCES mess(m_no) ON DELETE CASCADE
);

-- Create Student-Laundry Relationship
CREATE TABLE gives_laundry (
    s_id VARCHAR(20),
    l_no VARCHAR(20),
    submission_date DATE NOT NULL,
    PRIMARY KEY (s_id, l_no, submission_date),
    FOREIGN KEY (s_id) REFERENCES student(s_id) ON DELETE CASCADE,
    FOREIGN KEY (l_no) REFERENCES laundry(l_no) ON DELETE CASCADE
);

-- Create Warden-Student Relationship (M:N)
CREATE TABLE monitors (
    w_id VARCHAR(20),
    s_id VARCHAR(20),
    assigned_date DATE NOT NULL,
    PRIMARY KEY (w_id, s_id),
    FOREIGN KEY (w_id) REFERENCES warden(w_id) ON DELETE CASCADE,
    FOREIGN KEY (s_id) REFERENCES student(s_id) ON DELETE CASCADE
);

-- Insert Sample Data

-- Insert Wardens
INSERT INTO warden VALUES 
('W001', 'Dr. Rajesh Kumar', '9876543210'),
('W002', 'Mrs. Priya Sharma', '9876543211'),
('W003', 'Mr. Arun Patel', '9876543212');

-- Insert Rooms
INSERT INTO room VALUES 
('R101', 0, 4), ('R102', 0, 4), ('R103', 0, 4), ('R104', 0, 4),
('R201', 0, 2), ('R202', 0, 2), ('R203', 0, 2), ('R204', 0, 2),
('R301', 0, 3), ('R302', 0, 3), ('R303', 0, 3), ('R304', 0, 3);

-- Insert Mess
INSERT INTO mess VALUES 
('M01', 'North Mess', 4500.00),
('M02', 'South Mess', 4200.00),
('M03', 'Special Mess', 5000.00);

-- Insert Laundry
INSERT INTO laundry VALUES 
('L001', 7, 50.00),
('L002', 3, 30.00),
('L003', 5, 40.00);

-- Insert Students (with leader_id NULL initially)
INSERT INTO student VALUES 
('PES1UG23CS440', 'PRANEET', 'VASUDEV', 'MAHENDRAKAR', '9123456780', NULL),
('PES1UG23CS461', 'RAGHAVENDRA', NULL, 'N', '9123456781', NULL),
('PES1UG23CS100', 'Amit', 'Kumar', 'Sharma', '9123456782', NULL),
('PES1UG23CS101', 'Sneha', 'Devi', 'Singh', '9123456783', 'PES1UG23CS440'),
('PES1UG23CS102', 'Rahul', NULL, 'Verma', '9123456784', 'PES1UG23CS440'),
('PES1UG23CS103', 'Priya', 'Kumari', 'Reddy', '9123456785', 'PES1UG23CS461');

-- Insert Local Guardians
INSERT INTO local_guardian VALUES 
('PES1UG23CS440', 'Mr. Vasudev Mahendrakar', '9988776655'),
('PES1UG23CS461', 'Mr. Nagaraj', '9988776656'),
('PES1UG23CS100', 'Mr. Rajesh Sharma', '9988776657'),
('PES1UG23CS101', 'Mrs. Sunita Singh', '9988776658'),
('PES1UG23CS102', 'Mr. Vijay Verma', '9988776659'),
('PES1UG23CS103', 'Mrs. Lakshmi Reddy', '9988776660');

-- Insert Fees
INSERT INTO fees VALUES 
('F001', '2025-01-15', 'UPI', 75000.00),
('F002', '2025-01-16', 'Net Banking', 75000.00),
('F003', '2025-01-17', 'Card', 80000.00),
('F004', '2025-01-18', 'UPI', 75000.00),
('F005', '2025-01-19', 'Cash', 75000.00),
('F006', '2025-01-20', 'UPI', 80000.00);

-- Insert Student-Room-Fees relationships
INSERT INTO student_room_fees VALUES 
('PES1UG23CS440', 'R101', 'F001', '2025-01-15'),
('PES1UG23CS461', 'R101', 'F002', '2025-01-16'),
('PES1UG23CS100', 'R102', 'F003', '2025-01-17'),
('PES1UG23CS101', 'R201', 'F004', '2025-01-18'),
('PES1UG23CS102', 'R201', 'F005', '2025-01-19'),
('PES1UG23CS103', 'R301', 'F006', '2025-01-20');

-- Update room occupancy
UPDATE room SET no_of_people = 2 WHERE r_no = 'R101';
UPDATE room SET no_of_people = 1 WHERE r_no = 'R102';
UPDATE room SET no_of_people = 2 WHERE r_no = 'R201';
UPDATE room SET no_of_people = 1 WHERE r_no = 'R301';

-- Insert Mess Bookings
INSERT INTO books_mess VALUES 
('PES1UG23CS440', 'M01', '2025-01-15'),
('PES1UG23CS461', 'M01', '2025-01-16'),
('PES1UG23CS100', 'M02', '2025-01-17'),
('PES1UG23CS101', 'M03', '2025-01-18'),
('PES1UG23CS102', 'M02', '2025-01-19'),
('PES1UG23CS103', 'M01', '2025-01-20');

-- Insert Laundry Records
INSERT INTO gives_laundry VALUES 
('PES1UG23CS440', 'L001', '2025-01-20'),
('PES1UG23CS461', 'L002', '2025-01-21'),
('PES1UG23CS100', 'L001', '2025-01-22'),
('PES1UG23CS101', 'L003', '2025-01-23');

-- Insert Monitor Relationships
INSERT INTO monitors VALUES 
('W001', 'PES1UG23CS440', '2025-01-01'),
('W001', 'PES1UG23CS461', '2025-01-01'),
('W001', 'PES1UG23CS100', '2025-01-01'),
('W002', 'PES1UG23CS101', '2025-01-01'),
('W002', 'PES1UG23CS102', '2025-01-01'),
('W003', 'PES1UG23CS103', '2025-01-01');

-- Useful Queries

-- 1. View all students with their room details
CREATE VIEW student_room_view AS
SELECT 
    s.s_id,
    CONCAT(s.f_name, ' ', IFNULL(s.m_name, ''), ' ', s.l_name) AS full_name,
    s.p_no,
    srf.r_no,
    r.no_of_people,
    f.amount AS fees_paid,
    f.p_method,
    f.p_date
FROM student s
LEFT JOIN student_room_fees srf ON s.s_id = srf.s_id
LEFT JOIN room r ON srf.r_no = r.r_no
LEFT JOIN fees f ON srf.p_id = f.p_id;

-- 2. View students with their mess bookings
CREATE VIEW student_mess_view AS
SELECT 
    s.s_id,
    CONCAT(s.f_name, ' ', IFNULL(s.m_name, ''), ' ', s.l_name) AS full_name,
    m.m_no,
    m.m_name,
    m.monthly_fee,
    bm.booking_date
FROM student s
LEFT JOIN books_mess bm ON s.s_id = bm.s_id
LEFT JOIN mess m ON bm.m_no = m.m_no;

-- 3. View warden monitoring assignments
CREATE VIEW warden_student_view AS
SELECT 
    w.w_id,
    w.name AS warden_name,
    w.p_no AS warden_phone,
    s.s_id,
    CONCAT(s.f_name, ' ', IFNULL(s.m_name, ''), ' ', s.l_name) AS student_name,
    mon.assigned_date
FROM warden w
JOIN monitors mon ON w.w_id = mon.w_id
JOIN student s ON mon.s_id = s.s_id;

-- Select from views
SELECT * FROM student_room_view;
SELECT * FROM student_mess_view;
SELECT * FROM warden_student_view;

-- ====================================================================
-- Functions and Triggers for hostel_management
-- ====================================================================

DELIMITER $$

/* Function: room_available_slots
   Returns number of free slots for a room (>= 0). */
CREATE FUNCTION room_available_slots(r VARCHAR(10))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE cap INT DEFAULT 0;
    DECLARE occ INT DEFAULT 0;
    SELECT IFNULL(max_capacity,0) INTO cap FROM room WHERE r_no = r LIMIT 1;
    SELECT IFNULL(no_of_people,0) INTO occ FROM room WHERE r_no = r LIMIT 1;
    RETURN GREATEST(cap - occ, 0);
END$$

/* Function: student_total_paid
   Returns total amount paid by a student (sums fees linked by student_room_fees). */
CREATE FUNCTION student_total_paid(sid VARCHAR(30))
RETURNS DECIMAL(20,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(20,2) DEFAULT 0;
    SELECT IFNULL(SUM(f.amount),0) INTO total
    FROM student_room_fees srf
    JOIN fees f ON srf.p_id = f.p_id
    WHERE srf.s_id = sid;
    RETURN total;
END$$

/* Trigger: ensure fees amount positive and default p_date to CURDATE() if NULL */
CREATE TRIGGER trg_fees_before_insert
BEFORE INSERT ON fees
FOR EACH ROW
BEGIN
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Fee amount must be positive';
    END IF;
    IF NEW.p_date IS NULL THEN
        SET NEW.p_date = CURDATE();
    END IF;
END$$

/* Trigger: prevent insertion of a second student_room_fees row for same student */
CREATE TRIGGER trg_alloc_before_insert
BEFORE INSERT ON student_room_fees
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM student_room_fees WHERE s_id = NEW.s_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student already allocated to a room';
    END IF;
END$$

/* Trigger: after successful allocation, increment room occupancy and enforce capacity */
CREATE TRIGGER trg_alloc_after_insert
AFTER INSERT ON student_room_fees
FOR EACH ROW
BEGIN
    UPDATE room
    SET no_of_people = no_of_people + 1
    WHERE r_no = NEW.r_no;

    -- If capacity exceeded now, rollback via SIGNAL
    IF (SELECT no_of_people FROM room WHERE r_no = NEW.r_no) >
       (SELECT max_capacity FROM room WHERE r_no = NEW.r_no) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Room capacity exceeded';
    END IF;
END$$

/* Trigger: when deallocating (DELETE from student_room_fees), decrement occupancy safely */
CREATE TRIGGER trg_alloc_after_delete
AFTER DELETE ON student_room_fees
FOR EACH ROW
BEGIN
    UPDATE room
    SET no_of_people = GREATEST(no_of_people - 1, 0)
    WHERE r_no = OLD.r_no;
END$$

/* Optional safety: when a fee is deleted, do not allow deletion if referenced (CASCADE already set).
   If you want, you could also log deletions or prevent deletion — omitted here. */

DELIMITER ;
USE hostel_management;
