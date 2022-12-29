-- Create a database for storing tick data
CREATE DATABASE tick_data;

-- Use the tick_data database
USE tick_data;

-- Create a table for storing tick data
CREATE TABLE ticks (
  id INTEGER PRIMARY KEY AUTO_INCREMENT, 
  date DATETIME NOT NULL,
  price FLOAT NOT NULL,
  volume INTEGER NOT NULL,
  label FLOAT NOT NULL
);

-- Create an index on the date column to improve querying performance
CREATE INDEX idx_date ON ticks (date);

-- Insert data into the ticks table
INSERT INTO ticks (date, price, volume, label)
VALUES 
  ('2020-01-01 00:00:00', 1.2000, 1, 1.2010),
  ('2020-01-01 00:01:00', 1.2010, 1, 1.2020),
  ('2020-01-01 00:02:00', 1.2020, 1, 1.2030),
  ('2020-01-01 00:03:00', 1.2030, 1, 1.2040);
