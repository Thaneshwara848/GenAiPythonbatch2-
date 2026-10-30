CREATE DATABASE IF NOT EXISTS employee_management
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE employee_management;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    department VARCHAR(80) NOT NULL,
    designation VARCHAR(80) NOT NULL,
    salary DECIMAL(12,2) NOT NULL,
    status ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
