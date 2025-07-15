CREATE DATABASE IF NOT EXISTS selenium;

USE selenium;

CREATE TABLE IF NOT EXISTS fixed_deposits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Principal INT(100) NOT NULL,
    RateOfInterest DECIMAL(5, 2) NOT NULL,
    Period INT NOT NULL,
    PeriodUnit VARCHAR(20) NOT NULL,
    Frequency VARCHAR(50) NOT NULL,
    MaturityValue DECIMAL(12, 2) NOT NULL,
    Expected VARCHAR(10) NOT NULL,
    Result VARCHAR(10) NOT NULL
);

INSERT INTO fixed_deposits (Principal, RateOfInterest, Period, PeriodUnit, Frequency, MaturityValue, Expected, Result)
VALUES
(20000, 10.00, 2, 'year(s)', 'Simple Interest', 24000.00, 'pass', ''),
(40000, 15.00, 5, 'year(s)', 'Simple Interest', 70000.00, 'pass', ''),
(50000, 10.00, 3, 'month(s)', 'Simple Interest', 51250.00, 'pass', ''),
(75000, 12.00, 2, 'month(s)', 'Simple Interest', 76500.00, 'pass', ''),
(75000, 12.00, 2, 'day(s)', 'Simple Interest', 75045.32, 'fail', '');
