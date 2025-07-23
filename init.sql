CREATE DATABASE IF NOT EXISTS test_data;

USE test_data;

CREATE TABLE IF NOT EXISTS fixed_deposits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fd_amount_rs INT NOT NULL,
    fd_period_value INT NOT NULL,
    fd_period_unit VARCHAR(10), 
    interest_rate DECIMAL(5, 2) NOT NULL, 
    compounding_frequency VARCHAR(20) NOT NULL, 
    maturity_amount_lakh DECIMAL(10, 1) NOT NULL, 
    expected_result VARCHAR(10) NOT NULL, 
    actual_result VARCHAR(10) 
);

INSERT INTO fixed_deposits (
    fd_amount_rs,
    fd_period_value,
    fd_period_unit,
    interest_rate,
    compounding_frequency,
    maturity_amount_lakh,
    expected_result,
    actual_result
) VALUES
(20000, 2, 'years', 10.00, 'Monthly', 0.2, 'pass', NULL),
(40000, 5, 'years', 15.00, 'Quarterly', 0.8, 'pass', NULL),
(50000, 3, 'months', 10.00, 'Half Yearly', 0.6, 'pass', NULL),
(75000, 2, 'months', 12.00, 'Yearly', 0.9, 'pass', NULL),
(85000, 2, 'days', 12.00, 'Yearly', 2.1, 'fail', NULL);
